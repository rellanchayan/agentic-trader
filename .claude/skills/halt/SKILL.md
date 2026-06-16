---
name: halt
description: Emergency stop. Creates the .HALT_TRADING file so the bot places no more orders. Removal is by a human only.
allowed-tools: Write(.HALT_TRADING), Read
---

# Halt

Use this to STOP all trading immediately. It writes a file called `.HALT_TRADING` in the project root.
While that file exists:
- the safety gate (`preflight.py`) makes every tick EXIT without trading,
- `alpaca_client.py --submit` refuses to send any order,
- the constitution check fails on every order.

## To halt
Write `.HALT_TRADING` with a short reason and the time, e.g.:
```
Halted by Chayan on 2026-06-15 11:20 ET — wanted to pause and review.
```

## Important
- This does NOT cancel open orders or sell positions by itself. If you also want to go flat, run
  `/flatten-close` first.
- **Only a human removes `.HALT_TRADING`.** The bot must never delete it. Trading resumes only when a
  person deletes the file on purpose.
