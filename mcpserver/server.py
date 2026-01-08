from typing import Any
import httpx
from mcp.server.fastmcp import FastMCP

# Create an MCP server
mcp = FastMCP(
    name="oxyloans-api",
    host="0.0.0.0",
    port=8001,
)

# Constants
BASE_URL = "https://meta.oxyloans.com/api"

async def make_api_request(url: str, method: str = "GET", data: dict = None) -> dict[str, Any] | None:
    """Generic API request handler."""
    headers = {"Content-Type": "application/json"}
    
    async with httpx.AsyncClient() as client:
        try:
            if method.upper() == "GET":
                response = await client.get(url, headers=headers, timeout=30.0)
            elif method.upper() == "POST":
                response = await client.post(url, headers=headers, json=data, timeout=30.0)
            else:
                return {"error": "Unsupported method"}
            
            response.raise_for_status()
            return response.json()
        except Exception as e:
            return {"error": str(e)}

@mcp.tool()
async def get_user_cart(customer_id: str) -> str:
    """Get user's cart information.
    
    Args:
        customer_id: The customer ID
    """
    url = f"{BASE_URL}/cart-service/cart/userCartInfo?customerId={customer_id}"
    data = await make_api_request(url)
    
    if "error" in data:
        return f"Error fetching cart: {data['error']}"
    
    return str(data)

@mcp.tool()
async def get_user_profile(user_id: str) -> str:
    """Get user profile information.
    
    Args:
        user_id: The user ID
    """
    url = f"{BASE_URL}/users/{user_id}"
    data = await make_api_request(url)
    
    if "error" in data:
        return f"Error fetching profile: {data['error']}"
    
    return str(data)

@mcp.tool()
async def get_trending_products() -> str:
    """Get all trending products with details."""
    url = "https://meta.oxyloans.com/api/product-service/showGroupItemsForCustomrs"
    data = await make_api_request(url)
    
    if "error" in data:
        return f"Error fetching products: {data['error']}"
    
    items = []
    try:
        for category in data:
            for cat in category.get("categories", []):
                for item in cat.get("itemsResponseDtoList", []):
                    items.append({
                        "id": item.get("itemId"),
                        "name": item.get("itemName"),
                        "price": item.get("itemPrice"),
                        "mrp": item.get("itemMrp"),
                        "image": item.get("itemImage"),
                        "description": item.get("itemDescription"),
                        "saveAmount": item.get("saveAmount"),
                        "savePercentage": item.get("savePercentage"),
                        "weight": item.get("weight"),
                        "units": item.get("units"),
                        "quantity": item.get("quantity"),
                        "category": cat.get("categoryName"),
                    })
        return str(items)
    except Exception as e:
        return f"Error processing products: {str(e)}"

@mcp.tool()
async def get_active_offers() -> str:
    """Get active combo offers."""
    url = f"{BASE_URL}/product-service/getComboActiveInfo"
    data = await make_api_request(url)
    
    if "error" in data:
        return f"Error fetching offers: {data['error']}"
    
    return str(data)

@mcp.tool()
async def add_to_cart(customer_id: str, item_id: str, quantity: int) -> str:
    """Add item to user's cart.
    
    Args:
        customer_id: The customer ID
        item_id: The item ID to add
        quantity: Quantity to add
    """
    url = f"{BASE_URL}/cart-service/cart/addAndIncrementCart"
    payload = {
        "customerId": customer_id,
        "itemId": item_id,
        "quantity": quantity
    }
    data = await make_api_request(url, "POST", payload)
    
    if "error" in data:
        return f"Error adding to cart: {data['error']}"
    
    return f"Item added to cart successfully: {data}"

@mcp.tool()
async def remove_from_cart(customer_id: str, item_id: str) -> str:
    """Remove item from user's cart.
    
    Args:
        customer_id: The customer ID
        item_id: The item ID to remove
    """
    url = f"{BASE_URL}/cart-service/cart/remove"
    payload = {
        "customerId": customer_id,
        "itemId": item_id
    }
    data = await make_api_request(url, "POST", payload)
    
    if "error" in data:
        return f"Error removing from cart: {data['error']}"
    
    return "Item removed from cart successfully"

# Run the server
if __name__ == "__main__":
    transport = "sse"
    if transport == "stdio":
        print("Running server with stdio transport")
        mcp.run(transport="stdio")
    elif transport == "sse":
        print("Running server with SSE transport")
        mcp.run(transport="sse")
    else:
        raise ValueError(f"Unknown transport: {transport}")