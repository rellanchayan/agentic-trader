"""
alpaca_client.py — the ONLY module that talks to Alpaca.

Hard-wired to paper. `_require_paper()` refuses to run against anything that is
not the paper host, no matter what the environment says.

This is the day-trader edition. On top of the proven swing-trader client it adds
the few things an intraday bot needs:
  * minute bars               (--bars TICKER --timeframe minute --limit N)
  * a full account snapshot   (--account)  equity / cash / daytrade_count / PDT
  * the market clock           (--clock)   the authority on holidays & half-days
  * idempotent order submit    (uses client_order_id = trade_id, so a routine
                                that fires twice never double-submits)
  * a list of open orders      (--open-orders)  so a tick can see / cancel stale limits
  * cancel one order by id     (--cancel ORDER_ID)
  * an intraday equity snapshot (--snapshot)  appended to state/intraday_history.jsonl

CLI usage:
    python3 code/alpaca_client.py --healthcheck
    python3 code/alpaca_client.py --account
    python3 code/alpaca_client.py --clock
    python3 code/alpaca_client.py --positions
    python3 code/alpaca_client.py --snapshot
    python3 code/alpaca_client.py --quote AAPL
    python3 code/alpaca_client.py --bars AAPL --timeframe day --days 5
    python3 code/alpaca_client.py --bars AAPL --timeframe minute --limit 60
    python3 code/alpaca_client.py --open-orders
    python3 code/alpaca_client.py --submit state/pending_trades/<trade_id>.json
    python3 code/alpaca_client.py --order-status <order_id>
    python3 code/alpaca_client.py --cancel <order_id>
    python3 code/alpaca_client.py --reconcile
    python3 code/alpaca_client.py --cancel-all
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

from constitution import run_all_checks

ROOT = Path(__file__).resolve().parent.parent

try:
    from dotenv import load_dotenv
    # override=True so THIS project's .env wins over any ALPACA_* variables the
    # surrounding shell/harness may already have injected (e.g. another project's
    # keys in a global settings env block). In the cloud there is no .env, so the
    # routine's environment variables are used instead.
    load_dotenv(ROOT / ".env", override=True)
except ImportError:
    pass

PORTFOLIO_FILE = ROOT / "state" / "portfolio.json"
HISTORY_FILE = ROOT / "state" / "portfolio_history.jsonl"
INTRADAY_HISTORY_FILE = ROOT / "state" / "intraday_history.jsonl"
HALT_FILE = ROOT / ".HALT_TRADING"

# Hard-wired safety. The script REFUSES to run anything that targets live,
# regardless of the env variable.
PAPER_HOST_REQUIRED = "paper-api.alpaca.markets"


def _require_paper() -> None:
    endpoint = os.environ.get("ALPACA_ENDPOINT", "")
    if PAPER_HOST_REQUIRED not in endpoint:
        print(
            f"REFUSED: ALPACA_ENDPOINT must contain '{PAPER_HOST_REQUIRED}'. "
            f"Got: {endpoint!r}. Live trading disabled in this build.",
            file=sys.stderr,
        )
        sys.exit(99)


def _client():
    """Lazy import so this module imports fine without alpaca-py (for tests)."""
    try:
        from alpaca.trading.client import TradingClient
    except ImportError:
        print("alpaca-py not installed. Run: pip install -r requirements.txt", file=sys.stderr)
        sys.exit(98)

    key = os.environ.get("ALPACA_API_KEY")
    secret = os.environ.get("ALPACA_SECRET_KEY")
    if not (key and secret):
        print("ALPACA_API_KEY / ALPACA_SECRET_KEY missing. See .env.example.", file=sys.stderr)
        sys.exit(97)
    # paper=True is enforced; the SDK uses the paper endpoint regardless of env.
    return TradingClient(key, secret, paper=True)


def _data_client():
    try:
        from alpaca.data.historical import StockHistoricalDataClient
    except ImportError:
        print("alpaca-py not installed.", file=sys.stderr)
        sys.exit(98)
    key = os.environ.get("ALPACA_API_KEY")
    secret = os.environ.get("ALPACA_SECRET_KEY")
    return StockHistoricalDataClient(key, secret)


def _normalize_bars(barset) -> dict:
    """Return the {symbol: [Bar, ...]} dict from a get_stock_bars response,
    tolerant of alpaca-py versions that expose it as `.data` or as a plain dict."""
    data = getattr(barset, "data", None)
    if data is not None:
        return data
    if isinstance(barset, dict):
        return barset
    return {}


def healthcheck() -> int:
    _require_paper()
    try:
        c = _client()
        acct = c.get_account()
        print(f"OK — paper account: {acct.account_number}, equity ${float(acct.equity):,.2f}, status {acct.status}")
        return 0
    except Exception as e:
        print(f"FAIL — {e}", file=sys.stderr)
        return 1


def account() -> int:
    """Full account snapshot the intraday brain needs (PDT, day-trade count, buying power)."""
    _require_paper()
    try:
        c = _client()
        a = c.get_account()
        out = {
            "account_number": a.account_number,
            "status": str(a.status),
            "equity": float(a.equity),
            "last_equity": float(a.last_equity),
            "cash": float(a.cash),
            "buying_power": float(a.buying_power),
            "daytrading_buying_power": float(getattr(a, "daytrading_buying_power", 0) or 0),
            "daytrade_count": int(getattr(a, "daytrade_count", 0) or 0),
            "pattern_day_trader": bool(getattr(a, "pattern_day_trader", False)),
            "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        }
        # Persist so the day-trade guard / preflight can read PDT + equity without
        # another API call.
        account_file = ROOT / "state" / "account.json"
        account_file.parent.mkdir(parents=True, exist_ok=True)
        account_file.write_text(json.dumps(out, indent=2))
        print(json.dumps(out, indent=2))
        return 0
    except Exception as e:
        print(f"FAIL — {e}", file=sys.stderr)
        return 1


def clock() -> int:
    """Alpaca's market clock — the single authority on open/closed, holidays, half-days."""
    _require_paper()
    try:
        c = _client()
        ck = c.get_clock()
        print(json.dumps({
            "is_open": bool(ck.is_open),
            "next_open": ck.next_open.isoformat() if ck.next_open else None,
            "next_close": ck.next_close.isoformat() if ck.next_close else None,
            "timestamp": ck.timestamp.isoformat(),
        }))
        return 0
    except Exception as e:
        print(f"FAIL — {e}", file=sys.stderr)
        return 1


