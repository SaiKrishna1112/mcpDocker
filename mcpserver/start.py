#!/usr/bin/env python3
"""
Flexible server starter - runs web server for production, MCP server for development
"""

import os
import sys

def main():
    # Check if we're in production (Render) or development
    server_mode = os.environ.get("SERVER_MODE", "web")
    
    if server_mode == "web":
        print("🌐 Starting in WEB mode (for OpenAI verification)")
        from web_server import app
        import uvicorn
        
        # Start scheduler in background
        from scheduler import start_scheduler_thread
        start_scheduler_thread(interval_minutes=10)
        
        port = int(os.environ.get("PORT", 8001))
        uvicorn.run(app, host="0.0.0.0", port=port)
        
    elif server_mode == "mcp":
        print("🔧 Starting in MCP mode")
        from server import mcp
        mcp.run(transport="sse", host="0.0.0.0", port=8001)
        
    elif server_mode == "both":
        print("🚀 Starting BOTH servers in UNIFIED mode")
        from server import mcp
        from web_server import app as web_app
        from starlette.applications import Starlette
        from starlette.routing import Mount
        import uvicorn

        # Start scheduler in background
        from scheduler import start_scheduler_thread
        start_scheduler_thread(interval_minutes=10)

        # Use a bare Starlette router so web_app middleware doesn't intercept MCP ASGI messages
        mcp_asgi = mcp.http_app(transport="sse")
        root_app = Starlette(routes=[
            Mount("/mcp", app=mcp_asgi),
            Mount("/", app=web_app),
        ])

        port = int(os.environ.get("PORT", 8001))
        print(f"✅ Unified Server running on port {port}")
        print(f"   - Web Interface: http://0.0.0.0:{port}/")
        print(f"   - MCP SSE Endpoint: http://0.0.0.0:{port}/mcp/sse")

        uvicorn.run(root_app, host="0.0.0.0", port=port)
    
    else:
        print(f"❌ Unknown SERVER_MODE: {server_mode}")
        print("Available modes: web, mcp, both")
        sys.exit(1)

if __name__ == "__main__":
    main()