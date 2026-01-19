#!/usr/bin/env python3
"""
Unified server - FastMCP + FastAPI on single port for Render deployment
"""

from fastmcp import FastMCP
from fastapi import FastAPI
from fastapi.responses import PlainTextResponse
import threading
import uvicorn
import os

# Create FastMCP instance
mcp = FastMCP(name="oxyloans-api")

# Create FastAPI app for web endpoints
web_app = FastAPI(title="OxyLoans Web Server")

@web_app.get("/.well-known/openai-apps-challenge")
async def openai_challenge():
    return PlainTextResponse("lCG1ME4nDMF4SQ5WN34e_mRcJ2671QubLKki1faFH8o")

@web_app.get("/")
async def root():
    return {"message": "OxyLoans Unified Server", "mcp": "running", "web": "running"}

@web_app.get("/health")
async def health():
    return {"status": "healthy", "services": ["mcp", "web"]}

# Import all MCP tools
from server import mcp as configured_mcp

def run_mcp_server():
    """Run MCP server in background thread"""
    configured_mcp.run(transport="sse", host="0.0.0.0", port=8001)

def main():
    port = int(os.environ.get("PORT", 8000))
    
    # Start MCP server in background
    mcp_thread = threading.Thread(target=run_mcp_server, daemon=True)
    mcp_thread.start()
    
    # Start web server on main thread
    uvicorn.run(web_app, host="0.0.0.0", port=port)

if __name__ == "__main__":
    main()