"""Tests for daypnl.py — day P&L math and the hard $3,000 loss-stop floor."""
import json
import shutil
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import daypnl

PASS = 0
FAIL = 0


def check(name, cond):
    global PASS, FAIL
    if cond:
        PASS += 1
    else:
        FAIL += 1
        print(f"  FAIL: {name}")


def run():
    check("day_pnl", daypnl.day_pnl(99000, 100000) == -1000)
    check("loss_stop trips at -3000", daypnl.loss_stop_tripped(-3000, 3000) is True)
    check("loss_stop not at -2999", daypnl.loss_stop_tripped(-2999, 3000) is False)

    # hard floor: a config that tries to allow a bigger loss is clamped to 3000
    check("hard floor clamps", daypnl.effective_loss_stop_usd({"daily_loss_stop_usd": 5000}) == 3000.0)
    check("smaller stop honored", daypnl.effective_loss_stop_usd({"daily_loss_stop_usd": 2000}) == 2000.0)

    # file-based evaluate, using a clearly-fake date that we clean up
    fake_date = "1900-01-02"
    bdir = daypnl.ROOT / "state" / "day" / fake_date
    try:
        bdir.mkdir(parents=True, exist_ok=True)
        (bdir / "open_baseline.json").write_text(json.dumps({"date": fake_date, "equity": 100000}))
        ev = daypnl.evaluate(fake_date, 97000)
        check("evaluate day_pnl", ev["day_pnl"] == -3000)
        check("evaluate tripped", ev["tripped"] is True)
        ev2 = daypnl.evaluate(fake_date, 98000)
        check("evaluate not tripped", ev2["tripped"] is False)
        ev3 = daypnl.evaluate(fake_date, None)
        check("evaluate handles missing equity", ev3["tripped"] is False and "unavailable" in ev3["note"])
    finally:
        shutil.rmtree(bdir, ignore_errors=True)

    print(f"test_daypnl: {PASS} passed, {FAIL} failed")
    return 0 if FAIL == 0 else 1


if __name__ == "__main__":
    raise SystemExit(run())
