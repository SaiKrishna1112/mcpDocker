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
        from fastapi import FastAPI, Request
        from mcp.server.sse import SseServerTransport
        import uvicorn
        import asyncio

        # Start scheduler in background
        from scheduler import start_scheduler_thread
        start_scheduler_thread(interval_minutes=10)

        # Create a unified app
        unified_app = FastAPI()

        # Include Web Server routes
        unified_app.include_router(web_app.router)

        # Implementation of MCP SSE Transport
        # We manually expose the SSE and Message endpoints to ensure they work correctly
        sse_transport = SseServerTransport("/mcp/messages")

        @unified_app.get("/mcp/sse")
        async def handle_sse(request: Request):
            async with sse_transport.connect_sse(request.scope, request.receive, request._send) as streams:
                await mcp._mcp_server.run(
                    streams[0], 
                    streams[1], 
                    mcp._mcp_server.create_initialization_options()
                )

        @unified_app.post("/mcp/messages")
        async def handle_messages(request: Request):
            await sse_transport.handle_post_message(request.scope, request.receive, request._send)

        @unified_app.get("/sse")
        async def redirect_sse():
             """Helper to redirect legacy /sse to /mcp/sse"""
             from starlette.responses import RedirectResponse
             return RedirectResponse(url="/mcp/sse")

        # Run the unified server
        port = int(os.environ.get("PORT", 8001))
        print(f"✅ Unified Server running on port {port}")
        print(f"   - Web Interface: http://0.0.0.0:{port}/")
        print(f"   - MCP SSE Endpoint: http://0.0.0.0:{port}/mcp/sse")
        
        uvicorn.run(unified_app, host="0.0.0.0", port=port)
    
    else:
        print(f"❌ Unknown SERVER_MODE: {server_mode}")
        print("Available modes: web, mcp, both")
        sys.exit(1)

if __name__ == "__main__":
    main()