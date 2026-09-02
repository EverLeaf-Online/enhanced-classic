#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
QA_DIR="$ROOT/deploy/qa"
ENV_FILE="$QA_DIR/.env.qa"
COMPOSE_FILE="$QA_DIR/docker-compose.qa.yml"

if [[ ! -f "$ENV_FILE" ]]; then
  echo "Missing $ENV_FILE. Copy .env.qa.example and set a random QA DB password." >&2
  exit 2
fi

cmd="${1:-status}"
shift || true

compose=(docker compose --env-file "$ENV_FILE" -f "$COMPOSE_FILE" -p everleaf-qa)

case "$cmd" in
  up)
    "${compose[@]}" up -d --build
    ;;
  down)
    "${compose[@]}" down
    ;;
  reset)
    if [[ "${EVERLEAF_QA_RESET:-}" != "I_UNDERSTAND_QA_DATA_WILL_BE_DELETED" ]]; then
      echo "Refusing reset. Export EVERLEAF_QA_RESET=I_UNDERSTAND_QA_DATA_WILL_BE_DELETED" >&2
      exit 3
    fi
    "${compose[@]}" down -v
    ;;
  status)
    "${compose[@]}" ps
    ;;
  logs)
    "${compose[@]}" logs --tail=200 "$@"
    ;;
  ports)
    "${compose[@]}" port qa-game 8484
    for p in 7575 7576 7577 7578 7579 7580 7581 7582; do "${compose[@]}" port qa-game "$p"; done
    ;;
  *)
    echo "Usage: $0 {up|down|reset|status|logs|ports}" >&2
    exit 2
    ;;
esac
