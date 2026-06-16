"""
tuner.py — the auto-tune learning loop (runs once after the close).

This is how the bot "improves with experience" — but carefully, and never in a way
that can blow past the hard limits.

What it does each evening:
  1. Reads the last several daily summaries (state/runs/<date>-summary.json), each
     written honestly by the journal-writer from real, reconciled fills.
  2. GATES first — it refuses to tune at all if:
        * there are fewer than 5 days of history, or
        * yesterday hit the daily loss-stop, or
        * the last 3 days were net-negative (a losing streak), or
        * the account is in a drawdown deeper than 5%.
     "Don't optimize while you're bleeding."
  3. If allowed, it proposes AT MOST ONE small change to ONE parameter, chosen by
     simple evidence rules. The change is clamped to the per-day max step AND to the
     hard [min,max] in state/param_bounds.json. A parameter that was changed in the
     last 2 days is on cooldown and skipped.
  4. It applies the change to state/config.json and appends a fully reversible row
     to state/tuning_ledger.jsonl.

Nothing here can ever loosen the inviolable limits ($10k/trade, $50k/day, 8 names,
-$3,000 loss-stop, 25%/name): those are also hard-coded in constitution.py and
daytrade_guard.py, and param_bounds.json only allows safe ranges.

Usage:
    python3 code/tuner.py --run        # do tonight's (gated) tuning
    python3 code/tuner.py --status     # show the gating decision only, change nothing
    python3 code/tuner.py --show       # show current params + recent ledger
    python3 code/tuner.py --revert L-20260615-01
    python3 code/tuner.py --reset      # restore config.json from config.defaults.json
"""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone as tz
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CONFIG_FILE = ROOT / "state" / "config.json"
DEFAULTS_FILE = ROOT / "state" / "config.defaults.json"
BOUNDS_FILE = ROOT / "state" / "param_bounds.json"
LEDGER_FILE = ROOT / "state" / "tuning_ledger.jsonl"
RUNS_DIR = ROOT / "state" / "runs"
HISTORY_FILE = ROOT / "state" / "portfolio_history.jsonl"

MIN_DAYS = 5            # need at least this many daily summaries before tuning
MIN_TRADES_PER_SETUP = 20
COOLDOWN_DAYS = 2       # a parameter just changed cannot change again this soon
DRAWDOWN_FREEZE = 0.05  # freeze tuning if drawdown deeper than 5%
INT_PARAMS = {"orb_minutes", "orb_breakout_buffer_bp", "vwap_reclaim_buffer_bp",
              "risk_per_trade_usd", "per_trade_max_usd", "daily_deploy_cap_usd",
              "max_open_positions", "max_spread_bp", "min_quote_freshness_sec"}


# ---------- io helpers ----------

def _load(path: Path, default):
    if path.exists():
        try:
            return json.loads(path.read_text())
        except Exception:
            return default
    return default


def load_config() -> dict:
    return _load(CONFIG_FILE, {})


def load_bounds() -> dict:
    return _load(BOUNDS_FILE, {})


def load_ledger() -> list[dict]:
    if not LEDGER_FILE.exists():
        return []
    rows = []
    for line in LEDGER_FILE.read_text().splitlines():
        try:
            rows.append(json.loads(line))
        except Exception:
            continue
    return rows


def load_summaries() -> list[dict]:
    """Daily summaries written by the journal-writer, sorted by date ascending."""
    out = []
    if RUNS_DIR.exists():
        for f in RUNS_DIR.glob("*-summary.json"):
            d = _load(f, None)
            if d and d.get("date"):
                out.append(d)
    out.sort(key=lambda d: d["date"])
    return out


def current_drawdown() -> float:
    if not HISTORY_FILE.exists():
        return 0.0
    eqs = []
    for line in HISTORY_FILE.read_text().splitlines():
        try:
            eqs.append(float(json.loads(line)["equity"]))
        except Exception:
            continue
    if len(eqs) < 2:
        return 0.0
    hwm = max(eqs)
    return max(0.0, (hwm - eqs[-1]) / hwm) if hwm > 0 else 0.0


# ---------- aggregation ----------

