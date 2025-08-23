#!/usr/bin/env bash
set -euo pipefail

# Env with defaults
HOST="${DEBUGPY_HOST:-0.0.0.0}"
PORT="${DEBUGPY_PORT:-5678}"
WAIT="${WAIT_FOR_CLIENT:-true}"
PROC="${PROCEDURE:-}"

if [[ -z "$PROC" ]]; then
  echo "ERROR: PROCEDURE env var is required. Examples:"
  echo "  PROCEDURE=tools/myfop.py"
  echo "  PROCEDURE=mypkg.worker:main"
  exit 1
fi

WAIT_FLAG=""
if [[ "$WAIT" == "true" || "$WAIT" == "1" ]]; then
  WAIT_FLAG="--wait-for-client"
fi

# If PROCEDURE contains "module:function", run that callable
if [[ "$PROC" == *:* ]]; then
  MODULE="${PROC%%:*}"
  FUNC="${PROC##*:}"
  echo "Starting debugpy on ${HOST}:${PORT} and waiting for IDE: ${WAIT}"
  exec python -m debugpy --listen "${HOST}:${PORT}" ${WAIT_FLAG} -c \
"import importlib, sys; \
print('>> Running ${MODULE}:${FUNC} under debugpy...', flush=True); \
mod = importlib.import_module('${MODULE}'); \
getattr(mod, '${FUNC}')()"
else
  # Otherwise treat PROCEDURE as a script path under /work
  TARGET="/work/${PROC}"
  if [[ ! -f "$TARGET" ]]; then
    echo "ERROR: Script not found: $TARGET"
    exit 1
  fi
  echo "Starting debugpy on ${HOST}:${PORT} and waiting for IDE: ${WAIT}"
  exec python -m debugpy --listen "${HOST}:${PORT}" ${WAIT_FLAG} "$TARGET"
fi
