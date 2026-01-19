#!/usr/bin/env python3
"""
Example of standard MCP well-known endpoints
"""

from fastapi import FastAPI
from fastapi.responses import JSONResponse, PlainTextResponse

app = FastAPI()

@app.get("public/.well-known/mcp")
async def mcp_manifest():
    """MCP server manifest"""
    return JSONResponse({
        "name": "OxyLoans MCP Server",
        "version": "1.0.0",
        "description": "E-commerce MCP server with product search, cart, and order management",
        "capabilities": {
            "tools": True,
            "resources": False,
            "prompts": False
        },
        "endpoints": {
            "sse": "/sse",
            "websocket": "/ws"
        }
    })

@app.get("public/.well-known/openai-apps-challenge")
async def openai_challenge():
    """OpenAI verification token"""
    return PlainTextResponse("lCG1ME4nDMF4SQ5WN34e_mRcJ2671QubLKki1faFH8o")

@app.get("/health")
async def health():
    """Health check"""
    return {"status": "healthy", "server": "mcp"}