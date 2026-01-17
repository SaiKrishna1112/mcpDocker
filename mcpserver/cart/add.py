from pydantic import BaseModel, Field
from utils.http import post
from auth.token_store import get_token_by_session, get_user_id_by_session
from cart.validation import validate_profile_before_cart

mcp = None

class AddCartResponse(BaseModel):
    success: bool
    errorMessage: str | None


async def add_to_cart(
    session_id: str,
    item_id: str,
    cart_quantity: int = Field(..., ge=1),
    status: str | None = Field(None, description="Use COMBO for combo items"),
) -> AddCartResponse:
    """
    Add / increment item or add combo item.
    """
    user_id = get_user_id_by_session(session_id)
    if not user_id:
        raise ValueError("Invalid session")

    await validate_profile_before_cart(session_id, user_id)

    token = get_token_by_session(session_id)

    payload = {
        "customerId": user_id,
        "itemId": item_id,
        "cartQuantity": cart_quantity,
    }

    if status == "COMBO":
        payload["status"] = "COMBO"

    data = await post(
        "/cart-service/cart/addAndIncrementCart",
        payload,
        bearer_token=token,
    )

    return AddCartResponse(
        success=data.get("success", True),
        errorMessage=data.get("errorMessage"),
    )


def register_tools(mcp_instance):
    global mcp
    mcp = mcp_instance
    mcp.tool()(add_to_cart)
