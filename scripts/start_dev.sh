#!/usr/bin/env bash
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
BACKEND_DIR="$REPO_ROOT/backend"
FRONTEND_DIR="$REPO_ROOT/frontend"
COMPOSE_FILE="$REPO_ROOT/infrastructure/docker/docker-compose.yml"
BACKEND_PORT=8000
FRONTEND_PORT=3000

port_in_use() { lsof -i:"$1" >/dev/null 2>&1; }

kill_port() {
  local port=$1
  if port_in_use "$port"; then
    echo "⚠️  Port $port in use — freeing..."
    lsof -ti :"$port" | xargs kill -9 2>/dev/null || true
    sleep 1
  fi
}

cleanup() {
  echo ""
  echo "🛑  Shutting down..."
  [ -n "${BACKEND_PID:-}" ] && { pkill -P "$BACKEND_PID" 2>/dev/null; kill "$BACKEND_PID" 2>/dev/null; } || true
  [ -n "${FRONTEND_PID:-}" ] && { pkill -P "$FRONTEND_PID" 2>/dev/null; kill "$FRONTEND_PID" 2>/dev/null; } || true
  exit 0
}
trap cleanup SIGINT SIGTERM

if [ ! -f "$REPO_ROOT/.env" ]; then
  echo "❌  .env not found. Run: cp .env.example .env"
  exit 1
fi

echo "🐳  Starting infrastructure..."
docker compose -f "$COMPOSE_FILE" up -d db redis
timeout 30 bash -c "until docker compose -f '$COMPOSE_FILE' exec db pg_isready -U ragify >/dev/null 2>&1; do sleep 1; done"
echo "    ✓  DB ready"

echo "🐍  Starting backend..."
kill_port "$BACKEND_PORT"
(
  cd "$BACKEND_DIR"
  source venv/bin/activate
  alembic upgrade head
  uvicorn app.main:app --reload --host 127.0.0.1 --port "$BACKEND_PORT" 2>&1 | tee backend.log
) &
BACKEND_PID=$!

echo "⚛️   Starting frontend..."
kill_port "$FRONTEND_PORT"
(
  cd "$FRONTEND_DIR"
  npm run dev 2>&1 | tee frontend.log
) &
FRONTEND_PID=$!

echo ""
echo "✅  Running:"
echo "    Frontend  →  http://localhost:$FRONTEND_PORT"
echo "    Backend   →  http://localhost:$BACKEND_PORT"
echo "    API docs  →  http://localhost:$BACKEND_PORT/docs"
echo ""
echo "Ctrl+C to stop."
wait "$BACKEND_PID" "$FRONTEND_PID"
