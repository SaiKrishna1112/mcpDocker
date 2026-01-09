import json
import httpx
from fastmcp import FastMCP

# Create MCP server
mcp = FastMCP("OxyLoans API")

BASE_URL = "https://meta.oxyloans.com/api"

async def get_products():
    """Fetch all products from OxyLoans API"""
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(f"{BASE_URL}/product-service/showGroupItemsForCustomrs")
            return response.json()
        except:
            return []

@mcp.tool()
async def search(query: str) -> str:
    """Search products by name or category"""
    data = await get_products()
    results = []
    
    for category in data:
        for cat in category.get("categories", []):
            for item in cat.get("itemsResponseDtoList", []):
                if query.lower() in item.get("itemName", "").lower():
                    results.append({
                        "id": str(item.get("itemId")),
                        "title": item.get("itemName"),
                        "url": f"https://oxyloans.com/product/{item.get('itemId')}"
                    })
                    if len(results) >= 5:  # Limit results
                        break
    
    return json.dumps({"results": results})

@mcp.tool()
async def fetch(id: str) -> str:
    """Get complete product details by ID"""
    data = await get_products()
    
    for category in data:
        for cat in category.get("categories", []):
            for item in cat.get("itemsResponseDtoList", []):
                if str(item.get("itemId")) == id:
                    return json.dumps({
                        "id": id,
                        "title": item.get("itemName"),
                        "text": f"Price: ₹{item.get('itemPrice')}\nMRP: ₹{item.get('itemMrp')}\nDescription: {item.get('itemDescription')}",
                        "url": f"https://oxyloans.com/product/{id}"
                    })
    
    return json.dumps({"error": "Product not found"})

if __name__ == "__main__":
    mcp.run(transport="sse", host="0.0.0.0", port=8000)