def positions() -> int:
    _require_paper()
    try:
        c = _client()
        acct = c.get_account()
        pos_list = c.get_all_positions()
        equity = float(acct.equity)
        cash = float(acct.cash)

        out_positions = []
        for p in pos_list:
            mv = float(p.market_value)
            out_positions.append({
                "ticker": p.symbol,
                "qty": float(p.qty),
                "avg_entry_price": float(p.avg_entry_price),
                "market_value": mv,
                "unrealized_pl": float(p.unrealized_pl),
                "unrealized_plpc": float(p.unrealized_plpc),
                "current_price": float(p.current_price) if getattr(p, "current_price", None) else None,
                "pct_of_portfolio": mv / equity if equity > 0 else 0.0,
            })

        snapshot = {
            "timestamp_utc": datetime.now(timezone.utc).isoformat(),
            "equity": equity,
            "cash": cash,
            "buying_power": float(acct.buying_power),
            "positions": out_positions,
            "drawdown_from_hwm": _compute_drawdown(equity),
        }

        PORTFOLIO_FILE.parent.mkdir(parents=True, exist_ok=True)
        PORTFOLIO_FILE.write_text(json.dumps(snapshot, indent=2))
        with HISTORY_FILE.open("a") as f:
            f.write(json.dumps({"timestamp_utc": snapshot["timestamp_utc"], "equity": equity, "cash": cash}) + "\n")

        print(json.dumps(snapshot, indent=2))
        return 0
    except Exception as e:
        print(f"FAIL — {e}", file=sys.stderr)
        return 1


def snapshot() -> int:
    """Append one intraday equity point to state/intraday_history.jsonl (for the loss-stop chart)."""
    _require_paper()
    try:
        c = _client()
        a = c.get_account()
        row = {
            "timestamp_utc": datetime.now(timezone.utc).isoformat(),
            "equity": float(a.equity),
            "cash": float(a.cash),
        }
        INTRADAY_HISTORY_FILE.parent.mkdir(parents=True, exist_ok=True)
        with INTRADAY_HISTORY_FILE.open("a") as f:
            f.write(json.dumps(row) + "\n")
        print(json.dumps(row))
        return 0
    except Exception as e:
        print(f"FAIL — {e}", file=sys.stderr)
        return 1


