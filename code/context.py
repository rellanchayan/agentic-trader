"""
context.py — build ONE tidy snapshot of "everything the trader needs to know right
now", so the intraday brain can read a single file instead of making dozens of calls.

It gathers (in just a few batched API calls):
  * account     — equity, cash, buying power, day-trade count, PDT flag
  * day P&L     — vs the open baseline, and how much loss budget is left
  * positions   — what we currently hold
  * open orders — limit orders still working (so we can re-price / cancel stale ones)
  * budget      — trades used today vs the 20/day cap, position slots used vs 8
  * per-name market data for the day's watchlist + anything we hold:
        last price, bid/ask, spread, quote age, VWAP, opening range (ORB),
        intraday ATR + daily ATR, relative volume, and ready-to-use marketable
        LIMIT prices for buying and selling.
  * clock flags — minutes since open, past the no-new-entries cutoff?, in flatten window?

Writes state/day/<date>/tick_context.json and prints a short summary.

Usage:
    python3 code/context.py            # today
    python3 code/context.py --date 2026-06-15
"""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone as tz
from pathlib import Path

import alpaca_client as ac
import setups
from clockutil import ET, et_now, et_today_str, minutes_since_open, is_after
from daypnl import evaluate as daypnl_evaluate, load_config

ROOT = Path(__file__).resolve().parent.parent
WATCHLIST_FILE = ROOT / "state" / "watchlist.txt"
COMPLETED_DIR = ROOT / "state" / "completed_trades"

SESSION_MINUTES = 390  # 9:30–16:00 = 6.5 hours


def _load_watchlist() -> list[str]:
    out = []
    if WATCHLIST_FILE.exists():
        for line in WATCHLIST_FILE.read_text().splitlines():
            s = line.strip()
            if s and not s.startswith("#"):
                out.append(s.upper())
    return out


def _day_dir(date: str) -> Path:
    return ROOT / "state" / "day" / date


def _load_levels(date: str) -> dict:
    p = _day_dir(date) / "levels.json"
    if p.exists():
        try:
            return json.loads(p.read_text())
        except Exception:
            return {}
    return {}


def _session_start_utc(now_et: datetime) -> datetime:
    d = now_et.date()
    start_et = datetime(d.year, d.month, d.day, 9, 30, tzinfo=ET)
    return start_et.astimezone(tz.utc)


def _todays_trade_count() -> int:
    today = datetime.now(tz.utc).date().isoformat()
    if not COMPLETED_DIR.exists():
        return 0
    n = 0
    for f in COMPLETED_DIR.glob("*.json"):
        try:
            d = json.loads(f.read_text())
            if str(d.get("submitted_at_utc", ""))[:10] == today:
                n += 1
        except Exception:
            continue
    return n


def _recent_intraday_log(date: str, n: int = 10) -> list[dict]:
    p = _day_dir(date) / "intraday_log.jsonl"
    if not p.exists():
        return []
    rows = []
    for line in p.read_text().splitlines():
        try:
            rows.append(json.loads(line))
        except Exception:
            continue
    return rows[-n:]


def _batch_quotes(dc, symbols: list[str]) -> dict:
    from alpaca.data.requests import StockLatestQuoteRequest
    from alpaca.data.enums import DataFeed
    req = StockLatestQuoteRequest(symbol_or_symbols=symbols, feed=DataFeed.IEX)
    return dc.get_stock_latest_quote(req)


def _batch_minute_bars(dc, symbols: list[str], start_utc: datetime) -> dict:
    from alpaca.data.requests import StockBarsRequest
    from alpaca.data.enums import DataFeed
    from alpaca.data.timeframe import TimeFrame
    req = StockBarsRequest(symbol_or_symbols=symbols, timeframe=TimeFrame.Minute,
                           start=start_utc, end=datetime.now(tz.utc), feed=DataFeed.IEX)
    return ac._normalize_bars(dc.get_stock_bars(req))


