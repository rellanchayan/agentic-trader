"""
setups.py — PURE math for the day-trading setups. No network, no files, no clock.

Everything here takes numbers in and returns numbers out, so it is fully unit-
testable offline. The intraday brain reads the OUTPUTS of these functions (packed
into the per-tick context) and decides what to do; this module never decides.

Definitions in plain English live in docs/GLOSSARY.md. Quick version:
  * VWAP  — the average price of the day, weighted by how much volume traded at
            each price. A fair "where is the stock really trading" line.
  * ORB   — opening range breakout. The high/low of the first N minutes of the
            day. Breaking above that high (or below the low) is a classic signal.
  * ATR   — average true range. A measure of how much the stock typically moves;
            we size stops and targets as multiples of ATR.
  * bp    — "basis points". 1 bp = 0.01%. 100 bp = 1%.

A "bar" here is a dict: {"t": iso, "o": float, "h": float, "l": float, "c": float, "v": int}
"""

from __future__ import annotations

import math


# ---------- basic series math ----------

def sma(values: list[float], n: int) -> float | None:
    """Simple moving average of the last n values."""
    if n <= 0 or len(values) < n:
        return None
    return sum(values[-n:]) / n


def true_ranges(bars: list[dict]) -> list[float]:
    """The 'true range' of each bar: the biggest of (high-low), |high-prevclose|,
    |low-prevclose|. Captures gaps between bars, not just the bar's own range."""
    out: list[float] = []
    prev_close = None
    for b in bars:
        h, l, c = float(b["h"]), float(b["l"]), float(b["c"])
        if prev_close is None:
            out.append(h - l)
        else:
            out.append(max(h - l, abs(h - prev_close), abs(l - prev_close)))
        prev_close = c
    return out


def atr(bars: list[dict], n: int = 14) -> float | None:
    """Average true range over the last n bars."""
    if len(bars) < 2:
        return None
    tr = true_ranges(bars)
    if len(tr) < n:
        n = len(tr)
    if n <= 0:
        return None
    return sum(tr[-n:]) / n


def vwap(bars: list[dict]) -> float | None:
    """Volume-weighted average price across the supplied bars (use today's bars)."""
    num = 0.0
    den = 0.0
    for b in bars:
        typical = (float(b["h"]) + float(b["l"]) + float(b["c"])) / 3.0
        vol = float(b["v"])
        num += typical * vol
        den += vol
    if den <= 0:
        return None
    return num / den


def opening_range(bars: list[dict], minutes: int) -> dict | None:
    """High and low of the first `minutes` one-minute bars of the session.
    Assumes `bars` are today's 1-minute bars in time order, starting at the open."""
    if not bars:
        return None
    window = bars[:max(1, minutes)]
    return {
        "high": max(float(b["h"]) for b in window),
        "low": min(float(b["l"]) for b in window),
        "bars_used": len(window),
    }


def cumulative_volume(bars: list[dict]) -> int:
    return int(sum(float(b["v"]) for b in bars))


def rel_volume(today_cumulative_vol: float, avg_full_day_vol: float, fraction_of_day_elapsed: float) -> float | None:
    """Relative volume = how busy today is versus a normal day, at this point in
    the session. >1 means heavier-than-usual trading (what a day trader wants)."""
    if avg_full_day_vol <= 0 or fraction_of_day_elapsed <= 0:
        return None
    expected_by_now = avg_full_day_vol * min(1.0, fraction_of_day_elapsed)
    if expected_by_now <= 0:
        return None
    return today_cumulative_vol / expected_by_now


def spread_bp(bid: float, ask: float) -> float | None:
    """The bid/ask spread in basis points of the mid price. Wide spread = costly to trade."""
    if bid <= 0 or ask <= 0 or ask < bid:
        return None
    mid = (bid + ask) / 2.0
    if mid <= 0:
        return None
    return (ask - bid) / mid * 10000.0


# ---------- order pricing (LIMIT only — no market orders allowed) ----------

def marketable_buy_limit(ask: float, above_ask_pct: float) -> float:
    """A BUY limit set slightly ABOVE the ask so it fills right away like a market
    order would — but can never fill worse than this capped price."""
    return round(ask * (1.0 + max(0.0, above_ask_pct)), 2)


def marketable_sell_limit(bid: float, below_bid_pct: float) -> float:
    """A SELL limit set slightly BELOW the bid so it fills right away — but never
    worse than this floor price."""
    return round(bid * (1.0 - max(0.0, below_bid_pct)), 2)


# ---------- stops, targets, sizing ----------

def stop_price(entry: float, atr_value: float, mult: float, side: str = "BUY") -> float:
    """Where we admit the idea was wrong and exit. For a long, it's below entry."""
    dist = atr_value * mult
    return round(entry - dist if side.upper() == "BUY" else entry + dist, 2)


def target_price(entry: float, atr_value: float, mult: float, side: str = "BUY") -> float:
    """Where we take profit. For a long, it's above entry."""
    dist = atr_value * mult
    return round(entry + dist if side.upper() == "BUY" else entry - dist, 2)


def position_size(risk_usd: float, entry: float, stop: float, per_trade_max_usd: float) -> int:
    """How many shares to buy.

    Two caps, whichever is smaller:
      1. Risk cap: lose no more than `risk_usd` if the stop is hit
         → shares = risk_usd / (entry - stop)
      2. Notional cap: spend no more than `per_trade_max_usd`
         → shares = per_trade_max_usd / entry
    Returns a whole number of shares (rounded down), never negative.
    """
    if entry <= 0:
        return 0
    stop_dist = abs(entry - stop)
    by_risk = (risk_usd / stop_dist) if stop_dist > 0 else float("inf")
    by_notional = per_trade_max_usd / entry
    shares = min(by_risk, by_notional)
    if not math.isfinite(shares) or shares < 0:
        return 0
    return int(math.floor(shares))


# ---------- simple signal hints (booleans the brain may use) ----------

def is_orb_breakout(price: float, orb_high: float, buffer_bp: float) -> bool:
    """Price has cleared the opening-range high by at least the buffer."""
    if orb_high <= 0:
        return False
    return price >= orb_high * (1.0 + buffer_bp / 10000.0)


def is_orb_breakdown(price: float, orb_low: float, buffer_bp: float) -> bool:
    if orb_low <= 0:
        return False
    return price <= orb_low * (1.0 - buffer_bp / 10000.0)


def is_vwap_reclaim(prev_price: float, price: float, vwap_value: float, buffer_bp: float) -> bool:
    """Was below VWAP, now back above it by the buffer — a bullish reclaim."""
    if vwap_value <= 0:
        return False
    above = vwap_value * (1.0 + buffer_bp / 10000.0)
    return prev_price < vwap_value and price >= above