def _compute_drawdown(current_equity: float) -> float:
    if not HISTORY_FILE.exists():
        return 0.0
    hwm = current_equity
    try:
        with HISTORY_FILE.open() as f:
            for line in f:
                try:
                    d = json.loads(line)
                    e = float(d.get("equity", 0))
                    if e > hwm:
                        hwm = e
                except Exception:
                    continue
    except Exception:
        return 0.0
    if hwm <= 0:
        return 0.0
    return max(0.0, (hwm - current_equity) / hwm)


def quote(ticker: str) -> int:
    _require_paper()
    try:
        from alpaca.data.requests import StockLatestQuoteRequest
        from alpaca.data.enums import DataFeed
        dc = _data_client()
        req = StockLatestQuoteRequest(symbol_or_symbols=ticker, feed=DataFeed.IEX)
        result = dc.get_stock_latest_quote(req)
        q = result[ticker]
        ts = q.timestamp
        age = (datetime.now(timezone.utc) - ts).total_seconds() if ts else None
        print(json.dumps({
            "ticker": ticker,
            "bid": float(q.bid_price),
            "ask": float(q.ask_price),
            "bid_size": int(q.bid_size),
            "ask_size": int(q.ask_size),
            "timestamp": ts.isoformat() if ts else None,
            "age_sec": round(age, 1) if age is not None else None,
        }))
        return 0
    except Exception as e:
        print(f"FAIL — {e}", file=sys.stderr)
        return 1


def bars(ticker: str, timeframe: str, days: int, limit: int) -> int:
    """Daily or 1-minute bars. Minute bars power the intraday setups (ORB/VWAP/ATR)."""
    _require_paper()
    try:
        from datetime import timedelta
        from alpaca.data.requests import StockBarsRequest
        from alpaca.data.enums import DataFeed
        from alpaca.data.timeframe import TimeFrame
        dc = _data_client()
        end = datetime.now(timezone.utc)

        if timeframe == "minute":
            tf = TimeFrame.Minute
            # generous lookback so we always capture today's session from the open
            start = end - timedelta(minutes=max(limit, 1) + 60)
            take = limit
        else:
            tf = TimeFrame.Day
            start = end - timedelta(days=days * 2 + 5)  # buffer for non-trading days
            take = days

        req = StockBarsRequest(symbol_or_symbols=ticker, timeframe=tf, start=start, end=end, feed=DataFeed.IEX)
        bars_data = dc.get_stock_bars(req).data.get(ticker, [])
        out = []
        for b in bars_data[-take:]:
            out.append({
                "t": b.timestamp.isoformat(),
                "o": float(b.open), "h": float(b.high), "l": float(b.low), "c": float(b.close),
                "v": int(b.volume),
            })
        print(json.dumps({"ticker": ticker, "timeframe": timeframe, "count": len(out), "bars": out}, indent=2))
        return 0
    except Exception as e:
        print(f"FAIL — {e}", file=sys.stderr)
        return 1


def open_orders() -> int:
    """List currently-open (unfilled) orders so a tick can re-price or cancel stale limits."""
    _require_paper()
    try:
        from alpaca.trading.requests import GetOrdersRequest
        from alpaca.trading.enums import QueryOrderStatus
        c = _client()
        req = GetOrdersRequest(status=QueryOrderStatus.OPEN, limit=200)
        orders = c.get_orders(filter=req)
        out = []
        for o in orders:
            out.append({
                "order_id": str(o.id),
                "client_order_id": o.client_order_id,
                "symbol": o.symbol,
                "side": str(o.side).split(".")[-1].lower(),
                "qty": float(o.qty),
                "filled_qty": float(o.filled_qty or 0),
                "limit_price": float(o.limit_price) if o.limit_price else None,
                "status": str(o.status).split(".")[-1].lower(),
                "submitted_at": o.submitted_at.isoformat() if o.submitted_at else None,
            })
        print(json.dumps({"open_orders": out, "count": len(out)}, indent=2))
        return 0
    except Exception as e:
        print(f"FAIL — {e}", file=sys.stderr)
        return 1


