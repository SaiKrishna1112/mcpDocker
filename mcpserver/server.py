from typing import List, Optional, Dict
import httpx
from pydantic import BaseModel, Field
from mcp.server.fastmcp import FastMCP

# =====================================================
# MCP SERVER CONFIG
# =====================================================

mcp = FastMCP(
    name="oxyloans-api",
    host="0.0.0.0",
    port=8001,
)

BASE_URL = "https://meta.oxyloans.com/api"

# =====================================================
# TOKEN STORE (REPLACE WITH DB / REDIS LATER)
# =====================================================

USER_TOKENS: Dict[str, str] = {
    # Example
    # "14996e93-46c9-46cb-a5fb-8050b8af17ab": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
"14996e93-46c9-46cb-a5fb-8050b8af17ab":"eyJhbGciOiJIUzUxMiJ9.eyJzdWIiOiIxNDk5NmU5My00NmM5LTQ2Y2ItYTVmYi04MDUwYjhhZjE3YWIiLCJpYXQiOjE3NjczNjY0NjcsImV4cCI6MTc2ODIzMDQ2N30.SjLdZLFCDp8KDOoPdHrcjmPUdmLd9SItdaeXrBc-b5nJ7DemAPITCryBuZzGf5LtPkAuLn79xhGTvPTv_jPI4A"
}


def get_bearer_token(user_id: str) -> str:
    """
    Resolve bearer token for a user.
    """
    token = USER_TOKENS.get(user_id)
    if not token:
        raise ValueError("No bearer token found for user")
    return token


# =====================================================
# AUTH-AWARE HTTP CLIENT
# =====================================================

async def api_get(url: str, user_id: Optional[str] = None):
    headers = {}
    if user_id:
        headers["Authorization"] = f"Bearer {get_bearer_token(user_id)}"

    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.get(url, headers=headers)
        response.raise_for_status()
        return response.json()


async def api_post(url: str, payload: dict, user_id: Optional[str] = None):
    headers = {"Content-Type": "application/json"}
    if user_id:
        headers["Authorization"] = f"Bearer {get_bearer_token(user_id)}"

    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.post(url, json=payload, headers=headers)
        response.raise_for_status()
        return response.json()


# =====================================================
# SCHEMAS
# =====================================================

class Product(BaseModel):
    item_id: str
    name: str
    price: float
    mrp: float
    image: Optional[str]
    description: Optional[str]
    category: Optional[str]


class TrendingProductsResponse(BaseModel):
    products: List[Product]
    count: int


class ActiveOffersResponse(BaseModel):
    offers: list


class CartActionResponse(BaseModel):
    status: str
    message: str


# =====================================================
# READ-ONLY TOOLS (SAFE)
# =====================================================

@mcp.tool(read_only=True)
async def get_trending_products(
    limit: int = Field(20, ge=1, le=100)
) -> TrendingProductsResponse:
    """
    Get trending products (public, no auth).
    """
    url = f"{BASE_URL}/product-service/showGroupItemsForCustomrs"
    data = await api_get(url)

    products: List[Product] = []

    for group in data:
        for category in group.get("categories", []):
            for item in category.get("itemsResponseDtoList", []):
                products.append(
                    Product(
                        item_id=item.get("itemId"),
                        name=item.get("itemName"),
                        price=item.get("itemPrice", 0),
                        mrp=item.get("itemMrp", 0),
                        image=item.get("itemImage"),
                        description=item.get("itemDescription"),
                        category=category.get("categoryName"),
                    )
                )

    products = products[:limit]
    return TrendingProductsResponse(products=products, count=len(products))


@mcp.tool(read_only=True)
async def get_active_offers() -> ActiveOffersResponse:
    """
    Get active combo offers (public).
    """
    url = f"{BASE_URL}/product-service/getComboActiveInfo"
    data = await api_get(url)
    return ActiveOffersResponse(offers=data)


# =====================================================
# USER-SCOPED WRITE TOOLS (AUTH REQUIRED)
# =====================================================

@mcp.tool()
async def add_to_cart(
    user_id: str = Field(..., description="Authenticated user ID"),
    item_id: str = Field(...),
    quantity: int = Field(..., ge=1, le=10),
) -> CartActionResponse:
    """
    Add item to user's cart (requires auth).
    """
    url = f"{BASE_URL}/cart-service/cart/addAndIncrementCart"
    payload = {
        "customerId": user_id,
        "itemId": item_id,
        "quantity": quantity
    }

    await api_post(url, payload, user_id=user_id)

    return CartActionResponse(
        status="success",
        message="Item added to cart"
    )


# =====================================================
# SERVER START
# =====================================================

if __name__ == "__main__":
    print("✅ MCP Server running with auth support (SSE, port 8001)")
    mcp.run(transport="sse")