def aggregate(summaries: list[dict]) -> dict:
    days = len(summaries)
    total_trades = sum(int(s.get("num_trades", 0)) for s in summaries)

    def tw(metric):  # trade-weighted mean of a per-day rate
        num = sum(float(s.get(metric, 0)) * int(s.get("num_trades", 0)) for s in summaries)
        return (num / total_trades) if total_trades else 0.0

    fills = [float(s.get("fill_rate")) for s in summaries if s.get("fill_rate") is not None]
    per_setup: dict[str, dict] = {}
    for s in summaries:
        for name, st in (s.get("per_setup") or {}).items():
            agg = per_setup.setdefault(name, {"trades": 0, "wins": 0, "exp_sum": 0.0})
            t = int(st.get("trades", 0))
            agg["trades"] += t
            agg["wins"] += int(st.get("wins", 0))
            agg["exp_sum"] += float(st.get("expectancy_r", 0)) * t
    for name, agg in per_setup.items():
        agg["expectancy_r"] = (agg["exp_sum"] / agg["trades"]) if agg["trades"] else 0.0

    return {
        "days": days,
        "total_trades": total_trades,
        "avg_trades_per_day": (total_trades / days) if days else 0.0,
        "win_rate": tw("win_rate"),
        "avg_win_r": tw("avg_win_r"),
        "avg_loss_r": tw("avg_loss_r"),
        "avg_fill_rate": (sum(fills) / len(fills)) if fills else None,
        "per_setup": per_setup,
    }


# ---------- gating ----------

def gating(summaries: list[dict]) -> tuple[bool, str]:
    """Returns (frozen, reason). frozen=True means: do not tune tonight."""
    if len(summaries) < MIN_DAYS:
        return True, f"only {len(summaries)} day(s) of history (need {MIN_DAYS})"
    if summaries[-1].get("hit_loss_stop"):
        return True, "yesterday hit the daily loss-stop — not optimizing after a stop day"
    last3 = summaries[-3:]
    if sum(float(s.get("realized_pnl", 0)) for s in last3) < 0:
        return True, "last 3 days are net-negative — not optimizing during a losing streak"
    dd = current_drawdown()
    if dd > DRAWDOWN_FREEZE:
        return True, f"drawdown {dd:.1%} deeper than {DRAWDOWN_FREEZE:.0%} — freezing tuning"
    return False, "ok to tune"


# ---------- proposal ----------

def _days_since_last_change(ledger: list[dict], param: str, today: str) -> int | None:
    dates = [r.get("date") for r in ledger if r.get("param") == param and r.get("date")]
    if not dates:
        return None
    last = max(dates)
    try:
        return (datetime.fromisoformat(today).date() - datetime.fromisoformat(last).date()).days
    except Exception:
        return None


def _clamp_numeric(param: str, current, proposed, bounds: dict):
    b = bounds.get(param)
    if not b:
        return None
    step = float(b["max_step_per_day"])
    lo, hi = float(b["min"]), float(b["max"])
    delta = max(-step, min(step, proposed - current))      # cap the step size
    value = max(lo, min(hi, current + delta))               # cap to hard bounds
    if param in INT_PARAMS:
        value = int(round(value))
    else:
        value = round(value, 5)
    return value


