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


from fastmcp import FastMCP
import instructor
from pydantic import BaseModel
from typing import List

mcp = FastMCP(
    name="oxyloans-api"
)

class APIResponse(BaseModel):
    """Structured API response with instructor validation."""
    success: bool
    message: str
    data: dict = {}

class ProductSuggestion(BaseModel):
    """AI-powered product suggestion."""
    product_name: str
    category: str
    price_range: str
    why_recommended: str

@mcp.tool()
async def hello_world() -> str:
    """A simple test tool that returns a greeting."""
    return "Hello from OxyLoans MCP Server!"

@mcp.tool()
async def get_smart_product_suggestions(
    user_query: str,
    budget: float = 1000.0
) -> List[ProductSuggestion]:
    """Get AI-powered product suggestions based on user query and budget."""
    # Mock suggestions using instructor-like structured responses
    suggestions = [
        ProductSuggestion(
            product_name="Basmati Rice 5kg",
            category="Groceries",
            price_range="₹400-600",
            why_recommended="High quality, fits budget, essential staple"
        ),
        ProductSuggestion(
            product_name="Organic Pulses Combo",
            category="Groceries", 
            price_range="₹300-500",
            why_recommended="Nutritious, good value, popular choice"
        )
    ]
    return suggestions

@mcp.resource("oxyloans://api-docs")
async def get_api_docs() -> str:
    """OxyLoans API documentation and usage examples."""
    return """
# OxyLoans MCP Server API Documentation

## Available Tools:

### Authentication
- `send_login_otp`: Send OTP for login via SMS/WhatsApp
- `verify_login_otp`: Verify OTP and get session
- `send_register_otp`: Send OTP for registration
- `verify_otp_and_authenticate`: Verify OTP for login/register

### Products
- `dynamic_product_search`: Search products (requires session)
- `get_product_images`: Get product images
- `get_combo_item_details`: Get combo product details

### User Management
- `get_customer_profile`: Get user profile
- `update_customer_profile`: Update user profile
- `view_address_list`: View saved addresses
- `add_address`: Add new address

### Cart Operations
- `add_to_cart`: Add items to cart
- `view_user_cart`: View cart contents
- `decrement_cart_item`: Decrease item quantity
- `remove_cart_item`: Remove item from cart

## Usage Flow:
1. Send OTP using `send_login_otp` or `send_register_otp`
2. Verify OTP using `verify_login_otp` or `verify_otp_and_authenticate`
3. Use the returned session_id for authenticated operations
4. Search products, manage cart, update profile as needed

## Example:
```
1. send_login_otp(country_code="+91", mobile_or_whatsapp="9876543210", registration_type="sms")
2. verify_login_otp(..., session_id from step 1)
3. dynamic_product_search(q="rice", session_id=session_from_step2)
```
"""

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
from products import images, combo, public

add.mcp = mcp
view.mcp = mcp
decrement.mcp = mcp
remove.mcp = mcp
images.mcp = mcp
combo.mcp = mcp
public.mcp = mcp


if __name__ == "__main__":
    transport = "sse"
    if transport == "stdio":
        print("Running server with stdio transport")
        mcp.run(transport="stdio")
    elif transport == "sse":
        print("Running server with SSE transport")
        mcp.run(transport="sse", host="0.0.0.0", port=8001)
    else:
        raise ValueError(f"Unknown transport: {transport}")
