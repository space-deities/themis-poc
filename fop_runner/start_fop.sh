#!/usr/bin/env bash
set -euo pipefail

print_usage() {
  cat <<'USAGE'
Usage:
  start_fop.sh [--id <uuid>] [--background|--blocking] [--external-port <N>] <python-script-or-module> [extra docker compose run options...]

Examples:
  start_fop.sh fop.py
  start_fop.sh tools/myfop.py --no-build
  start_fop.sh --id 123e4567-e89b-12d3-a456-426614174000 mypkg.worker:main --background --external-port 0 --no-build
  start_fop.sh mypkg.worker:main --external-port 5679

Flags:
  --external-port N
      N > 0  -> expose container DEBUGPY_PORT on host port N
      N = 0  -> expose container DEBUGPY_PORT on a random host port
      (omit) -> do not expose the debug port
  --background | --blocking
      Run detached (background) or attached (blocking). Default: blocking.

Notes:
  - Internal debug port defaults to 5678. Override by exporting DEBUGPY_PORT, e.g.:
        DEBUGPY_PORT=9000 ./start_fop.sh myfop.py --external-port 0
  - All current env vars are forwarded into the container (except PROCEDURE and INSTANCE_ID).
  - The container will be named: fop-runner-<id>
  - Raw docker compose flags still pass through (e.g., --detach/-d, --no-build).
USAGE
}

INSTANCE_ID=""
PROCEDURE=""
EXTRA_ARGS=()
ENV_ARGS=()
BACKGROUND=false              # default attached
EXTERNAL_PORT_SPEC=""         # "", "0", or a positive integer
DEBUGPY_PORT_DEFAULT=5678

# Args handling
while [[ $# -gt 0 ]]; do
  case "$1" in
    -h|--help)
      print_usage; exit 0 ;;
    -i|--id)
      [[ $# -ge 2 ]] || { echo "Error: --id requires a value" >&2; exit 1; }
      INSTANCE_ID="$2"; shift 2 ;;
    --background)
      BACKGROUND=true; shift ;;
    --blocking)
      BACKGROUND=false; shift ;;
    --external-port)
      [[ $# -ge 2 ]] || { echo "Error: --external-port requires a value" >&2; exit 1; }
      EXTERNAL_PORT_SPEC="$2"; shift 2 ;;
    --) shift; EXTRA_ARGS+=("$@"); break ;;
    --*) EXTRA_ARGS+=("$1"); shift ;;        # pass through compose run options
    -*)
      EXTRA_ARGS+=("$1"); shift ;;
    *)
      if [[ -z "$PROCEDURE" ]]; then
        PROCEDURE="$1"; shift
      else
        # anything after the procedure that doesn't start with '-' is ambiguous;
        # if you really need to pass a COMMAND to the service, add it after '--'
        EXTRA_ARGS+=("$1"); shift
      fi
      ;;
  esac
done

if [[ -z "$PROCEDURE" ]]; then
  echo "Error: missing <python-script-or-module>" >&2
  print_usage
  exit 1
fi

# ---- ensure/generate UUID ----
if [[ -z "$INSTANCE_ID" ]]; then
  if command -v uuidgen >/dev/null 2>&1; then
    INSTANCE_ID="$(uuidgen)"
  elif [[ -r /proc/sys/kernel/random/uuid ]]; then
    INSTANCE_ID="$(cat /proc/sys/kernel/random/uuid)"
  elif command -v python3 >/dev/null 2>&1; then
    INSTANCE_ID="$(python3 - <<'PY'
import uuid; print(uuid.uuid4())
PY
)"
  else
    echo "Error: could not generate UUID (need uuidgen, /proc uuid, or python3)" >&2
    exit 1
  fi
fi

CONTAINER_NAME="fop-runner-${INSTANCE_ID}"

# ---- pass-through env (exclude PROCEDURE / INSTANCE_ID) ----
while IFS= read -r line; do
  [[ -z "$line" ]] && continue
  case "$line" in
    BASH_FUNC_*|_=*) continue ;;
  esac
  key="${line%%=*}"
  val="${line#*=}"
  [[ "$key" == "PROCEDURE" || "$key" == "INSTANCE_ID" ]] && continue
  ENV_ARGS+=("-e" "${key}=${val}")
done < <(env)

# Determine internal debug port from env (fallback to default)
_DEBUGPY_PORT="${DEBUGPY_PORT:-$DEBUGPY_PORT_DEFAULT}"

# Explicit overrides
ENV_ARGS+=(-e "PROCEDURE=${PROCEDURE}")
ENV_ARGS+=(-e "INSTANCE_ID=${INSTANCE_ID}")
ENV_ARGS+=(-e "DEBUGPY_PORT=${_DEBUGPY_PORT}")

# ---- docker compose args ----
DOCKER_ARGS=(
  --rm
  --build
  --name "${CONTAINER_NAME}"
)

# Background / attached
$BACKGROUND && DOCKER_ARGS+=(-d)

# External port mapping logic (only map if user asked)
# docker compose run --publish syntax mirrors docker run:
#   --publish "hostPort:containerPort"
#   --publish "containerPort"            # random host port
if [[ -n "${EXTERNAL_PORT_SPEC}" ]]; then
  if [[ "${EXTERNAL_PORT_SPEC}" == "0" ]]; then
    # Random host port for the container port
    DOCKER_ARGS+=( --publish "${_DEBUGPY_PORT}" )
  else
    # Validate numeric > 0
    if ! [[ "${EXTERNAL_PORT_SPEC}" =~ ^[0-9]+$ ]] || [[ "${EXTERNAL_PORT_SPEC}" -le 0 ]]; then
      echo "Error: --external-port must be 0 or a positive integer" >&2
      exit 1
    fi
    DOCKER_ARGS+=( --publish "${EXTERNAL_PORT_SPEC}:${_DEBUGPY_PORT}" )
  fi
fi

# ---- run the container ----
# IMPORTANT: docker compose run OPTIONS must come BEFORE the service name.
docker compose run \
  "${DOCKER_ARGS[@]}" \
  ${EXTRA_ARGS[@]+"${EXTRA_ARGS[@]}"} \
  "${ENV_ARGS[@]}" \
  pydebug

echo "Started container: ${CONTAINER_NAME}"
echo "Instance ID: ${INSTANCE_ID}"

if [[ -n "${EXTERNAL_PORT_SPEC}" ]]; then
  if [[ "${EXTERNAL_PORT_SPEC}" == "0" ]]; then
    # Try to resolve the actual random host port (works when detached)
    if $BACKGROUND; then
      # Query the mapped port; try tcp first, then no /proto
      if MAP=$(docker port "${CONTAINER_NAME}" "${_DEBUGPY_PORT}/tcp" 2>/dev/null | head -n1; true); then
        if [[ -n "$MAP" ]]; then
          echo "Debug port published at: ${MAP}"
        else
          # Fallback try without /tcp (older engines)
          if MAP=$(docker port "${CONTAINER_NAME}" "${_DEBUGPY_PORT}" 2>/dev/null | head -n1; true); then
            [[ -n "$MAP" ]] && echo "Debug port published at: ${MAP}"
          fi
        fi
      fi
    else
      echo "(random host port chosen; cannot display while attached)"
    fi
  else
    echo "Debug port published: host ${EXTERNAL_PORT_SPEC} -> container ${_DEBUGPY_PORT}"
  fi
else
  echo "No debug port exposed."
fi

$BACKGROUND && echo "(running in background; follow logs with: docker logs -f ${CONTAINER_NAME})"
