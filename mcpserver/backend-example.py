# Example of how to add your specific backend APIs

# Add to your server.py:

# Your API configuration
BACKEND_API_BASE = "https://your-api.com/api/v1"
API_KEY = "your-api-key"  # Store in .env file

# Add authentication headers
async def make_authenticated_request(url: str, method: str = "GET", data: dict = None):
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }
    return await make_api_request(url, method, headers, data)

# Example tools for your specific APIs:

@mcp.tool()
async def get_products() -> str:
    """Get all products from your e-commerce API."""
    url = f"{BACKEND_API_BASE}/products"
    data = await make_authenticated_request(url)
    return str(data)

@mcp.tool()
async def create_order(customer_id: str, product_id: str, quantity: int) -> str:
    """Create a new order."""
    url = f"{BACKEND_API_BASE}/orders"
    payload = {
        "customer_id": customer_id,
        "product_id": product_id,
        "quantity": quantity
    }
    data = await make_authenticated_request(url, "POST", payload)
    return str(data)

@mcp.tool()
async def get_analytics(start_date: str, end_date: str) -> str:
    """Get analytics data for date range."""
    url = f"{BACKEND_API_BASE}/analytics?start={start_date}&end={end_date}"
    data = await make_authenticated_request(url)
    return str(data)