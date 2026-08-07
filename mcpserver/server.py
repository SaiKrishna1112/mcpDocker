from fastmcp import FastMCP
from pydantic import BaseModel, Field, TypeAdapter
from typing import List, Optional, get_type_hints
import os

mcp = FastMCP(name="askoxy-api")

_original_tool = mcp.tool

def _infer_output_schema(fn):
    try:
        return_type = get_type_hints(fn, include_extras=True).get("return")
        if return_type is None:
            return None
        schema = TypeAdapter(return_type).json_schema()
        if schema.get("type") != "object" and "properties" not in schema:
            return None
        return schema
    except Exception:
        return None

def _tool_with_output_schema(*tool_args, **tool_kwargs):
    def _decorate(fn):
        call_kwargs = dict(tool_kwargs)
        if call_kwargs.get("output_schema") is None:
            output_schema = _infer_output_schema(fn)
            if output_schema is not None:
                call_kwargs["output_schema"] = output_schema
        return _original_tool(*tool_args, **call_kwargs)(fn)

    if tool_args and callable(tool_args[0]) and len(tool_args) == 1 and not tool_kwargs:
        return _decorate(tool_args[0])

    return _decorate

mcp.tool = _tool_with_output_schema
# Add route for health check
@mcp.custom_route("/health", methods=["GET"])
async def health(request):
    """Health check endpoint"""
    from starlette.responses import JSONResponse
    return JSONResponse({"status": "healthy"})

# Add route for OpenAI apps challenge
@mcp.tool(annotations={"readOnlyHint": True, "openWorldHint": False, "destructiveHint": False})
async def get_openai_challenge() -> str:
    """Serve OpenAI apps challenge token for verification"""
    return "lCG1ME4nDMF4SQ5WN34e_mRcJ2671QubLKki1faFH8o"

class ProductSuggestion(BaseModel):
    product_name: str
    category: str
    price: float
    mrp: float
    savings: str
    item_id: str
    why_recommended: str


@mcp.tool(annotations={"readOnlyHint": True, "openWorldHint": False, "destructiveHint": False})
async def hello_world() -> str:
    """Test connectivity to askoxy.ai MCP Server."""
    return "askoxy.ai MCP Server is running!"

@mcp.tool(annotations={"readOnlyHint": True, "openWorldHint": True, "destructiveHint": False})
async def get_product_suggestions(
    query: str = Field(..., min_length=1, description="Product search query"),
    budget: float = Field(1000.0, gt=0, description="Maximum budget in INR")
) -> List[ProductSuggestion]:
    """Get AI-powered product suggestions using askoxy.ai API."""
    from utils.http import get

    try:
        data = await get(
            "/api/product-service/dynamicSearch",
            params={"q": query},
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

@mcp.resource("askoxy://api-docs")
async def get_api_docs() -> str:
    """askoxy.ai MCP Server API documentation and usage examples."""
    return """
# Askoxy.ai MCP Server – API Documentation

## Public APIs (No Authentication Required)
These APIs are accessible without login.

- `get_trending_products`  
  Browse trending products with prices, discounts, weight, and availability.

- `hello_world`  
  Health check to verify MCP server connectivity.

---

## Authentication APIs (OTP-Based Only)

> NOTE: Simple login without OTP is **not supported**.

### Login Flow
- `send_login_otp`  
  Sends OTP via SMS/WhatsApp for existing users.

- `verify_login_otp`  
  Verifies OTP and returns session credentials.

### Registration Flow
- `send_register_otp`  
  Sends OTP for new user registration.

- `verify_otp_and_authenticate`  
  Verifies OTP and completes login or registration.

---

## Product APIs (Authentication Required)

- `dynamic_product_search`  
  Search products using keywords (e.g., rice, cashews).

- `get_product_suggestions`  
  AI-powered personalized product recommendations.

- `get_product_images`  
  Retrieve images for a given itemId.

- `get_combo_item_details`  
  Fetch combo offer details for a product.

---

## User Management APIs

- `get_customer_profile`  
  Fetch logged-in user profile details.

- `update_customer_profile`  
  Create or update user profile information.

- `view_address_list`  
  View all saved delivery addresses.

- `add_address`  
  Add a new delivery address with latitude & longitude.

---

## Cart Operations

- `add_to_cart`  
  Add or increment an item in the cart.

- `view_user_cart`  
  Retrieve cart items, totals, discounts, and free items.

- `decrement_cart_item`  
  Reduce item quantity by one.

- `remove_cart_item`  
  Remove an item completely from the cart.

---

## Order Management APIs

- `check_order_conditions`  
  Validate cart and order constraints.

- `check_delivery_availability`  
  Check serviceability for a given pincode.

- `place_order`  
  Place an order after successful payment.

- `get_order_history`  
  Fetch previous orders.

- `track_order`  
  Track current order status.

- `cancel_order`  
  Cancel eligible orders based on policy.

---

## Complete Checkout Flow (Sequential)

1. `fetch_cart_summary`  
   STEP 1 – Retrieve cart totals and discounts.

2. `get_user_addresses`  
   STEP 2.1 – Fetch delivery addresses.

3. `validate_pincode_serviceability`  
   STEP 2.2 – Confirm delivery availability.

4. `calculate_delivery_charges`  
   STEP 3 – Compute delivery & handling fees.

5. `get_available_coupons`  
   STEP 4 – Retrieve eligible coupons.

6. `apply_wallet_amount`  
   STEP 5 – Apply wallet or coin balance.

7. `fetch_delivery_slots`  
   STEP 6 – Get available delivery slots.

8. `initiate_payment`  
   STEP 7 – Initiate payment transaction.

9. `confirm_payment`  
   STEP 8 – Confirm payment success or failure.

10. `validate_checkout`  
    Final validation before order placement.

---

## API Summary
- Total APIs: 29
- Authentication: OTP-based only
- Status: All APIs implemented and registered

---

## Quick Start

1. Health Check  
   `hello_world()`

2. Login / Register  
   `send_login_otp()` → `verify_login_otp()`

3. Browse Products  
   `get_trending_products()`  
   or  
   `dynamic_product_search("rice")`

4. Add to Cart  
   `add_to_cart()` → `view_user_cart()`

5. Checkout & Payment  
   `validate_checkout()` → `initiate_payment()` → `confirm_payment()`
"""


# ---- auth modules ----
import auth.login as login
import auth.register as register
import auth.verify as verify
import auth.simple_login as simple_login
import auth.token_login as token_login
login.register_tools(mcp)
register.register_tools(mcp)
verify.register_tools(mcp)
simple_login.register_tools(mcp)
token_login.register_tools(mcp)

# ---- products ----
import products.search as search
import products.public as public
import products.images as images
import products.combo as combo
search.register_tools(mcp)
public.register_tools(mcp)
images.register_tools(mcp)
combo.register_tools(mcp)

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

# ---- orders ----
import orders.validation as order_validation
import orders.management as order_management
import orders.checkout as order_checkout
order_validation.register_tools(mcp)
order_management.register_tools(mcp)
order_checkout.register_tools(mcp)


if __name__ == "__main__":
    print(f"✅ askoxy.ai MCP Server configured")
    print(f"✅ Challenge token available via get_openai_challenge tool")
    mcp.run(transport="sse", host="0.0.0.0", port=8001)


