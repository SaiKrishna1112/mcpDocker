@echo off
echo Starting MCP Server for Development...
echo.
echo Available commands:
echo   dev-web     - Run web server only (port 8001)
echo   dev-mcp     - Run MCP server only (port 8001) 
echo   dev-both    - Run both servers (web:8001, mcp:8002)
echo.

if "%1"=="dev-web" (
    echo Starting Web Server on port 8001...
    set SERVER_MODE=web
    python start.py
) else if "%1"=="dev-mcp" (
    echo Starting MCP Server on port 8001...
    set SERVER_MODE=mcp
    python start.py
) else if "%1"=="dev-both" (
    echo Starting Both Servers (Web:8001, MCP:8002)...
    set SERVER_MODE=both
    python start.py
) else (
    echo Usage: dev.bat [dev-web^|dev-mcp^|dev-both]
    echo.
    echo Examples:
    echo   dev.bat dev-web    # For OpenAI verification
    echo   dev.bat dev-mcp    # For MCP client testing
    echo   dev.bat dev-both   # For full development
)