#!/bin/bash

# Quick Start Script for Quantum Slot Machine Demo
# This script starts both backend and frontend servers

echo "🚀 Starting Quantum Slot Machine Demo"
echo ""

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Error: Python 3 is not installed"
    exit 1
fi

# Check if Node.js is installed
if ! command -v node &> /dev/null; then
    echo "❌ Error: Node.js is not installed"
    exit 1
fi

# Start backend in background
echo "📡 Starting backend server (FastAPI + Qiskit)..."
cd backend
python3 main.py &
BACKEND_PID=$!
cd ..

# Wait for backend to start
sleep 3

# Check if backend is running
if curl -s http://localhost:8000/ > /dev/null; then
    echo "✅ Backend running on http://localhost:8000"
else
    echo "❌ Backend failed to start"
    kill $BACKEND_PID 2>/dev/null
    exit 1
fi

# Start frontend
echo "🎨 Starting frontend server (React)..."
cd frontend
npm start &
FRONTEND_PID=$!
cd ..

echo ""
echo "✨ Quantum Slot Machine is starting!"
echo ""
echo "Backend API: http://localhost:8000"
echo "Frontend UI: http://localhost:3000"
echo ""
echo "Press Ctrl+C to stop all servers"
echo ""

# Wait for Ctrl+C
trap "echo ''; echo '🛑 Stopping servers...'; kill $BACKEND_PID $FRONTEND_PID 2>/dev/null; exit" INT
wait
