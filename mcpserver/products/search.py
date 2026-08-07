from typing import List, Any
from pydantic import BaseModel, Field
from utils.http import get

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
) -> DynamicSearchResponse:
    """
    Search products dynamically and return the items array.
    """

    data = await get(
        "/product-service/dynamicSearch",
        params={"q": q},
    )

    return DynamicSearchResponse(
        query=q,
        items=data.get("items", []),
        empty=data.get("empty", False),
    )


def register_tools(mcp_instance):
    global mcp
    mcp = mcp_instance
    mcp.tool(annotations={"readOnlyHint": True, "openWorldHint": True, "destructiveHint": False})(dynamic_product_search)
