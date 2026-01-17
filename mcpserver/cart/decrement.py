from pydantic import BaseModel
from utils.http import patch
from auth.token_store import get_token_by_session, get_user_id_by_session

mcp = None

class DecrementCartResponse(BaseModel):
    success: bool
    errorMessage: str | None


async def decrement_cart_item(
    session_id: str,
    item_id: str,
) -> DecrementCartResponse:
    user_id = get_user_id_by_session(session_id)
    if not user_id:
        raise ValueError("Invalid session")
    
    token = get_token_by_session(session_id)

    payload = {
        "customerId": user_id,
        "itemId": item_id,
    }

    data = await patch(
        "/cart-service/cart/minusCartItem",
        payload,
        bearer_token=token,
    )

    return DecrementCartResponse(
        success=data.get("success", True),
        errorMessage=data.get("errorMessage"),
    )


def register_tools(mcp_instance):
    global mcp
    mcp = mcp_instance
    mcp.tool()(decrement_cart_item)
