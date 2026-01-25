#!/bin/bash

# Run the 1000 Soccer Players app locally

# Get the directory where the script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

echo "Starting 1000 Soccer Players..."
echo ""

# Check if virtual environment exists, create if not
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
    source venv/bin/activate
    echo "Installing dependencies..."
    pip install -r backend/requirements.txt
    echo ""
else
    source venv/bin/activate
fi

# Check if backend data exists
if [ ! -f "backend/data/players.db" ]; then
    echo "No player database found. Running sample data extraction..."
    echo "(For full data, run: python backend/scripts/extract_wikidata.py)"
    echo ""
    python3 backend/scripts/extract_sample.py
    echo ""
fi

# Start backend
echo "Starting backend server on http://localhost:8000..."
cd backend
python3 -m uvicorn app.main:app --host 0.0.0.0 --port 8000 &
BACKEND_PID=$!
cd ..

sleep 3

# Check if backend started
if ! curl -s http://localhost:8000/health > /dev/null 2>&1; then
    echo "ERROR: Backend failed to start. Check if port 8000 is in use."
    kill $BACKEND_PID 2>/dev/null
    exit 1
fi
echo "Backend started successfully!"

# Start frontend server
echo "Starting frontend server on http://localhost:3000..."
cd frontend
python3 -m http.server 3000 &
FRONTEND_PID=$!
cd ..

echo ""
echo "================================================"
echo "App is running!"
echo ""
echo "  Frontend: http://localhost:3000"
echo "  Backend:  http://localhost:8000"
echo "  API Docs: http://localhost:8000/docs"
echo ""
echo "Press Ctrl+C to stop both servers"
echo "================================================"

# Handle shutdown
trap "kill $BACKEND_PID $FRONTEND_PID 2>/dev/null; exit" INT TERM

# Wait
wait
