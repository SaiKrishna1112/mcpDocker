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
from pydantic import BaseModel, Field
from typing import List, Optional

mcp = FastMCP(name="oxyloans-api")

class ProductSuggestion(BaseModel):
    product_name: str
    category: str
    price: float
    mrp: float
    savings: str
    item_id: str
    why_recommended: str


@mcp.tool()
async def hello_world() -> str:
    """Test connectivity to OxyLoans MCP Server."""
    return "OxyLoans MCP Server is running!"

@mcp.tool()
async def get_product_suggestions(
    query: str = Field(..., min_length=1, description="Product search query"),
    session_id: str = Field(..., description="User session ID from login"),
    budget: float = Field(1000.0, gt=0, description="Maximum budget in INR")
) -> List[ProductSuggestion]:
    """Get AI-powered product suggestions using OxyLoans API."""
    from auth.token_store import get_token_by_session
    from utils.http import get
    
    token = get_token_by_session(session_id)
    if not token:
        raise ValueError("Invalid session. Please login first.")
    
    try:
        data = await get(
            "/api/product-service/dynamicSearch",
            params={"q": query},
            bearer_token=token
        )
        
        suggestions = []
        for category in data.get("items", []):
            category_name = category.get("categoryName", "General")
            
            for item in category.get("itemsResponseDtoList", []):
                price = float(item.get("itemPrice", 0))
                mrp = float(item.get("itemMrp", 0))
                
                if price <= budget and price > 0:
                    save_pct = ((mrp - price) / mrp * 100) if mrp > 0 else 0
                    
                    suggestions.append(ProductSuggestion(
                        product_name=item.get("itemName", "Unknown Product"),
                        category=category_name,
                        price=price,
                        mrp=mrp,
                        savings=f"{save_pct:.0f}% off" if save_pct > 0 else "No discount",
                        item_id=item.get("itemId", ""),
                        why_recommended=f"Matches '{query}', within ₹{budget} budget, {save_pct:.0f}% savings"
                    ))
        
        # Sort by savings percentage and return top 5
        suggestions.sort(key=lambda x: float(x.savings.replace('% off', '').replace('No discount', '0')), reverse=True)
        return suggestions[:5]
        
    except Exception as e:
        raise ValueError(f"Failed to fetch suggestions: {str(e)}")


@mcp.resource("oxyloans://api-docs")
async def get_api_docs() -> str:
    """OxyLoans API documentation and usage examples."""
    return """
# OxyLoans MCP Server API Documentation

## Public APIs (No Auth Required):
- `get_trending_products`: Browse all trending products with prices, discounts, and details
- `hello_world`: Test server connectivity

## Authentication Required:

### Auth Flow
- `send_login_otp`: Send OTP via SMS/WhatsApp
- `verify_login_otp`: Verify OTP and get session_id
- `send_register_otp`: Send OTP for new registration
- `verify_otp_and_authenticate`: Verify OTP for login/register

### Products (Auth)
- `dynamic_product_search`: Search products by query
- `get_product_suggestions`: AI-powered product recommendations
- `get_product_images`: Get product images
- `get_combo_item_details`: Get combo details

### User Management
- `get_customer_profile`: Get user profile
- `update_customer_profile`: Update profile
- `view_address_list`: View saved addresses
- `add_address`: Add new address

### Cart Operations
- `add_to_cart`: Add items to cart
- `view_user_cart`: View cart contents
- `decrement_cart_item`: Decrease quantity
- `remove_cart_item`: Remove item

## Quick Start:
1. Browse products: `get_trending_products()`
2. Login: `send_login_otp()` → `verify_login_otp()`
3. Shop: `dynamic_product_search()` → `add_to_cart()`
"""

# ---- auth modules ----
import auth.login as login
import auth.register as register
import auth.verify as verify
login.register_tools(mcp)
register.register_tools(mcp)
verify.register_tools(mcp)

# ---- products ----
import products.search as search
import products.public as public
search.register_tools(mcp)
public.register_tools(mcp)

# ---- user ----
import user.profile as profile
import user.address as address
profile.register_tools(mcp)
address.register_tools(mcp)

# ---- cart ----
import cart.add as cart_add
import cart.view as cart_view
import cart.decrement as cart_decrement
import cart.remove as cart_remove
cart_add.register_tools(mcp)
cart_view.register_tools(mcp)
cart_decrement.register_tools(mcp)
cart_remove.register_tools(mcp)

# ---- products extras ----
import products.images as images
import products.combo as combo
images.register_tools(mcp)
combo.register_tools(mcp)


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
