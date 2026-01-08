import asyncio
from mcp import ClientSession
from mcp.client.sse import sse_client

"""
Make sure:
1. The server is running before running this script.
2. The server is configured to use SSE transport.
3. The server is listening on port 8000.

To run the server:
uv run server.py
"""


async def main():
    # Connect to the server using SSE
    async with sse_client("http://localhost:8001/sse") as (read_stream, write_stream):
        async with ClientSession(read_stream, write_stream) as session:
            # Initialize the connection
            await session.initialize()

            # List available tools
            tools_result = await session.list_tools()
            print("Available OxyLoans API tools:")
            for tool in tools_result.tools:
                print(f"  - {tool.name}: {tool.description}")

            print("\n--- Testing OxyLoans APIs ---")
            
            # Get trending products
            products_result = await session.call_tool("get_trending_products", arguments={})
            print(f"\nTrending products: {products_result.content[0].text[:200]}...")  # Show first 200 chars
            
            # Get active offers
            offers_result = await session.call_tool("get_active_offers", arguments={})
            print(f"\nActive offers: {offers_result.content[0].text}")
            
            # Test with sample customer ID (replace with real ID)
            sample_customer_id = "12345"
            
            # Get user cart
            cart_result = await session.call_tool("get_user_cart", arguments={"customer_id": sample_customer_id})
            print(f"\nUser cart: {cart_result.content[0].text}")
            
            # Get user profile
            profile_result = await session.call_tool("get_user_profile", arguments={"user_id": sample_customer_id})
            print(f"\nUser profile: {profile_result.content[0].text}")


if __name__ == "__main__":
    asyncio.run(main())