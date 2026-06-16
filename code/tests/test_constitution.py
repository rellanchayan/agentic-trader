"""Tests for the per-order constitution checks (pure: called with explicit dicts)."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import constitution as K

PASS = 0
FAIL = 0


def check(name, cond):
    global PASS, FAIL
    if cond:
        PASS += 1
    else:
        FAIL += 1
        print(f"  FAIL: {name}")


def buy(ticker="AAPL", limit=100.0, qty=10, **extra):
    return {"ticker": ticker, "side": "BUY", "limit_price": limit, "qty": qty,
            "order_type": "LIMIT", "time_in_force": "DAY",
            "reason": "Opening-range breakout with strong relative volume.", **extra}


def portfolio(equity=100000, cash=100000, buying_power=100000, positions=None):
    return {"equity": equity, "cash": cash, "buying_power": buying_power, "positions": positions or []}


def run():
    # per-trade cap ($10,000)
    check("per_trade_cap pass at 10k", K.check_per_trade_cap(buy(limit=100, qty=100)).passed)
    check("per_trade_cap fail over 10k", not K.check_per_trade_cap(buy(limit=100, qty=101)).passed)

    # max 8 open positions
    eight = [{"ticker": f"T{i}", "qty": 1, "market_value": 1000} for i in range(8)]
    check("max_positions fail on 9th name", not K.check_max_open_positions(buy("NEW"), portfolio(positions=eight)).passed)
    check("max_positions ok adding to held", K.check_max_open_positions(buy("T0"), portfolio(positions=eight)).passed)
    seven = eight[:7]
    check("max_positions ok with 7", K.check_max_open_positions(buy("NEW"), portfolio(positions=seven)).passed)

    # 25% per-name cap
    check("position_size fail at 30%", not K.check_position_size(buy(limit=300, qty=100), portfolio()).passed)
    check("position_size ok at 20%", K.check_position_size(buy(limit=200, qty=100), portfolio()).passed)

    # buying power
    check("buying_power fail", not K.check_buying_power(buy(limit=100, qty=60), portfolio(buying_power=5000)).passed)
    check("buying_power ok", K.check_buying_power(buy(limit=100, qty=40), portfolio(buying_power=5000)).passed)

    # order type LIMIT + DAY only
    check("order_type fail MARKET", not K.check_order_type(buy(order_type="MARKET")).passed)
    check("order_type fail GTC", not K.check_order_type(buy(time_in_force="GTC")).passed)
    check("order_type ok", K.check_order_type(buy()).passed)

    # side
    check("side fail", not K.check_side({"side": "HOLD"}).passed)
    check("side ok", K.check_side(buy()).passed)

    # forbidden instruments (leveraged/inverse)
    check("forbidden TQQQ", not K.check_forbidden_instrument(buy("TQQQ")).passed)
    check("forbidden ok AAPL", K.check_forbidden_instrument(buy("AAPL")).passed)

    # trade reason required
    check("reason fail short", not K.check_trade_reason({"reason": "x"}).passed)
    check("reason ok", K.check_trade_reason(buy()).passed)

    print(f"test_constitution: {PASS} passed, {FAIL} failed")
    return 0 if FAIL == 0 else 1


if __name__ == "__main__":
    raise SystemExit(run())
