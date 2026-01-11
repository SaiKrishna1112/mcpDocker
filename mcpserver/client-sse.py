import asyncio
from mcp.client.sse import sse_client
from mcp import ClientSession


MCP_SSE_URL = "http://localhost:8001/sse"
# For Render, replace with:
# MCP_SSE_URL = "https://<your-render-service>.onrender.com/sse"


async def main():
    print("Connecting to MCP server via SSE...")

    async with sse_client(MCP_SSE_URL) as (read, write):
        async with ClientSession(read, write) as session:
            # Initialize MCP session
            await session.initialize()
            print("MCP session initialized\n")

            # -----------------------------
            # List available tools
            # -----------------------------
            tools_response = await session.list_tools()

            print("Available tools:")
            for tool in tools_response.tools:
                print(f"- {tool.name}")
            print()

            # -----------------------------
            # Example: Call get_active_offers
            # -----------------------------
            print("Calling get_active_offers...")
            offers = await session.call_tool(
                "get_active_offers",
                {}
            )
            print("Active Offers Response:")
            print(offers.content)
            print()

            # -----------------------------
            # Example: Call get_trending_products
            # -----------------------------
            print("Calling get_trending_products...")
            products = await session.call_tool(
                "get_trending_products",
                {}
            )

            print("Trending Products (preview):")
            if products.content:
                print(products.content[:1])
            else:
                print("No products returned")


if __name__ == "__main__":
    asyncio.run(main())
