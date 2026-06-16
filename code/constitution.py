"""
constitution.py — programmatic guardrails checked on EVERY order before it is sent.

This is the day-trader edition. It is the universal per-order gate: alpaca_client.py
calls run_all_checks() inside submit(), so no order can reach Alpaca without passing
all of these. Same-day round trips ARE allowed here (this is a day trader) — but every
hard money limit still applies.

The contextual, day-STATE checks (is the loss-stop tripped? are we past the
no-new-entries cutoff? is PDT a risk? is the quote stale?) live in
code/daytrade_guard.py and code/preflight.py. Both gates run; this one is the
backstop that can never be skipped.

Run as a script:
    python3 code/constitution.py --check state/pending_trades/<trade_id>.json

Exit code 0 = PASS, non-zero = FAIL. Stdout is human-readable; stderr captures violations.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

try:
    from dotenv import load_dotenv
except ImportError:  # keep importable for tests without python-dotenv
    def load_dotenv(*_a, **_k):
        return False

ROOT = Path(__file__).resolve().parent.parent
HALT_FILE = ROOT / ".HALT_TRADING"
PORTFOLIO_FILE = ROOT / "state" / "portfolio.json"
COMPLETED_DIR = ROOT / "state" / "completed_trades"

# ------ Hard limits (mirror CLAUDE.md + the locked aggressive budget) ------
# These numbers are inviolable. They live here in code so a corrupted/edited
# state/config.json can never loosen them.

MAX_POSITION_PCT = 0.25          # max 25% of equity in any one ticker
MAX_TRADES_PER_WEEK = 50
MAX_TRADES_PER_DAY = 20
MAX_DAILY_INVEST_USD = 50000.0   # most BUY notional we deploy in one day
MAX_PER_TRADE_USD = 10000.0      # most BUY notional in any single order
MAX_OPEN_POSITIONS = 8           # most names held at once

FORBIDDEN_SUBSTRINGS_IN_SYMBOL = {
    # leveraged
    "TQQQ", "SQQQ", "UPRO", "SPXU", "SOXL", "SOXS", "TNA", "TZA", "LABU", "LABD",
    "FAS", "FAZ", "TMF", "TMV", "UVXY", "VIXY", "SVXY", "VXX",
    # inverse
    "SH", "PSQ", "DOG", "RWM", "SEF",
}


@dataclass
class CheckResult:
    name: str
    passed: bool
    note: str = ""

    def __str__(self) -> str:
        status = "PASS" if self.passed else "FAIL"
        return f"  [{status}] {self.name}{(': ' + self.note) if self.note else ''}"


class ConstitutionViolation(Exception):
    pass


def _load_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        raise ConstitutionViolation(f"required file missing: {path}")
    with path.open() as f:
        return json.load(f)


def check_halt_switch() -> CheckResult:
    if HALT_FILE.exists():
        return CheckResult("halt_switch", False, f"{HALT_FILE.name} exists")
    return CheckResult("halt_switch", True)


def check_live_mode_forbidden() -> CheckResult:
    """Hard refuse if env points anywhere but the paper host."""
    endpoint = os.environ.get("ALPACA_ENDPOINT", "")
    if "paper-api.alpaca.markets" not in endpoint:
        return CheckResult(
            "live_mode_forbidden",
            False,
            f"ALPACA_ENDPOINT must be paper-api.alpaca.markets, got: {endpoint!r}",
        )
    if os.environ.get("LIVE_TRADING_AUTHORIZED", "").lower() == "true":
        return CheckResult(
            "live_mode_forbidden",
            False,
            "LIVE_TRADING_AUTHORIZED is true; this build operates paper-only.",
        )
    return CheckResult("live_mode_forbidden", True)


def check_forbidden_instrument(trade: dict) -> CheckResult:
    ticker = trade.get("ticker", "").upper()
    if ticker in FORBIDDEN_SUBSTRINGS_IN_SYMBOL:
        return CheckResult("forbidden_instrument", False, f"{ticker} is on the denylist (leveraged/inverse/vol)")
    if any(c.isdigit() for c in ticker) and len(ticker) > 6:
        return CheckResult("forbidden_instrument", False, f"{ticker} looks like an option/contract")
    return CheckResult("forbidden_instrument", True)


def check_order_type(trade: dict) -> CheckResult:
    order_type = trade.get("order_type", "LIMIT").upper()
    tif = trade.get("time_in_force", "DAY").upper()
    if order_type != "LIMIT":
        return CheckResult("order_type", False, f"order_type must be LIMIT, got {order_type}")
    if tif != "DAY":
        return CheckResult("order_type", False, f"time_in_force must be DAY, got {tif}")
    return CheckResult("order_type", True)


def check_side(trade: dict) -> CheckResult:
    side = trade.get("side", "").upper()
    if side not in {"BUY", "SELL"}:
        return CheckResult("side", False, f"side must be BUY or SELL, got {side!r}")
    return CheckResult("side", True)


def check_position_size(trade: dict, portfolio: dict) -> CheckResult:
    """Buys: post-trade position in this name must stay within the 25% cap."""
    if trade["side"].upper() != "BUY":
        return CheckResult("position_size", True, "sell — not applicable")

    equity = float(portfolio.get("equity", 0))
    if equity <= 0:
        return CheckResult("position_size", False, "portfolio equity unknown — cannot size-check")

    ticker = trade["ticker"].upper()
    notional = float(trade["limit_price"]) * float(trade["qty"])
    current_pos_value = 0.0
    for pos in portfolio.get("positions", []):
        if pos["ticker"].upper() == ticker:
            current_pos_value = float(pos["market_value"])
            break

    post_pct = (current_pos_value + notional) / equity
    if post_pct > MAX_POSITION_PCT:
        return CheckResult("position_size", False,
                           f"position would be {post_pct:.1%} > {MAX_POSITION_PCT:.0%} cap")
    return CheckResult("position_size", True, f"position {post_pct:.1%}")


def check_per_trade_cap(trade: dict) -> CheckResult:
    """No single BUY order may deploy more than the per-trade cap."""
    if trade["side"].upper() != "BUY":
        return CheckResult("per_trade_cap", True, "sell — not applicable")
    notional = float(trade["limit_price"]) * float(trade["qty"])
    if notional > MAX_PER_TRADE_USD + 1e-6:
        return CheckResult("per_trade_cap", False,
                           f"order ${notional:,.0f} exceeds ${MAX_PER_TRADE_USD:,.0f}/trade cap")
    return CheckResult("per_trade_cap", True, f"${notional:,.0f} of ${MAX_PER_TRADE_USD:,.0f}/trade")


def check_max_open_positions(trade: dict, portfolio: dict) -> CheckResult:
    """A new name may not push us past the max concurrent holdings."""
    if trade["side"].upper() != "BUY":
        return CheckResult("max_open_positions", True, "sell — not applicable")
    ticker = trade["ticker"].upper()
    held = {p["ticker"].upper() for p in portfolio.get("positions", []) if abs(float(p.get("qty", 0))) > 0}
    if ticker in held:
        return CheckResult("max_open_positions", True, f"adding to existing {ticker}")
    if len(held) >= MAX_OPEN_POSITIONS:
        return CheckResult("max_open_positions", False,
                           f"already {len(held)} names held (max {MAX_OPEN_POSITIONS})")
    return CheckResult("max_open_positions", True, f"{len(held)}/{MAX_OPEN_POSITIONS} names held")


def check_buying_power(trade: dict, portfolio: dict) -> CheckResult:
    """Buys must be coverable by available buying power. On the margin paper
    account intraday buying power exceeds settled cash (this is what makes
    legal intraday recycling possible), but the $50k/day deploy cap keeps total
    deployment well under equity, so we are never actually levered."""
    if trade["side"].upper() != "BUY":
        return CheckResult("buying_power", True, "sell — not applicable")
    available = float(portfolio.get("buying_power", portfolio.get("cash", 0)) or 0)
    notional = float(trade["limit_price"]) * float(trade["qty"])
    if notional > available + 1e-6:
        return CheckResult("buying_power", False,
                           f"trade needs ${notional:,.2f}, buying power is ${available:,.2f}")
    return CheckResult("buying_power", True, f"needs ${notional:,.2f}, have ${available:,.2f}")


def _trades_in_window(days: int) -> int:
    cutoff = datetime.now(timezone.utc) - timedelta(days=days)
    if not COMPLETED_DIR.exists():
        return 0
    count = 0
    for f in COMPLETED_DIR.glob("*.json"):
        try:
            d = json.loads(f.read_text())
            submitted = d.get("submitted_at_utc")
            if submitted and datetime.fromisoformat(submitted.replace("Z", "+00:00")) >= cutoff:
                count += 1
        except Exception:
            continue
    return count


def check_frequency(trade: dict) -> CheckResult:
    day_count = _trades_in_window(1)
    week_count = _trades_in_window(7)
    if day_count >= MAX_TRADES_PER_DAY:
        return CheckResult("frequency", False, f"already {day_count} trades today (max {MAX_TRADES_PER_DAY})")
    if week_count >= MAX_TRADES_PER_WEEK:
        return CheckResult("frequency", False, f"already {week_count} trades this week (max {MAX_TRADES_PER_WEEK})")
    return CheckResult("frequency", True, f"day {day_count}/{MAX_TRADES_PER_DAY}, week {week_count}/{MAX_TRADES_PER_WEEK}")


def check_trade_reason(trade: dict) -> CheckResult:
    reason = trade.get("reason") or trade.get("thesis")
    if not reason or len(str(reason).strip()) < 10:
        return CheckResult("trade_reason", False, "missing short reason/thesis")
    return CheckResult("trade_reason", True)


def _todays_completed() -> list[dict]:
    today = datetime.now(timezone.utc).date().isoformat()
    out: list[dict] = []
    if not COMPLETED_DIR.exists():
        return out
    for f in COMPLETED_DIR.glob("*.json"):
        try:
            d = json.loads(f.read_text())
            if str(d.get("submitted_at_utc", ""))[:10] == today:
                out.append(d)
        except Exception:
            continue
    return out


def check_daily_invest_cap(trade: dict) -> CheckResult:
    """Total BUY notional submitted today + this order must stay under the cap.
    Sells are exempt — reducing risk is never throttled."""
    if trade["side"].upper() != "BUY":
        return CheckResult("daily_invest_cap", True, "sell — not applicable")
    notional = float(trade["limit_price"]) * float(trade["qty"])
    prior = sum(
        float(d.get("limit_price", 0)) * float(d.get("qty", 0))
        for d in _todays_completed() if str(d.get("side", "")).upper() == "BUY"
    )
    if prior + notional > MAX_DAILY_INVEST_USD + 1e-6:
        return CheckResult("daily_invest_cap", False,
                           f"today's buys ${prior:,.0f} + ${notional:,.0f} would exceed ${MAX_DAILY_INVEST_USD:,.0f}/day cap")
    return CheckResult("daily_invest_cap", True, f"${prior + notional:,.0f} of ${MAX_DAILY_INVEST_USD:,.0f}/day")


def run_all_checks(trade_path: Path) -> tuple[bool, list[CheckResult]]:
    trade = _load_json(trade_path)
    portfolio = _load_json(PORTFOLIO_FILE) if PORTFOLIO_FILE.exists() else {"equity": 0, "cash": 0, "buying_power": 0, "positions": []}

    results: list[CheckResult] = [
        check_halt_switch(),
        check_live_mode_forbidden(),
        check_forbidden_instrument(trade),
        check_side(trade),
        check_order_type(trade),
        check_position_size(trade, portfolio),
        check_per_trade_cap(trade),
        check_max_open_positions(trade, portfolio),
        check_buying_power(trade, portfolio),
        check_frequency(trade),
        check_daily_invest_cap(trade),
        check_trade_reason(trade),
    ]
    passed = all(r.passed for r in results)
    return passed, results


def main() -> int:
    # override=True so this project's .env wins over any injected ALPACA_* env vars.
    load_dotenv(ROOT / ".env", override=True)
    p = argparse.ArgumentParser()
    p.add_argument("--check", required=True, help="path to trade JSON")
    args = p.parse_args()
    trade_path = Path(args.check)
    if not trade_path.exists():
        print(f"ERROR: trade file not found: {trade_path}", file=sys.stderr)
        return 2

    passed, results = run_all_checks(trade_path)
    print(f"Constitution check: {'PASS' if passed else 'FAIL'} — {trade_path.name}")
    for r in results:
        print(r)
    return 0 if passed else 1


if __name__ == "__main__":
    sys.exit(main())
