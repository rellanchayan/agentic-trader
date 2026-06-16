# Glossary (every term, in plain English)

Trading has a lot of jargon. Here is every term this project uses, explained simply.

- **Paper trading** — practice trading with fake money but real prices. No real dollars are at risk.

- **Limit order** — an order to buy or sell *only at a price you set, or better, never worse*. A BUY
  limit at $100 will pay $100 or less; a SELL limit at $100 will get $100 or more.

- **Market order** — an order to buy/sell *right now at whatever price is available*. Fast but risky on
  moving stocks. **This bot never uses market orders.**

- **Marketable limit** — a limit order priced just past the current price (a touch above the ask to buy,
  a touch below the bid to sell) so it fills almost immediately, but still with a price cap for safety.

- **DAY order** — an order that is only good for today. If it doesn't fill by the close, it's canceled
  automatically. (We use LIMIT + DAY orders only.)

- **Bid / Ask** — the **bid** is the highest price someone will pay right now; the **ask** is the lowest
  price someone will sell for. You usually buy at the ask and sell at the bid.

- **Spread** — the gap between the bid and the ask. A wide spread is a hidden cost: you "lose" the spread
  just by getting in and out. We avoid names with wide spreads. Measured in **basis points (bp)**.

- **Basis point (bp)** — one one-hundredth of a percent. 100 bp = 1%. A 5 bp spread = 0.05%.

- **Slippage** — getting a worse price than you expected, usually from using market orders in fast
  markets. Limit orders prevent this.

- **Liquidity** — how easily you can trade a stock without moving its price. High average volume = liquid.

- **Volume** — how many shares trade. **Relative volume** = today's volume compared to a normal day; above
  1.0 means busier than usual (good for day trading).

- **VWAP** — Volume-Weighted Average Price: the day's average price weighted by how much traded at each
  level. A common "fair value" line; trading above it is bullish, below it bearish.

- **Opening range / ORB** — the high and low of the first ~15 minutes of the day. Breaking above the high
  (an "Opening-Range Breakout") is a classic buy signal.

- **ATR (Average True Range)** — how much a stock typically moves over a period. We size stops and targets
  as multiples of ATR, so a calm stock gets a tight stop and a wild one gets more room.

- **Stop (stop level)** — the price where we admit the trade idea was wrong and sell to cut the loss.

- **Target** — the price where we take profit and sell.

- **R / R-multiple** — your risk on a trade is "1R" (the distance from entry to stop). A win of twice your
  risk is "+2R"; a full stop-out is "−1R". Thinking in R keeps wins and losses comparable.

- **Position** — a stock you currently own. **Flat** means you own nothing (zero positions).

- **Overnight exposure** — risk from holding positions after the close (a gap up or down before the next
  open). This bot goes flat every night, so its overnight exposure is zero.

- **Partial fill** — when only some of your order's shares fill (e.g., you wanted 100, got 60). We always
  act on what actually filled, never what we hoped would fill.

- **Reconcile** — checking with the broker (Alpaca) what *really* happened to each order. We never assume
  an order filled — we reconcile.

- **Drawdown** — how far the account is below its highest point. A −5% drawdown means we're 5% below the
  best the account has ever been.

- **Loss-stop (daily)** — a hard rule: if we're down $3,000 on the day, stop trading and sell everything.
  It resets the next morning.

- **PDT (Pattern Day Trader)** — a US rule: an account under $25,000 can't freely day-trade. We keep the
  account above $25,000 to stay clear of it, and the bot blocks new buys if equity nears that line.

- **Margin (borrowing)** — using the broker's money to trade bigger than your cash. **This bot never
  borrows.** It uses a margin-type account only so same-day round trips settle cleanly, but it never
  deploys more than the account's own equity.

- **Regime / market mood** — the overall tone of the day: **risk-on** (buyers confident, trends work) or
  **risk-off** (fear, selling, be careful). The morning plan calls it.

- **Setup** — a specific, repeatable trade situation we know how to handle (ORB, VWAP reclaim, etc.).

- **Expectancy** — the average profit (in R) we expect per trade for a setup over many trades. Positive
  expectancy = the setup makes money on average.
