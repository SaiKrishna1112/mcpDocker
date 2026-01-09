@echo off
echo Starting dual server setup...

echo Starting MCP server on port 8001...
start "MCP Server" uv run mcpserver/server.py

timeout /t 3 /nobreak > nul

echo Starting REST API server on port 3000...
start "REST API" uv run chatgpt-api.py

echo Both servers running:
echo - MCP Server: http://localhost:8001 (for OpenAI API)
echo - REST API: http://localhost:3000 (for ChatGPT web)
echo - API Docs: http://localhost:3000/docs

pause