#!/usr/bin/env bash
# cloud_sync.sh — persist state across isolated CLOUD runs via git.
#
# Each cloud routine gets a FRESH checkout, so without this the bot would forget
# everything between runs (no trade history, no journals, no learning). This script
# pulls the latest saved state at the start of a run and pushes the run's new
# state/ + docs/ at the end.
#
# It only acts when AGENTIC_SYNC=1 (set in the cloud routine's .env). Locally it is
# a no-op, so running the bot on your Mac never spams your git history.
#
# Cloud sandboxes can clone a public repo but cannot PUSH without a write token, so
# pushing uses a fine-grained GitHub token from GITHUB_TOKEN (also set in the cloud
# routine's .env). The token is redacted from all output so it never lands in logs.
#
#   bash code/cloud_sync.sh pull
#   bash code/cloud_sync.sh push "<phase label>"
set -uo pipefail
cd "$(dirname "$0")/.."

# Cloud routines write a .env that sets AGENTIC_SYNC=1 and GITHUB_TOKEN; pick those
# up here. Your local .env sets neither, so locally this stays a no-op.
if [ -f .env ]; then set -a; . ./.env >/dev/null 2>&1 || true; set +a; fi

if [ "${AGENTIC_SYNC:-0}" != "1" ]; then
  echo "cloud_sync: disabled (AGENTIC_SYNC != 1) — no-op"
  exit 0
fi

REMOTE="origin"
if [ -n "${GITHUB_TOKEN:-}" ]; then
  REMOTE="https://x-access-token:${GITHUB_TOKEN}@github.com/rellanchayan/agentic-trader.git"
fi
redact() { sed -E 's#x-access-token:[^@]+@#x-access-token:***@#g'; }

MODE="${1:-push}"

if [ "$MODE" = "pull" ]; then
  git pull --rebase --autostash "$REMOTE" main > /tmp/cs_pull.log 2>&1 || true
  redact < /tmp/cs_pull.log | tail -3
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
if git push "$REMOTE" HEAD:main > /tmp/cs_push.log 2>&1; then
  redact < /tmp/cs_push.log | tail -3
  echo "cloud_sync: state persisted"
else
  redact < /tmp/cs_push.log | tail -3
  echo "cloud_sync: PUSH FAILED — set a GITHUB_TOKEN with Contents:write to enable persistence"
fi
