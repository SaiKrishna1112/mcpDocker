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
        port = int(os.environ.get("PORT", 8001))
        uvicorn.run(app, host="0.0.0.0", port=port)
        
    elif server_mode == "mcp":
        print("🔧 Starting in MCP mode")
        from server import mcp
        mcp.run(transport="sse", host="0.0.0.0", port=8001)
        
    elif server_mode == "both":
        print("🚀 Starting BOTH servers")
        import threading
        import time
        
        def run_mcp():
            from server import mcp
            mcp.run(transport="sse", host="0.0.0.0", port=8001)
        
        def run_web():
            from web_server import app
            import uvicorn
            port = int(os.environ.get("PORT", 8002))
            uvicorn.run(app, host="0.0.0.0", port=port)
        
        # Start MCP in background
        mcp_thread = threading.Thread(target=run_mcp, daemon=True)
        mcp_thread.start()
        time.sleep(2)
        
        # Start web in foreground
        run_web()
    
    else:
        print(f"❌ Unknown SERVER_MODE: {server_mode}")
        print("Available modes: web, mcp, both")
        sys.exit(1)

if __name__ == "__main__":
    main()