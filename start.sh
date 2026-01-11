#!/bin/bash

# --- Rates Change Playground Startup Script ---

echo "🚀 Starting US Treasury Rates Change Simulator..."

# 1. Install dependencies
echo "📦 Installing dependencies..."
/opt/anaconda3/bin/pip install -r requirements.txt -q

# 2. Cleanup existing processes (port 8081 and 3001)
echo "🧹 Cleaning up old processes..."
lsof -ti:8081 | xargs kill -9 2>/dev/null
lsof -ti:3001 | xargs kill -9 2>/dev/null

# 3. Start Backend (FastAPI)
echo "🔗 Starting Backend on port 8081..."
/opt/anaconda3/bin/python -m uvicorn backend.main:app --host 0.0.0.0 --port 8081 > backend.log 2>&1 &
BACKEND_PID=$!

# 4. Start Frontend (HTTP Server)
echo "🎨 Starting Frontend on port 3001..."
echo "📍 Access the app at: http://localhost:3001"
/opt/anaconda3/bin/python -m http.server 3001 --directory frontend > frontend.log 2>&1 &
FRONTEND_PID=$!

# 5. Handle shutdown
trap "kill $BACKEND_PID $FRONTEND_PID; echo '🛑 Servers stopped.'; exit" INT TERM
wait
