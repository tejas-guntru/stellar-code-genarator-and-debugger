#!/bin/bash

# Start the backend Flask server
echo "Starting Flask backend..."
cd backend
python app.py &

# Start the frontend Vite server
echo "Starting React frontend..."
cd ..
npm run dev

# Trap to kill both processes when script is stopped
trap "trap - SIGTERM && kill -- -$$" SIGINT SIGTERM EXIT
