from typing import List, Optional, Any
from pydantic import BaseModel, Field
from utils.http import get
from auth.token_store import get_token_by_session

mcp = None

# -------------------------------------------------
# Schema (RAW items passthrough)
# -------------------------------------------------

class DynamicSearchResponse(BaseModel):
    query: str
    items: List[Any]
    empty: bool


# -------------------------------------------------
# Tool
# -------------------------------------------------

async def dynamic_product_search(
    q: str = Field(..., min_length=1, description="Search keyword"),
    session_id: str = Field(..., description="User session ID"),
) -> DynamicSearchResponse:
    """
    Search products dynamically and return ONLY the items array.
    """

    token = get_token_by_session(session_id)
    if not token:
        raise ValueError("Invalid session")

    data = await get(
        "/product-service/dynamicSearch",
        params={"q": q},
    )

    # ✅ Return only items array
    return DynamicSearchResponse(
        query=q,
        items=data.get("items", []),
        empty=data.get("empty", False),
    )


def register_tools(mcp_instance):
    global mcp
    mcp = mcp_instance
    mcp.tool()(dynamic_product_search)
