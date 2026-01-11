from pydantic import BaseModel
from mcp.server.fastmcp import FastMCP
from ..utils.http import post
from ..auth.token_store import get_token_by_session

# mcp: FastMCP
mcp = FastMCP(
    name="oxyloans-api"
)

class DecrementCartResponse(BaseModel):
    success: bool
    errorMessage: str | None


@mcp.tool()
async def decrement_cart_item(
    session_id: str,
    customer_id: str,
    item_id: str,
) -> DecrementCartResponse:
    token = get_token_by_session(session_id)

    payload = {
        "customerId": customer_id,
        "itemId": item_id,
    }

    data = await post(
        "/api/cart-service/cart/minusCartItem",
        payload,
        bearer_token=token,
    )

    return DecrementCartResponse(
        success=data.get("success", True),
        errorMessage=data.get("errorMessage"),
    )
