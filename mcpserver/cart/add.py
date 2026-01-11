from pydantic import BaseModel, Field
from fastmcp import FastMCP
from ..utils.http import post
from ..auth.token_store import get_token_by_session
from .validation import validate_profile_before_cart

mcp: FastMCP


class AddCartResponse(BaseModel):
    success: bool
    errorMessage: str | None


@mcp.tool()
async def add_to_cart(
    session_id: str,
    customer_id: str,
    item_id: str,
    cart_quantity: int = Field(..., ge=1),
    status: str | None = Field(None, description="Use COMBO for combo items"),
) -> AddCartResponse:
    """
    Add / increment item or add combo item.
    """
    await validate_profile_before_cart(session_id, customer_id)

    token = get_token_by_session(session_id)

    payload = {
        "customerId": customer_id,
        "itemId": item_id,
        "cartQuantity": cart_quantity,
    }

    if status == "COMBO":
        payload["status"] = "COMBO"

    data = await post(
        "/api/cart-service/cart/addAndIncrementCart",
        payload,
        bearer_token=token,
    )

    return AddCartResponse(
        success=data.get("success", True),
        errorMessage=data.get("errorMessage"),
    )
