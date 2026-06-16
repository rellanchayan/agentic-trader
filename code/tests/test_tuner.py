"""Tests for tuner.py — clamping, gating, aggregation, and proposal logic.
These do NOT write config or the ledger (those touch real state); they exercise
the pure decision functions with synthetic inputs and the real bounds file."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import tuner

PASS = 0
FAIL = 0


def check(name, cond):
    global PASS, FAIL
    if cond:
        PASS += 1
    else:
        FAIL += 1
        print(f"  FAIL: {name}")


def summary(date, pnl, n, wr, setup="orb", trades=4, wins=2, exp=0.2, loss_stop=False,
            avg_win_r=1.5, avg_loss_r=-1.0, fill_rate=0.9):
    return {"date": date, "realized_pnl": pnl, "num_trades": n, "win_rate": wr,
            "avg_win_r": avg_win_r, "avg_loss_r": avg_loss_r, "fill_rate": fill_rate,
            "hit_loss_stop": loss_stop,
            "per_setup": {setup: {"trades": trades, "wins": wins, "expectancy_r": exp}}}


def run():
    bounds = tuner.load_bounds()

    # ---- clamping ----
    check("clamp steps by max_step", tuner._clamp_numeric("stop_atr_mult", 1.5, 3.5, bounds) == 1.7)
    check("clamp to hard max", tuner._clamp_numeric("stop_atr_mult", 2.95, 3.5, bounds) == 3.0)
    check("clamp int param to max", tuner._clamp_numeric("max_open_positions", 8, 9, bounds) == 8)
    check("clamp int stays int", isinstance(tuner._clamp_numeric("max_open_positions", 5, 6, bounds), int))

    # ---- aggregation ----
    summaries = [summary("2026-06-01", 100, 10, 0.5), summary("2026-06-02", 100, 30, 0.6)]
    agg = tuner.aggregate(summaries)
    check("avg_trades_per_day", agg["avg_trades_per_day"] == 20.0)
    check("trade-weighted win_rate", abs(agg["win_rate"] - 0.575) < 1e-6)

    # ---- gating ----
    few = [summary(f"2026-06-0{i}", 50, 5, 0.5) for i in range(1, 4)]
    check("gate: too few days", tuner.gating(few)[0] is True)

    five_pos = [summary(f"2026-06-0{i}", 50, 5, 0.5) for i in range(1, 6)]
    check("gate: 5 positive days ok", tuner.gating(five_pos)[0] is False)

    five_stop = list(five_pos)
    five_stop[-1] = summary("2026-06-05", 50, 5, 0.5, loss_stop=True)
    check("gate: loss-stop day freezes", tuner.gating(five_stop)[0] is True)

    five_losing = [summary(f"2026-06-0{i}", -50, 5, 0.5) for i in range(1, 6)]
    check("gate: losing streak freezes", tuner.gating(five_losing)[0] is True)

    # ---- proposal: disable a clearly-losing setup ----
    losing_setup = [summary(f"2026-06-0{i}", 50, 6, 0.4, setup="orb", trades=6, wins=2, exp=-0.2)
                    for i in range(1, 7)]
    config = {"setup_enabled": {"orb": True}, "limit_buy_above_ask_pct": 0.001,
              "stop_atr_mult": 1.5, "target_atr_mult": 2.5, "min_rel_volume": 1.2}
    change = tuner.propose(losing_setup, config, bounds, [], "2026-06-07")
    check("propose disables losing setup", change is not None and change["param"] == "setup_enabled.orb" and change["to"] is False)

    # ---- proposal: nothing fires on healthy numbers ----
    healthy = [summary(f"2026-06-0{i}", 80, 5, 0.55, setup="orb", trades=5, wins=3, exp=0.4,
                       avg_win_r=1.5, avg_loss_r=-1.0, fill_rate=0.95) for i in range(1, 7)]
    healthy_config = {"setup_enabled": {"orb": True}, "limit_buy_above_ask_pct": 0.001,
                      "stop_atr_mult": 1.5, "target_atr_mult": 2.5, "min_rel_volume": 1.2}
    check("propose leaves healthy alone", tuner.propose(healthy, healthy_config, bounds, [], "2026-06-07") is None)

    print(f"test_tuner: {PASS} passed, {FAIL} failed")
    return 0 if FAIL == 0 else 1


if __name__ == "__main__":
    raise SystemExit(run())
