"""Pure-math tests for setups.py — no network, no files."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import setups

PASS = 0
FAIL = 0


def check(name, cond):
    global PASS, FAIL
    if cond:
        PASS += 1
    else:
        FAIL += 1
        print(f"  FAIL: {name}")


def approx(a, b, tol=1e-6):
    return a is not None and abs(a - b) <= tol


def run():
    check("sma", approx(setups.sma([1, 2, 3, 4], 2), 3.5))
    check("sma too short", setups.sma([1], 2) is None)

    bars = [{"h": 10, "l": 9, "c": 9.5}, {"h": 11, "l": 9.5, "c": 10.5}, {"h": 10.5, "l": 10, "c": 10.2}]
    check("atr", approx(setups.atr(bars, 3), 1.0))

    vbars = [{"h": 10, "l": 10, "c": 10, "v": 100}, {"h": 20, "l": 20, "c": 20, "v": 300}]
    check("vwap", approx(setups.vwap(vbars), 17.5))

    orb = setups.opening_range(bars, 2)
    check("orb high", approx(orb["high"], 11.0))
    check("orb low", approx(orb["low"], 9.0))

    check("spread_bp", approx(setups.spread_bp(99.95, 100.05), 10.0, 0.01))
    check("spread_bp crossed", setups.spread_bp(101, 100) is None)

    check("buy limit", approx(setups.marketable_buy_limit(100, 0.001), 100.10))
    check("sell limit", approx(setups.marketable_sell_limit(100, 0.001), 99.90))

    check("stop", approx(setups.stop_price(100, 2, 1.5, "BUY"), 97.0))
    check("target", approx(setups.target_price(100, 2, 2.5, "BUY"), 105.0))

    check("position_size risk-capped", setups.position_size(250, 100, 97, 10000) == 83)
    check("position_size notional-capped", setups.position_size(100000, 100, 99.99, 10000) == 100)
    check("position_size zero on bad entry", setups.position_size(250, 0, 0, 10000) == 0)

    check("orb_breakout yes", setups.is_orb_breakout(100.06, 100, 5) is True)
    check("orb_breakout no", setups.is_orb_breakout(100.04, 100, 5) is False)
    check("vwap_reclaim yes", setups.is_vwap_reclaim(99.9, 100.06, 100, 5) is True)
    check("vwap_reclaim no (was above)", setups.is_vwap_reclaim(100.1, 100.2, 100, 5) is False)

    check("rel_volume", approx(setups.rel_volume(600000, 1000000, 0.5), 1.2))

    print(f"test_setups: {PASS} passed, {FAIL} failed")
    return 0 if FAIL == 0 else 1


if __name__ == "__main__":
    raise SystemExit(run())
