from mcp.server.fastmcp import FastMCP

mcp = FastMCP(name="askoxy-api")

@mcp.tool()
async def hello_world() -> str:
    """Health check – verify MCP server is reachable."""
    return "askoxy.ai MCP Server is running!"

if __name__ == "__main__":
    print("✅ MCP Server running on http://localhost:8001/sse")
    mcp.run(transport="sse")
