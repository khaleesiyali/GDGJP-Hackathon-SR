#!/bin/bash

# Start only the Backend API + Vision Agent (no frontend)
# Useful if frontend is already running

set -e

BACKEND_DIR="/Users/y4l1/Documents/GDGJP-Hackathon/ai-privacy-amanuensis/backend"

echo "🚀 Starting Backend + Vision Agent..."
echo "======================================"

# Kill existing processes
pkill -f "uvicorn|Vision.py" 2>/dev/null || true
sleep 2

# Start Backend API
echo "📡 Starting FastAPI server on port 8000..."
cd "$BACKEND_DIR"
uv run uvicorn server:app --reload --host 0.0.0.0 --port 8000 &
sleep 2

# Start Vision Agent
echo "🧠 Starting Vision Agent..."
uv run python Vision.py dev &

echo ""
echo "✅ Backend and Agent started!"
echo "📡 API: http://localhost:8000"
echo ""
echo "Press Ctrl+C to stop"
sleep 2
wait
