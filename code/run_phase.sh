#!/usr/bin/env bash
# run_phase.sh — installs dependencies if needed, then runs the DETERMINISTIC part
# of one trading phase. The language-model judgment (research, the buy/sell decision,
# the journal) is done by the Claude skills that call this script; this script only
# does the mechanical, repeatable steps so they are identical every time.
#
#   bash code/run_phase.sh deps                 # just make sure deps are installed
#   bash code/run_phase.sh premarket            # account snapshot, baseline, screen
#   bash code/run_phase.sh tick                 # preflight gate; if PROCEED, build context
#   bash code/run_phase.sh flatten 1            # end-of-day flatten, pass 1|2|3
#   bash code/run_phase.sh postmarket           # reconcile, day summary, gated auto-tune
#
# Exit codes for `tick`: 0 = PROCEED (context built), 3 = EXIT (do nothing),
#                        4 = FLATTEN (loss-stop tripped — caller must flatten).
set -uo pipefail
cd "$(dirname "$0")/.."

if [ -x ".venv/bin/python" ]; then PY=".venv/bin/python"; else PY="python3"; fi

ensure_deps() {
  if ! "$PY" -c "import alpaca, dotenv" >/dev/null 2>&1; then
    if ! "$PY" -m pip install -q -r requirements.txt >/dev/null 2>&1; then
      python3 -m venv .venv
      PY=".venv/bin/python"
      "$PY" -m pip install -q -r requirements.txt
    fi
  fi
}

PHASE="${1:-}"
ensure_deps

case "$PHASE" in
  deps)
    echo "deps ok"
    ;;

  premarket)
    echo "== PREMARKET =="
    "$PY" code/alpaca_client.py --healthcheck || exit 1
    "$PY" code/alpaca_client.py --reconcile           # close the books on anything stale
    "$PY" code/alpaca_client.py --account             # writes state/account.json
    "$PY" code/daypnl.py --set-baseline               # open equity baseline + clear day-stop
    "$PY" code/alpaca_client.py --positions           # refresh portfolio.json
    "$PY" code/watchlist_build.py --top 10            # today's names -> levels.json
    ;;

  tick)
    "$PY" code/preflight.py
    RC=$?
    if [ "$RC" -eq 0 ]; then
      "$PY" code/context.py        # only build the (heavier) context if we may trade
    fi
    exit $RC
    ;;

  flatten)
    AGG="${2:-1}"
    "$PY" code/flatten.py --aggression "$AGG"
    ;;

  postmarket)
    echo "== POSTMARKET =="
    "$PY" code/alpaca_client.py --reconcile           # final truth on every order
    "$PY" code/alpaca_client.py --positions           # snapshot equity for the history
    "$PY" code/metrics.py --summary                   # write state/runs/<date>-summary.json
    "$PY" code/metrics.py || true                     # long-run scorecard (never blocks)
    ;;

  *)
    echo "usage: bash code/run_phase.sh {deps|premarket|tick|flatten N|postmarket}" >&2
    exit 2
    ;;
esac
