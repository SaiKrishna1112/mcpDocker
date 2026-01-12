# import os
# from typing import List, Optional, Dict
# import httpx
# from pydantic import BaseModel, Field
# from mcp.server.fastmcp import FastMCP
#
# # =====================================================
# # SERVER CONFIG (RENDER SAFE)
# # =====================================================
#
# PORT = int(os.environ.get("PORT", 8001))
#
# mcp = FastMCP(
#     name="oxyloans-api",
#     host="0.0.0.0",
#     port=PORT,
# )
#
# BASE_URL = "https://meta.oxyloans.com/api"
#
# # =====================================================
# # TOKEN STORE (REPLACE WITH DB / REDIS LATER)
# # =====================================================
#
# USER_TOKENS: Dict[str, str] = {
#     # "test-user": "REAL_OR_DUMMY_BEARER_TOKEN"
# }
#
# def get_bearer_token(user_id: str) -> str:
#     token = USER_TOKENS.get(user_id)
#     if not token:
#         raise ValueError("Bearer token not found for user")
#     return token
#
# # =====================================================
# # HTTP HELPERS
# # =====================================================
#
# async def api_get(url: str, user_id: Optional[str] = None):
#     headers = {}
#     if user_id:
#         headers["Authorization"] = f"Bearer {get_bearer_token(user_id)}"
#
#     async with httpx.AsyncClient(timeout=30.0) as client:
#         response = await client.get(url, headers=headers)
#         response.raise_for_status()
#         return response.json()
#
# async def api_post(url: str, payload: dict, user_id: Optional[str] = None):
#     headers = {"Content-Type": "application/json"}
#     if user_id:
#         headers["Authorization"] = f"Bearer {get_bearer_token(user_id)}"
#
#     async with httpx.AsyncClient(timeout=30.0) as client:
#         response = await client.post(url, json=payload, headers=headers)
#         response.raise_for_status()
#         return response.json()
#
# # =====================================================
# # SCHEMAS
# # =====================================================
#
# class Product(BaseModel):
#     item_id: str
#     name: str
#     price: float
#     mrp: float
#     image: Optional[str]
#     description: Optional[str]
#     category: Optional[str]
#
# class TrendingProductsResponse(BaseModel):
#     products: List[Product]
#     count: int
#
# class ActiveOffersResponse(BaseModel):
#     offers: list
#
# class CartActionResponse(BaseModel):
#     status: str
#     message: str
#
# # =====================================================
# # TOOLS (NO read_only FLAG)
# # =====================================================
#
# @mcp.tool()
# async def get_trending_products(
#     limit: int = Field(20, ge=1, le=100)
# ) -> TrendingProductsResponse:
#     """
#     Get trending products (public).
#     """
#     url = f"{BASE_URL}/product-service/showGroupItemsForCustomrs"
#     data = await api_get(url)
#
#     products: List[Product] = []
#
#     for group in data:
#         for category in group.get("categories", []):
#             for item in category.get("itemsResponseDtoList", []):
#                 products.append(
#                     Product(
#                         item_id=item.get("itemId"),
#                         name=item.get("itemName"),
#                         price=item.get("itemPrice", 0),
#                         mrp=item.get("itemMrp", 0),
#                         image=item.get("itemImage"),
#                         description=item.get("itemDescription"),
#                         category=category.get("categoryName"),
#                     )
#                 )
#
#     products = products[:limit]
#     return TrendingProductsResponse(products=products, count=len(products))
#
# @mcp.tool()
# async def get_active_offers() -> ActiveOffersResponse:
#     """
#     Get active combo offers (public).
#     """
#     url = f"{BASE_URL}/product-service/getComboActiveInfo"
#     data = await api_get(url)
#     return ActiveOffersResponse(offers=data)
#
# @mcp.tool()
# async def add_to_cart(
#     user_id: str = Field(..., description="User ID"),
#     item_id: str = Field(...),
#     quantity: int = Field(..., ge=1, le=10),
# ) -> CartActionResponse:
#     """
#     Add item to user's cart (auth required).
#     """
#     url = f"{BASE_URL}/cart-service/cart/addAndIncrementCart"
#     payload = {
#         "customerId": user_id,
#         "itemId": item_id,
#         "quantity": quantity
#     }
#
#     await api_post(url, payload, user_id=user_id)
#
#     return CartActionResponse(
#         status="success",
#         message="Item added to cart"
#     )
#
# # =====================================================
# # START SERVER
# # =====================================================
#
# if __name__ == "__main__":
#     print(f"✅ MCP Server running on port {PORT}")
#     mcp.run(transport="sse")


from mcp.server.fastmcp import FastMCP

mcp = FastMCP(
    name="oxyloans-api",
    host="0.0.0.0",  # only used for SSE transport (localhost)
    port=8001,  # only used for SSE transport (set this to any port)
)

# ---- auth modules ----
from auth import login, register, verify
login.mcp = mcp
register.mcp = mcp
verify.mcp = mcp

# ---- products ----
from products import search
search.mcp = mcp

# ---- user ----
from user import profile, address
profile.mcp = mcp
address.mcp = mcp

from cart import add, view, decrement, remove
from products import images, combo

add.mcp = mcp
view.mcp = mcp
decrement.mcp = mcp
remove.mcp = mcp
images.mcp = mcp
combo.mcp = mcp


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
