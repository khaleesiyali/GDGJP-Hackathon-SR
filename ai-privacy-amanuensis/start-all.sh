#!/bin/bash

# AI Privacy Amanuensis - Complete Startup Script
# Starts: Frontend (Next.js) + Backend API (FastAPI) + Vision Agent (LiveKit)

set -e

PROJECT_DIR="/Users/y4l1/Documents/GDGJP-Hackathon/ai-privacy-amanuensis"
BACKEND_DIR="$PROJECT_DIR/backend"

echo "🚀 Starting AI Privacy Amanuensis System..."
echo "=========================================="
echo ""

# Kill any existing processes
echo "🛑 Cleaning up any existing processes..."
pkill -f "npm run dev|next dev|uvicorn|Vision.py" 2>/dev/null || true
sleep 2

# Start Backend API Server
echo "📡 Starting Backend API Server on port 8000..."
cd "$BACKEND_DIR"
uv run uvicorn server:app --reload --host 0.0.0.0 --port 8000 &
BACKEND_PID=$!
echo "   Backend PID: $BACKEND_PID"
sleep 3

# Start Frontend 
echo "🎨 Starting Frontend (Next.js) on port 3001..."
cd "$PROJECT_DIR"
npm run dev &
FRONTEND_PID=$!
echo "   Frontend PID: $FRONTEND_PID"
sleep 5

# Start Vision Agent
echo "🧠 Starting Vision Agent (LiveKit)..."
cd "$BACKEND_DIR"
uv run python Vision.py dev &
AGENT_PID=$!
echo "   Agent PID: $AGENT_PID"

echo ""
echo "=========================================="
echo "✅ All systems started!"
echo "=========================================="
echo ""
echo "📱 Frontend:     http://localhost:3001"
echo "📡 Backend API:  http://localhost:8000"
echo "🧠 Vision Agent: Connected to LiveKit"
echo ""
echo "🌐 Form Page:    http://localhost:3001/form"
echo ""
echo "Press Ctrl+C to stop all services"
echo ""

# Wait for any process to exit
wait
