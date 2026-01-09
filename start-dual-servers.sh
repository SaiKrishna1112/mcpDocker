#!/bin/bash

# Install required dependencies
pip install fastapi uvicorn

echo "Starting dual server setup..."

# Start MCP server in background
echo "Starting MCP server on port 8001..."
uv run mcpserver/server.py &
MCP_PID=$!

# Wait a moment for MCP server to start
sleep 2

# Start REST API server for ChatGPT
echo "Starting REST API server on port 3000..."
uv run chatgpt-api.py &
API_PID=$!

echo "Both servers running:"
echo "- MCP Server: http://localhost:8001 (for OpenAI API)"
echo "- REST API: http://localhost:3000 (for ChatGPT web)"
echo "- API Docs: http://localhost:3000/docs"

# Wait for user input to stop
read -p "Press Enter to stop both servers..."

# Kill both processes
kill $MCP_PID $API_PID
echo "Servers stopped."