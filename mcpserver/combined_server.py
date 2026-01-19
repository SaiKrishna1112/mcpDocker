#!/usr/bin/env python3
"""
Combined server that runs both MCP server and web server simultaneously
"""

import threading
import time
import os
import uvicorn
from fastapi import FastAPI
from fastapi.responses import PlainTextResponse

# Import the MCP server
from server import mcp

# Create FastAPI web server
web_app = FastAPI()

@web_app.get("/.well-known/openai-apps-challenge")
async def openai_apps_challenge():
    """Serve OpenAI apps challenge token"""
    return PlainTextResponse("lCG1ME4nDMF4SQ5WN34e_mRcJ2671QubLKki1faFH8o")

@web_app.get("/")
async def root():
    """Root endpoint"""
    return {"message": "OxyLoans Combined Server", "mcp_status": "running", "web_status": "running"}

@web_app.get("/health")
async def health():
    """Health check endpoint"""
    return {"status": "healthy", "servers": ["mcp", "web"]}

def run_mcp_server():
    """Run MCP server in a separate thread"""
    print("🔧 Starting MCP Server on SSE transport...")
    mcp.run(transport="sse", host="0.0.0.0", port=8001)

def run_web_server():
    """Run web server in main thread"""
    port = int(os.environ.get("PORT", 8002))
    print(f"🌐 Starting Web Server on port {port}")
    print(f"✅ Challenge file available at: /.well-known/openai-apps-challenge")
    uvicorn.run(web_app, host="0.0.0.0", port=port)

if __name__ == "__main__":
    print("🚀 Starting Combined Server (MCP + Web)")
    
    # Start MCP server in background thread
    mcp_thread = threading.Thread(target=run_mcp_server, daemon=True)
    mcp_thread.start()
    
    # Give MCP server time to start
    time.sleep(2)
    
    # Start web server in main thread
    run_web_server()