def _finalize_submitted(trade: dict, order, path: Path) -> dict:
    """Stamp a trade JSON with submission state and move it to completed_trades/."""
    trade["status"] = str(order.status).split(".")[-1].lower() or "submitted"
    if trade["status"] not in ("filled", "partially_filled", "canceled", "expired", "rejected"):
        trade["status"] = "submitted"
    trade["alpaca_order_id"] = str(order.id)
    trade["client_order_id"] = order.client_order_id
    trade["submitted_at_utc"] = datetime.now(timezone.utc).isoformat()
    path.write_text(json.dumps(trade, indent=2))
    completed = ROOT / "state" / "completed_trades" / path.name
    completed.parent.mkdir(parents=True, exist_ok=True)
    path.replace(completed)
    return {
        "trade_id": trade["trade_id"],
        "alpaca_order_id": str(order.id),
        "status": str(order.status),
        "submitted_at": trade["submitted_at_utc"],
        "saved_to": str(completed.relative_to(ROOT)),
    }


def submit(trade_json_path: str) -> int:
    _require_paper()
    if HALT_FILE.exists():
        print("REFUSED: .HALT_TRADING exists", file=sys.stderr)
        return 95

    path = Path(trade_json_path)
    if not path.exists():
        print(f"FAIL: trade file not found: {path}", file=sys.stderr)
        return 2
    trade = json.loads(path.read_text())

    required = ["trade_id", "ticker", "side", "qty", "limit_price", "reason"]
    for k in required:
        if k not in trade:
            print(f"FAIL: trade JSON missing required key: {k}", file=sys.stderr)
            return 3

    passed, checks = run_all_checks(path)
    if not passed:
        print("REFUSED: trade failed checks", file=sys.stderr)
        for check in checks:
            print(check, file=sys.stderr)
        return 90

    if trade.get("order_type", "LIMIT").upper() != "LIMIT":
        print("REFUSED: only LIMIT orders supported", file=sys.stderr)
        return 94
    if trade.get("time_in_force", "DAY").upper() != "DAY":
        print("REFUSED: only DAY orders supported", file=sys.stderr)
        return 94

    try:
        from alpaca.trading.requests import LimitOrderRequest
        from alpaca.trading.enums import OrderSide, TimeInForce
        c = _client()

        # --- Idempotency: a routine that fires twice must never double-submit. ---
        # We use the trade_id as the Alpaca client_order_id (unique per account).
        # If an order with this id already exists, we adopt it instead of re-sending.
        client_id = str(trade["trade_id"])
        try:
            existing = c.get_order_by_client_id(client_id)
            if existing is not None:
                result = _finalize_submitted(trade, existing, path)
                result["note"] = "already submitted (idempotent no-op)"
                print(json.dumps(result))
                return 0
        except Exception:
            pass  # not found → proceed to submit

        side = OrderSide.BUY if trade["side"].upper() == "BUY" else OrderSide.SELL
        req = LimitOrderRequest(
            symbol=trade["ticker"].upper(),
            qty=float(trade["qty"]),
            side=side,
            time_in_force=TimeInForce.DAY,
            limit_price=round(float(trade["limit_price"]), 2),
            client_order_id=client_id,
        )
        order = c.submit_order(req)
        print(json.dumps(_finalize_submitted(trade, order, path)))
        return 0
    except Exception as e:
        print(f"SUBMIT FAILED — {e}", file=sys.stderr)
        return 1


def order_status(order_id: str) -> int:
    _require_paper()
    try:
        c = _client()
        o = c.get_order_by_id(order_id)
        out = {
            "order_id": str(o.id),
            "symbol": o.symbol,
            "status": str(o.status),
            "qty": float(o.qty),
            "filled_qty": float(o.filled_qty or 0),
            "filled_avg_price": float(o.filled_avg_price) if o.filled_avg_price else None,
            "limit_price": float(o.limit_price) if o.limit_price else None,
            "submitted_at": o.submitted_at.isoformat() if o.submitted_at else None,
            "filled_at": o.filled_at.isoformat() if o.filled_at else None,
        }
        print(json.dumps(out, indent=2))
        return 0
    except Exception as e:
        print(f"FAIL — {e}", file=sys.stderr)
        return 1


def cancel_one(order_id: str) -> int:
    _require_paper()
    try:
        c = _client()
        c.cancel_order_by_id(order_id)
        print(json.dumps({"canceled": order_id}))
        return 0
    except Exception as e:
        print(f"FAIL — {e}", file=sys.stderr)
        return 1


