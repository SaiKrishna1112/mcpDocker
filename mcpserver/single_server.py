#!/usr/bin/env python3
"""
Single server approach - Embed web routes directly in FastMCP
"""

from fastmcp import FastMCP
from fastapi.responses import PlainTextResponse
import os

# Create unified MCP server
mcp = FastMCP(name="oxyloans-unified")

# Add web endpoints directly to FastMCP
@mcp.get("/.well-known/openai-apps-challenge")
async def openai_challenge():
    return PlainTextResponse("lCG1ME4nDMF4SQ5WN34e_mRcJ2671QubLKki1faFH8o")

@mcp.get("/")
async def root():
    return {"message": "OxyLoans Unified Server", "status": "running"}

@mcp.get("/health")
async def health():
    return {"status": "healthy"}

# Import all existing MCP tools
import auth.login as login
import auth.register as register
import auth.verify as verify
import auth.simple_login as simple_login
login.register_tools(mcp)
register.register_tools(mcp)
verify.register_tools(mcp)
simple_login.register_tools(mcp)

import products.search as search
import products.public as public
import products.images as images
import products.combo as combo
search.register_tools(mcp)
public.register_tools(mcp)
images.register_tools(mcp)
combo.register_tools(mcp)

import user.profile as profile
import user.address as address
profile.register_tools(mcp)
address.register_tools(mcp)

import cart.add as cart_add
import cart.view as cart_view
import cart.decrement as cart_decrement
import cart.remove as cart_remove
cart_add.register_tools(mcp)
cart_view.register_tools(mcp)
cart_decrement.register_tools(mcp)
cart_remove.register_tools(mcp)

import orders.validation as order_validation
import orders.management as order_management
import orders.checkout as order_checkout
order_validation.register_tools(mcp)
order_management.register_tools(mcp)
order_checkout.register_tools(mcp)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    print(f"🚀 Starting unified server on port {port}")
    print(f"✅ MCP tools: Available")
    print(f"✅ Web endpoints: /.well-known/openai-apps-challenge")
    mcp.run(transport="sse", host="0.0.0.0", port=port)