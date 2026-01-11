from pydantic import BaseModel
from mcp.server.fastmcp import FastMCP
from ..utils.http import post
from ..auth.token_store import get_token_by_session

# mcp: FastMCP
mcp = FastMCP(
    name="oxyloans-api"
)

class RemoveCartResponse(BaseModel):
    success: bool
    message: str


@mcp.tool()
async def remove_cart_item(
    session_id: str,
    cart_id: str,
) -> RemoveCartResponse:
    token = get_token_by_session(session_id)

    data = await post(
        "/api/cart-service/cart/remove",
        {"id": cart_id},
        bearer_token=token,
    )

    return RemoveCartResponse(
        success=True,
        message="Cart item removed successfully",
    )
