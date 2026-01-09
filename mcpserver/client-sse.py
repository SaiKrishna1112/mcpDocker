import asyncio
from mcp.client.sse import sse_client
from mcp import ClientSession


async def main():
    async with sse_client("http://localhost:8001/sse") as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()

            tools = await session.list_tools()
            print("\nAvailable tools:")
            for tool in tools.tools:
                print(f"- {tool.name}")

            offers = await session.call_tool("get_active_offers", {})
            print("\nActive Offers:")
            print(offers.content)

            products = await session.call_tool("get_trending_products", {})
            print("\nTrending Products:")
            print(products.content[:1])  # preview


if __name__ == "__main__":
    asyncio.run(main())
