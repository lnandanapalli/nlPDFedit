#!/bin/bash
echo "Starting PDF Chat Assistant..."

# Check if virtual environment exists
if [ ! -d "backend/venv" ]; then
    echo "Creating virtual environment..."
    cd backend
    python -m venv venv
    cd ..
fi

# Activate virtual environment and install dependencies
echo "Setting up backend..."
cd backend
source venv/bin/activate  # On Windows: venv\Scripts\activate.bat
pip install -r requirements.txt

# Start backend in background
echo "Starting backend server..."
python main.py &
BACKEND_PID=$!

cd ../frontend

# Install npm dependencies if node_modules doesn't exist
if [ ! -d "node_modules" ]; then
    echo "Installing frontend dependencies..."
    npm install
fi

# Start frontend
echo "Starting frontend server..."
npm start &
FRONTEND_PID=$!

echo "PDF Chat Assistant is starting..."
echo "Backend: http://localhost:8000"
echo "Frontend: http://localhost:3000"
echo "API Docs: http://localhost:8000/docs"
echo ""
echo "Press Ctrl+C to stop both servers"

# Wait for Ctrl+C
trap "kill $BACKEND_PID $FRONTEND_PID; exit" INT
wait