def propose(summaries: list[dict], config: dict, bounds: dict, ledger: list[dict], today: str):
    """Return a single change dict or None. Tries rules in priority order and
    skips any parameter currently on cooldown."""
    agg = aggregate(summaries)

    def on_cooldown(param):
        d = _days_since_last_change(ledger, param, today)
        return d is not None and d < COOLDOWN_DAYS

    # Rule 1 — disable a setup that is clearly losing money over a big sample.
    for name, st in agg["per_setup"].items():
        if (st["trades"] >= MIN_TRADES_PER_SETUP and st["expectancy_r"] <= -0.15
                and config.get("setup_enabled", {}).get(name, False)):
            param = f"setup_enabled.{name}"
            if not on_cooldown(param):
                return {"param": param, "from": True, "to": False,
                        "reason": f"setup '{name}' expectancy {st['expectancy_r']:+.2f}R over {st['trades']} trades — disabling",
                        "evidence": {"setup": name, **st}}

    # Rule 2 — too many of our limit orders never fill: be a touch more marketable.
    if agg["avg_fill_rate"] is not None and agg["avg_fill_rate"] < 0.70:
        param = "limit_buy_above_ask_pct"
        cur = float(config.get(param, 0.001))
        new = _clamp_numeric(param, cur, cur + bounds[param]["max_step_per_day"], bounds)
        if new is not None and new != cur and not on_cooldown(param):
            return {"param": param, "from": cur, "to": new,
                    "reason": f"fill rate {agg['avg_fill_rate']:.0%} < 70% — pricing entries slightly more marketable",
                    "evidence": {"avg_fill_rate": agg["avg_fill_rate"]}}

    # Rule 3 — low win rate with full-size losses: stops may be too tight, widen them.
    if agg["total_trades"] >= MIN_TRADES_PER_SETUP and agg["win_rate"] < 0.40 and agg["avg_loss_r"] <= -0.90:
        param = "stop_atr_mult"
        cur = float(config.get(param, 1.5))
        new = _clamp_numeric(param, cur, cur + bounds[param]["max_step_per_day"], bounds)
        if new is not None and new != cur and not on_cooldown(param):
            return {"param": param, "from": cur, "to": new,
                    "reason": f"win rate {agg['win_rate']:.0%} with avg loss {agg['avg_loss_r']:.2f}R — widening stops",
                    "evidence": {"win_rate": agg["win_rate"], "avg_loss_r": agg["avg_loss_r"]}}

    # Rule 4 — winning often but small: let targets come in sooner to bank gains.
    if agg["total_trades"] >= MIN_TRADES_PER_SETUP and agg["win_rate"] >= 0.55 and 0 < agg["avg_win_r"] < 1.2:
        param = "target_atr_mult"
        cur = float(config.get(param, 2.5))
        new = _clamp_numeric(param, cur, cur - bounds[param]["max_step_per_day"], bounds)
        if new is not None and new != cur and not on_cooldown(param):
            return {"param": param, "from": cur, "to": new,
                    "reason": f"win rate {agg['win_rate']:.0%} but avg win only {agg['avg_win_r']:.2f}R — taking profit sooner",
                    "evidence": {"win_rate": agg["win_rate"], "avg_win_r": agg["avg_win_r"]}}

    # Rule 5 — too few trades while winning: qualify more names (lower the rel-vol bar).
    if agg["avg_trades_per_day"] < 2 and agg["win_rate"] >= 0.50:
        param = "min_rel_volume"
        cur = float(config.get(param, 1.2))
        new = _clamp_numeric(param, cur, cur - bounds[param]["max_step_per_day"], bounds)
        if new is not None and new != cur and not on_cooldown(param):
            return {"param": param, "from": cur, "to": new,
                    "reason": f"only {agg['avg_trades_per_day']:.1f} trades/day while winning — loosening rel-volume filter",
                    "evidence": {"avg_trades_per_day": agg["avg_trades_per_day"], "win_rate": agg["win_rate"]}}

    # Rule 6 — overtrading and losing: be pickier (raise the rel-vol bar).
    if agg["avg_trades_per_day"] > 8 and agg["win_rate"] < 0.45:
        param = "min_rel_volume"
        cur = float(config.get(param, 1.2))
        new = _clamp_numeric(param, cur, cur + bounds[param]["max_step_per_day"], bounds)
        if new is not None and new != cur and not on_cooldown(param):
            return {"param": param, "from": cur, "to": new,
                    "reason": f"{agg['avg_trades_per_day']:.1f} trades/day at {agg['win_rate']:.0%} win — tightening rel-volume filter",
                    "evidence": {"avg_trades_per_day": agg["avg_trades_per_day"], "win_rate": agg["win_rate"]}}

    return None


# ---------- apply / revert ----------

def _set_param(config: dict, param: str, value) -> None:
    if param.startswith("setup_enabled."):
        config.setdefault("setup_enabled", {})[param.split(".", 1)[1]] = value
    else:
        config[param] = value


def _get_param(config: dict, param: str):
    if param.startswith("setup_enabled."):
        return config.get("setup_enabled", {}).get(param.split(".", 1)[1])
    return config.get(param)


