from pydantic import BaseModel
from utils.http import post
from auth.token_store import get_token_by_session, get_user_id_by_session

mcp = None

class RemoveCartResponse(BaseModel):
    success: bool
    message: str


async def remove_cart_item(
    session_id: str,
    cart_id: str,
) -> RemoveCartResponse:
    user_id = get_user_id_by_session(session_id)
    if not user_id:
        raise ValueError("Invalid session")
    
    token = get_token_by_session(session_id)

    data = await post(
        "/cart-service/cart/remove",
        {"id": cart_id},
        bearer_token=token,
    )

    return RemoveCartResponse(
        success=True,
        message="Cart item removed successfully",
    )


def register_tools(mcp_instance):
    global mcp
    mcp = mcp_instance
    mcp.tool()(remove_cart_item)
