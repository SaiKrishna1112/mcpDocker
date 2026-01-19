@echo off
echo 🚀 OxyLoans MCP Server Manager
echo ==============================

if "%1"=="web" (
    echo 🌐 Starting Web Server (OpenAI verification)
    set SERVER_MODE=web
    uv run python start.py
) else if "%1"=="mcp" (
    echo 🔧 Starting MCP Server
    set SERVER_MODE=mcp
    uv run python start.py
) else if "%1"=="both" (
    echo 🚀 Starting Both Servers
    set SERVER_MODE=both
    uv run python start.py
) else if "%1"=="docker" (
    echo 🐳 Starting Docker Container
    docker build -t mcpserver .
    docker run --rm -p 8001:8001 -p 8002:8002 mcpserver
) else (
    echo Usage: %0 {web^|mcp^|both^|docker}
    echo.
    echo   web   - Start web server only (port 8002)
    echo   mcp   - Start MCP server only (port 8001)
    echo   both  - Start both servers
    echo   docker- Start in Docker with both ports
    exit /b 1
)