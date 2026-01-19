#!/bin/bash

# Development server manager
echo "🚀 OxyLoans MCP Server Manager"
echo "=============================="

case "$1" in
  "web")
    echo "🌐 Starting Web Server (OpenAI verification)"
    export SERVER_MODE=web
    uv run python start.py
    ;;
  "mcp")
    echo "🔧 Starting MCP Server"
    export SERVER_MODE=mcp
    uv run python start.py
    ;;
  "both")
    echo "🚀 Starting Both Servers"
    export SERVER_MODE=both
    uv run python start.py
    ;;
  "docker")
    echo "🐳 Starting Docker Container"
    docker build -t mcpserver .
    docker run --rm -p 8001:8001 -p 8002:8002 mcpserver
    ;;
  *)
    echo "Usage: $0 {web|mcp|both|docker}"
    echo ""
    echo "  web   - Start web server only (port 8002)"
    echo "  mcp   - Start MCP server only (port 8001)"
    echo "  both  - Start both servers"
    echo "  docker- Start in Docker with both ports"
    exit 1
    ;;
esac