#!/usr/bin/env bash
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
BACKEND_DIR="$REPO_ROOT/backend"
FRONTEND_DIR="$REPO_ROOT/frontend"
COMPOSE_FILE="$REPO_ROOT/infrastructure/docker/docker-compose.yml"
BACKEND_PORT=8000
FRONTEND_PORT=3000

# IMPORTANT: Docker Compose volume names depend on the *project name*.
# To keep DB data persistent across sessions (and regardless of where you run the script from),
# we pin a stable project name here.
COMPOSE_PROJECT_NAME="${COMPOSE_PROJECT_NAME:-aaim_proj}"

dc() {
  docker compose -p "$COMPOSE_PROJECT_NAME" -f "$COMPOSE_FILE" "$@"
}

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
expected_pg_vol="${COMPOSE_PROJECT_NAME}_postgres_data"
expected_redis_vol="${COMPOSE_PROJECT_NAME}_redis_data"

# docker-compose.yml uses fixed container_name values (ragify-db/ragify-redis).
# If these containers already exist but are attached to a different compose project's volumes,
# the app may appear to have "lost" data. In that case, recreate ONLY the containers so the
# correct persistent volumes are re-attached (we do NOT remove volumes).
existing_pg_vol="$(docker inspect ragify-db --format '{{range .Mounts}}{{if eq .Destination "/var/lib/postgresql/data"}}{{.Name}}{{end}}{{end}}' 2>/dev/null || true)"
existing_redis_vol="$(docker inspect ragify-redis --format '{{range .Mounts}}{{if eq .Destination "/data"}}{{.Name}}{{end}}{{end}}' 2>/dev/null || true)"

if [ -n "$existing_pg_vol" ] && [ "$existing_pg_vol" != "$expected_pg_vol" ]; then
  echo "⚠️  ragify-db is attached to volume '$existing_pg_vol' (expected '$expected_pg_vol')."
  echo "    Recreating containers to re-attach persistent data volume (no volume deletion)."
  docker rm -f ragify-db >/dev/null 2>&1 || true
fi
if [ -n "$existing_redis_vol" ] && [ "$existing_redis_vol" != "$expected_redis_vol" ]; then
  docker rm -f ragify-redis >/dev/null 2>&1 || true
fi

dc up -d db redis

# macOS doesn't include `timeout` by default; use a portable wait loop.
echo "    (waiting for DB...)"
deadline=$((SECONDS + 30))
until dc exec -T db pg_isready -U ragify >/dev/null 2>&1; do
  if [ "$SECONDS" -ge "$deadline" ]; then
    echo "❌  DB did not become ready within 30s"
    dc logs --no-color db | tail -n 80 || true
    exit 1
  fi
  sleep 1
done
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