def reconcile() -> int:
    """Check every submitted trade against Alpaca and record what really happened.

    A trade file stays in status "submitted" until the order reaches a final
    state. This keeps our local records honest — we never assume an order filled.
    """
    _require_paper()
    completed_dir = ROOT / "state" / "completed_trades"
    if not completed_dir.exists():
        print(json.dumps({"checked": 0, "updated": [], "still_open": []}))
        return 0

    FINAL_STATES = {"filled", "canceled", "expired", "rejected", "done_for_day"}
    updated: list[dict] = []
    still_open: list[dict] = []
    checked = 0

    try:
        c = _client()
        for path in sorted(completed_dir.glob("*.json")):
            trade = json.loads(path.read_text())
            order_id = trade.get("alpaca_order_id")
            if not order_id or trade.get("status") not in ("submitted", "partially_filled"):
                continue
            checked += 1
            o = c.get_order_by_id(order_id)
            status = str(o.status).split(".")[-1].lower()
            trade["filled_qty"] = float(o.filled_qty or 0)
            trade["filled_avg_price"] = float(o.filled_avg_price) if o.filled_avg_price else None
            if status in FINAL_STATES:
                trade["status"] = status
                trade["reconciled_at_utc"] = datetime.now(timezone.utc).isoformat()
                path.write_text(json.dumps(trade, indent=2))
                updated.append({
                    "trade_id": trade.get("trade_id"),
                    "ticker": trade.get("ticker"),
                    "side": trade.get("side"),
                    "status": status,
                    "filled_qty": trade["filled_qty"],
                    "filled_avg_price": trade["filled_avg_price"],
                })
            else:
                if status == "partially_filled":
                    trade["status"] = "partially_filled"
                    path.write_text(json.dumps(trade, indent=2))
                still_open.append({
                    "trade_id": trade.get("trade_id"),
                    "ticker": trade.get("ticker"),
                    "status": status,
                })
        print(json.dumps({"checked": checked, "updated": updated, "still_open": still_open}, indent=2))
        return 0
    except Exception as e:
        print(f"FAIL — {e}", file=sys.stderr)
        return 1


def cancel_all() -> int:
    _require_paper()
    try:
        c = _client()
        canceled = c.cancel_orders()
        print(json.dumps({"canceled_count": len(canceled) if canceled else 0}))
        return 0
    except Exception as e:
        print(f"FAIL — {e}", file=sys.stderr)
        return 1


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--healthcheck", action="store_true")
    p.add_argument("--account", action="store_true")
    p.add_argument("--clock", action="store_true")
    p.add_argument("--is-open", action="store_true", help="alias for --clock")
    p.add_argument("--positions", action="store_true")
    p.add_argument("--snapshot", action="store_true")
    p.add_argument("--quote", metavar="TICKER")
    p.add_argument("--bars", metavar="TICKER")
    p.add_argument("--timeframe", choices=["day", "minute"], default="day")
    p.add_argument("--days", type=int, default=5)
    p.add_argument("--limit", type=int, default=60)
    p.add_argument("--open-orders", action="store_true")
    p.add_argument("--submit", metavar="TRADE_JSON")
    p.add_argument("--order-status", metavar="ORDER_ID")
    p.add_argument("--cancel", metavar="ORDER_ID")
    p.add_argument("--reconcile", action="store_true")
    p.add_argument("--cancel-all", action="store_true")
    args = p.parse_args()

    if args.healthcheck:
        return healthcheck()
    if args.account:
        return account()
    if args.clock or args.is_open:
        return clock()
    if args.positions:
        return positions()
    if args.snapshot:
        return snapshot()
    if args.quote:
        return quote(args.quote.upper())
    if args.bars:
        return bars(args.bars.upper(), args.timeframe, args.days, args.limit)
    if args.open_orders:
        return open_orders()
    if args.submit:
        return submit(args.submit)
    if args.order_status:
        return order_status(args.order_status)
    if args.cancel:
        return cancel_one(args.cancel)
    if args.reconcile:
        return reconcile()
    if args.cancel_all:
        return cancel_all()

    p.print_help()
    return 1


if __name__ == "__main__":
    sys.exit(main())