def _batch_daily_bars(dc, symbols: list[str]) -> dict:
    from datetime import timedelta
    from alpaca.data.requests import StockBarsRequest
    from alpaca.data.enums import DataFeed
    from alpaca.data.timeframe import TimeFrame
    end = datetime.now(tz.utc)
    start = end - timedelta(days=25)
    req = StockBarsRequest(symbol_or_symbols=symbols, timeframe=TimeFrame.Day,
                           start=start, end=end, feed=DataFeed.IEX)
    return ac._normalize_bars(dc.get_stock_bars(req))


def _bar_to_dict(b) -> dict:
    return {"t": b.timestamp.isoformat(), "o": float(b.open), "h": float(b.high),
            "l": float(b.low), "c": float(b.close), "v": int(b.volume)}


def build(date: str) -> dict:
    ac._require_paper()
    config = load_config()
    now_et = et_now()
    mins = minutes_since_open(now_et)

    c = ac._client()
    dc = ac._data_client()

    acct = c.get_account()
    account = {
        "equity": float(acct.equity),
        "cash": float(acct.cash),
        "buying_power": float(acct.buying_power),
        "daytrade_count": int(getattr(acct, "daytrade_count", 0) or 0),
        "pattern_day_trader": bool(getattr(acct, "pattern_day_trader", False)),
    }

    positions = []
    held_symbols = []
    for p in c.get_all_positions():
        held_symbols.append(p.symbol.upper())
        positions.append({
            "ticker": p.symbol, "qty": float(p.qty),
            "avg_entry_price": float(p.avg_entry_price),
            "current_price": float(p.current_price) if getattr(p, "current_price", None) else None,
            "market_value": float(p.market_value),
            "unrealized_pl": float(p.unrealized_pl),
            "unrealized_plpc": float(p.unrealized_plpc),
        })

    open_orders = []
    try:
        from alpaca.trading.requests import GetOrdersRequest
        from alpaca.trading.enums import QueryOrderStatus
        for o in c.get_orders(filter=GetOrdersRequest(status=QueryOrderStatus.OPEN, limit=200)):
            open_orders.append({
                "order_id": str(o.id), "client_order_id": o.client_order_id,
                "ticker": o.symbol, "side": str(o.side).split(".")[-1].lower(),
                "qty": float(o.qty), "limit_price": float(o.limit_price) if o.limit_price else None,
            })
    except Exception:
        pass

    # Which names to look at: the day's screened list (levels.json) + whatever we hold.
    levels = _load_levels(date)
    names = list(levels.keys()) if levels else _load_watchlist()[:12]
    names = [n for n in names if not n.startswith("_")]
    for h in held_symbols:
        if h not in names:
            names.append(h)
    names = sorted(set(names))

    # Batched market data
    quotes = _batch_quotes(dc, names) if names else {}
    minute_bars = _batch_minute_bars(dc, names, _session_start_utc(now_et)) if names else {}
    daily_bars = _batch_daily_bars(dc, names) if names else {}

    frac = max(0.01, min(1.0, mins / SESSION_MINUTES)) if mins > 0 else 0.01
    buy_pct = float(config.get("limit_buy_above_ask_pct", 0.001))
    sell_pct = float(config.get("limit_sell_below_bid_pct", 0.001))
    orb_minutes = int(config.get("orb_minutes", 15))
    breakout_bp = float(config.get("orb_breakout_buffer_bp", 5))

    market = {}
    for sym in names:
        q = quotes.get(sym)
        mbars = [_bar_to_dict(b) for b in minute_bars.get(sym, [])]
        dbars = [_bar_to_dict(b) for b in daily_bars.get(sym, [])]

        bid = float(q.bid_price) if q else None
        ask = float(q.ask_price) if q else None
        age = None
        if q and q.timestamp:
            age = round((datetime.now(tz.utc) - q.timestamp).total_seconds(), 1)
        last = None
        if mbars:
            last = mbars[-1]["c"]
        elif bid and ask:
            last = round((bid + ask) / 2, 2)

        # opening range: prefer premarket-computed levels, else compute from today's bars
        lv = levels.get(sym, {}) if isinstance(levels.get(sym), dict) else {}
        orb = None
        if lv.get("orb_high") is not None:
            orb = {"high": lv.get("orb_high"), "low": lv.get("orb_low")}
        elif mbars:
            orb = setups.opening_range(mbars, orb_minutes)

        vwap_v = setups.vwap(mbars) if mbars else None
        atr_1m = setups.atr(mbars, 14) if len(mbars) >= 2 else None
        atr_day = setups.atr(dbars, 14) if len(dbars) >= 2 else None
        avg_vol = setups.sma([b["v"] for b in dbars], min(10, len(dbars))) if dbars else None
        vol_today = setups.cumulative_volume(mbars) if mbars else 0
        relvol = setups.rel_volume(vol_today, avg_vol, frac) if avg_vol else None
        sbp = setups.spread_bp(bid, ask) if (bid and ask) else None

        market[sym] = {
            "last": last, "bid": bid, "ask": ask,
            "quote_age_sec": age, "spread_bp": round(sbp, 1) if sbp is not None else None,
            "vwap": round(vwap_v, 2) if vwap_v is not None else None,
            "orb_high": orb["high"] if orb else None,
            "orb_low": orb["low"] if orb else None,
            "atr_1m": round(atr_1m, 3) if atr_1m is not None else None,
            "atr_day": round(atr_day, 2) if atr_day is not None else None,
            "rel_volume": round(relvol, 2) if relvol is not None else None,
            "volume_today": vol_today,
            "above_vwap": (last is not None and vwap_v is not None and last > vwap_v),
            "orb_breakout": (last is not None and orb is not None and orb.get("high")
                             and setups.is_orb_breakout(last, orb["high"], breakout_bp)),
            "marketable_buy_limit": setups.marketable_buy_limit(ask, buy_pct) if ask else None,
            "marketable_sell_limit": setups.marketable_sell_limit(bid, sell_pct) if bid else None,
        }

    trades_today = _todays_trade_count()
    pnl = daypnl_evaluate(date, account["equity"])

    context = {
        "date": date,
        "timestamp_et": now_et.isoformat(),
        "minutes_since_open": mins,
        "clock_flags": {
            "past_no_new_entries": is_after(config.get("no_new_entries_after_et", "15:30"), now_et),
            "in_flatten_window": is_after(config.get("flatten_start_et", "15:50"), now_et),
        },
        "account": account,
        "day_pnl": pnl,
        "budget": {
            "trades_today": trades_today,
            "trades_remaining": max(0, int(config.get("max_trades_per_day", 20)) - trades_today),
            "positions_open": len(held_symbols),
            "position_slots_remaining": max(0, int(config.get("max_open_positions", 8)) - len(held_symbols)),
            "daily_deploy_cap_usd": config.get("daily_deploy_cap_usd", 50000),
        },
        "positions": positions,
        "open_orders": open_orders,
        "market": market,
        "recent_ticks": _recent_intraday_log(date),
        "config_snapshot": {k: v for k, v in config.items() if not k.startswith("_")},
    }
    return context


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--date", default=None)
    args = p.parse_args()
    date = args.date or et_today_str()

    ctx = build(date)
    out_path = _day_dir(date) / "tick_context.json"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(ctx, indent=2))

    b = ctx["budget"]
    pnl = ctx["day_pnl"].get("day_pnl")
    print(f"context written: {out_path.relative_to(ROOT)}")
    print(f"  day P&L: {pnl}   trades {b['trades_today']}/{b['trades_today'] + b['trades_remaining']}   "
          f"slots {b['positions_open']}/{b['positions_open'] + b['position_slots_remaining']}   "
          f"names tracked: {len(ctx['market'])}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
