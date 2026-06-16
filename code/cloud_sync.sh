#!/usr/bin/env bash
# cloud_sync.sh — persist state across isolated CLOUD runs via git.
#
# Each cloud routine gets a FRESH checkout, so without this the bot would forget
# everything between runs (no baseline, no trade history, no learning). This script
# pulls the latest saved state at the start of a run and pushes the run's new
# state/ + docs/ at the end.
#
# It only does anything when AGENTIC_SYNC=1 (set in the cloud routine's environment).
# Locally it is a no-op, so running the bot on your Mac never spams your git history.
#
#   bash code/cloud_sync.sh pull
#   bash code/cloud_sync.sh push "<phase label>"
set -uo pipefail
cd "$(dirname "$0")/.."

# Cloud routines write a .env that sets AGENTIC_SYNC=1; pick that up here. Your
# local .env does not set it, so locally this stays a no-op (no git spam).
if [ -f .env ]; then set -a; . ./.env >/dev/null 2>&1 || true; set +a; fi

if [ "${AGENTIC_SYNC:-0}" != "1" ]; then
  echo "cloud_sync: disabled (AGENTIC_SYNC != 1) — no-op"
  exit 0
fi

MODE="${1:-push}"

if [ "$MODE" = "pull" ]; then
  git pull --rebase --autostash origin main 2>&1 | tail -3 || echo "cloud_sync: pull failed (continuing with local state)"
  exit 0
fi

LABEL="${2:-update}"
git add state docs 2>/dev/null || true
if git diff --cached --quiet 2>/dev/null; then
  echo "cloud_sync: nothing to persist"
  exit 0
fi
git -c user.email="bot@agentic-trader.local" -c user.name="agentic-trader bot" \
    commit -q -m "state: ${LABEL} [skip ci]" 2>&1 | tail -2 || true
if git push origin HEAD:main 2>&1 | tail -3; then
  echo "cloud_sync: state persisted"
else
  echo "cloud_sync: PUSH FAILED — state for this run was NOT saved (check cloud git write access)"
fi