def _next_ledger_id(ledger: list[dict], today: str) -> str:
    ymd = today.replace("-", "")
    n = sum(1 for r in ledger if str(r.get("id", "")).startswith(f"L-{ymd}")) + 1
    return f"L-{ymd}-{n:02d}"


def apply_change(change: dict, today: str) -> dict:
    config = load_config()
    ledger = load_ledger()
    _set_param(config, change["param"], change["to"])
    CONFIG_FILE.write_text(json.dumps(config, indent=2) + "\n")

    row = {
        "id": _next_ledger_id(ledger, today),
        "date": today,
        "ts_utc": datetime.now(tz.utc).isoformat(),
        "param": change["param"],
        "from": change["from"],
        "to": change["to"],
        "reason": change["reason"],
        "evidence": change.get("evidence", {}),
        "revert": {"param": change["param"], "to": change["from"]},
    }
    with LEDGER_FILE.open("a") as f:
        f.write(json.dumps(row) + "\n")
    return row


def revert(ledger_id: str) -> dict:
    ledger = load_ledger()
    target = next((r for r in ledger if r.get("id") == ledger_id), None)
    if not target:
        return {"error": f"ledger id not found: {ledger_id}"}
    config = load_config()
    _set_param(config, target["revert"]["param"], target["revert"]["to"])
    CONFIG_FILE.write_text(json.dumps(config, indent=2) + "\n")
    row = {
        "id": _next_ledger_id(ledger, datetime.now(tz.utc).date().isoformat()),
        "date": datetime.now(tz.utc).date().isoformat(),
        "ts_utc": datetime.now(tz.utc).isoformat(),
        "param": target["revert"]["param"],
        "from": _get_param(load_config(), target["revert"]["param"]),
        "to": target["revert"]["to"],
        "reason": f"manual revert of {ledger_id}",
        "evidence": {"reverts": ledger_id},
        "revert": {"param": target["param"], "to": target["to"]},
    }
    with LEDGER_FILE.open("a") as f:
        f.write(json.dumps(row) + "\n")
    return {"reverted": ledger_id, "now": target["revert"]}


def reset() -> dict:
    defaults = _load(DEFAULTS_FILE, None)
    if defaults is None:
        return {"error": "config.defaults.json missing"}
    CONFIG_FILE.write_text(json.dumps(defaults, indent=2) + "\n")
    return {"reset": True, "note": "config.json restored from config.defaults.json"}


def run(today: str) -> dict:
    summaries = load_summaries()
    frozen, reason = gating(summaries)
    if frozen:
        return {"tuned": False, "reason": reason, "days_of_history": len(summaries)}
    change = propose(summaries, load_config(), load_bounds(), load_ledger(), today)
    if not change:
        return {"tuned": False, "reason": "no rule fired — parameters left unchanged",
                "days_of_history": len(summaries)}
    row = apply_change(change, today)
    return {"tuned": True, "change": row}


def main() -> int:
    from clockutil import et_today_str
    p = argparse.ArgumentParser()
    p.add_argument("--run", action="store_true")
    p.add_argument("--status", action="store_true")
    p.add_argument("--show", action="store_true")
    p.add_argument("--revert", metavar="LEDGER_ID")
    p.add_argument("--reset", action="store_true")
    p.add_argument("--date", default=None)
    args = p.parse_args()
    today = args.date or et_today_str()

    if args.reset:
        print(json.dumps(reset(), indent=2)); return 0
    if args.revert:
        print(json.dumps(revert(args.revert), indent=2)); return 0
    if args.show:
        print(json.dumps({"config": load_config(),
                          "recent_ledger": load_ledger()[-10:]}, indent=2)); return 0
    if args.status:
        summaries = load_summaries()
        frozen, reason = gating(summaries)
        print(json.dumps({"frozen": frozen, "reason": reason,
                          "days_of_history": len(summaries),
                          "drawdown": round(current_drawdown(), 4),
                          "aggregate": aggregate(summaries) if summaries else {}}, indent=2)); return 0
    # default action is --run
    print(json.dumps(run(today), indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
