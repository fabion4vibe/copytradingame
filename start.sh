#!/usr/bin/env bash
# Trading Platform Simulator — Start Script
# Avvia backend e frontend in parallelo

set -e

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "=== Trading Platform Simulator ==="

# Backend
echo "[1/2] Avvio backend (FastAPI)..."
cd "$ROOT/backend"
if [ ! -d ".venv" ]; then
  python -m venv .venv
  source .venv/bin/activate
  pip install fastapi "uvicorn[standard]" numpy pydantic
else
  source .venv/bin/activate
fi
uvicorn main:app --reload --port 8000 &
BACKEND_PID=$!

# Frontend
echo "[2/2] Avvio frontend (Vite)..."
cd "$ROOT/frontend"
if [ ! -d "node_modules" ]; then
  npm install
fi
npm run dev &
FRONTEND_PID=$!

echo ""
echo "Backend:  http://localhost:8000"
echo "Frontend: http://localhost:5173"
echo "API docs: http://localhost:8000/docs"
echo ""
echo "Premi Ctrl+C per fermare entrambi."

trap "kill $BACKEND_PID $FRONTEND_PID 2>/dev/null; exit 0" INT TERM
wait
