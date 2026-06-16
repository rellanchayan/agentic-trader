"""
watchlist_build.py — the pre-market screen.

Takes the big base universe (state/watchlist.txt) and narrows it to a short list of
names that are actually worth watching today: liquid, and ideally moving (gapping or
trading on heavier-than-usual volume). It writes those names plus reference levels to
state/day/<date>/levels.json, which the day-screener agent then reviews/refines and
the intraday brain reads all day.

It runs BEFORE the open, so the opening range (ORB) does not exist yet — those fields
are left null and get filled in live by code/context.py after the first few minutes.

Levels written per name:
    sector, prev_close, atr_day, avg_vol_10d, premarket_price, gap_pct, spread_bp,
    orb_high (null), orb_low (null), note

Usage:
    python3 code/watchlist_build.py --date 2026-06-15 --top 10
"""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timedelta, timezone as tz
from pathlib import Path

import alpaca_client as ac
import setups
from clockutil import et_today_str
from daypnl import load_config

ROOT = Path(__file__).resolve().parent.parent
WATCHLIST_FILE = ROOT / "state" / "watchlist.txt"
SECTORS_FILE = ROOT / "state" / "sectors.json"

MIN_AVG_VOL = 2_000_000  # only consider names trading at least ~2M shares/day (liquid)


def _load_watchlist() -> list[str]:
    out = []
    if WATCHLIST_FILE.exists():
        for line in WATCHLIST_FILE.read_text().splitlines():
            s = line.strip()
            if s and not s.startswith("#"):
                out.append(s.upper())
    return out


def _bar_to_dict(b) -> dict:
    return {"t": b.timestamp.isoformat(), "o": float(b.open), "h": float(b.high),
            "l": float(b.low), "c": float(b.close), "v": int(b.volume)}


def build(date: str, top: int) -> dict:
    ac._require_paper()
    config = load_config()
    names = _load_watchlist()
    sectors = json.loads(SECTORS_FILE.read_text()) if SECTORS_FILE.exists() else {}
    dc = ac._data_client()

    from alpaca.data.requests import StockBarsRequest, StockLatestQuoteRequest
    from alpaca.data.enums import DataFeed
    from alpaca.data.timeframe import TimeFrame

    end = datetime.now(tz.utc)
    start = end - timedelta(days=25)
    dbars = ac._normalize_bars(dc.get_stock_bars(StockBarsRequest(
        symbol_or_symbols=names, timeframe=TimeFrame.Day, start=start, end=end, feed=DataFeed.IEX)))
    try:
        quotes = dc.get_stock_latest_quote(StockLatestQuoteRequest(symbol_or_symbols=names, feed=DataFeed.IEX))
    except Exception:
        quotes = {}

    rows = []
    for sym in names:
        bars = [_bar_to_dict(b) for b in dbars.get(sym, [])]
        if len(bars) < 5:
            continue
        prev_close = bars[-1]["c"]
        avg_vol = setups.sma([b["v"] for b in bars], min(10, len(bars)))
        atr_day = setups.atr(bars, 14)
        q = quotes.get(sym)
        pm_price, spread_bp = None, None
        if q and q.bid_price and q.ask_price:
            pm_price = round((float(q.bid_price) + float(q.ask_price)) / 2, 2)
            spread_bp = setups.spread_bp(float(q.bid_price), float(q.ask_price))
        gap_pct = round((pm_price - prev_close) / prev_close, 4) if (pm_price and prev_close) else None

        if not avg_vol or avg_vol < MIN_AVG_VOL:
            continue

        # score: liquidity (log volume) + size of the gap (movement potential)
        import math
        score = math.log10(avg_vol) + (abs(gap_pct) * 20 if gap_pct is not None else 0)
        rows.append({
            "ticker": sym, "sector": sectors.get(sym, "unknown"),
            "prev_close": round(prev_close, 2),
            "atr_day": round(atr_day, 2) if atr_day else None,
            "avg_vol_10d": int(avg_vol),
            "premarket_price": pm_price,
            "gap_pct": gap_pct,
            "spread_bp": round(spread_bp, 1) if spread_bp is not None else None,
            "score": round(score, 3),
        })

    rows.sort(key=lambda r: r["score"], reverse=True)
    chosen = rows[:max(1, top)]

    levels = {"_meta": {
        "date": date,
        "generated_utc": datetime.now(tz.utc).isoformat(),
        "source": "watchlist_build",
        "candidates_considered": len(rows),
        "top": len(chosen),
        "note": "Pre-market screen. ORB levels fill in live after the open. The day-screener agent may edit this.",
    }}
    for r in chosen:
        gap_txt = f"{r['gap_pct']:+.1%} gap" if r["gap_pct"] is not None else "no premarket quote"
        levels[r["ticker"]] = {
            "sector": r["sector"], "prev_close": r["prev_close"], "atr_day": r["atr_day"],
            "avg_vol_10d": r["avg_vol_10d"], "premarket_price": r["premarket_price"],
            "gap_pct": r["gap_pct"], "spread_bp": r["spread_bp"],
            "orb_high": None, "orb_low": None,
            "note": f"liquid ({r['avg_vol_10d']:,} sh/day); {gap_txt}",
        }
    return levels


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--date", default=None)
    p.add_argument("--top", type=int, default=10)
    args = p.parse_args()
    date = args.date or et_today_str()

    levels = build(date, args.top)
    out_dir = ROOT / "state" / "day" / date
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "levels.json").write_text(json.dumps(levels, indent=2))
    chosen = [k for k in levels if not k.startswith("_")]
    print(f"levels written: state/day/{date}/levels.json")
    print(f"  today's names ({len(chosen)}): {', '.join(chosen)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
