from mcp.server.fastmcp import FastMCP

mcp = FastMCP(name="oxyloans-api")

@mcp.tool()
async def test_tool():
    """Test tool to verify server is working"""
    return {"status": "Server is running"}

if __name__ == "__main__":
    print("✅ MCP Server running")
    mcp.run(transport="sse")