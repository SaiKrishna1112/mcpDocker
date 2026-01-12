from typing import List, Optional
from pydantic import BaseModel, Field
from fastmcp import FastMCP
from utils.http import get
from auth.token_store import get_token_by_session

# mcp: FastMCP  # injected from server.py
mcp = FastMCP(
    name="oxyloans-api"
)

# -------------------------------------------------
# Schemas
# -------------------------------------------------

class SearchItem(BaseModel):
    item_id: str
    item_name: str
    description: Optional[str]
    image: Optional[str]
    units: Optional[str]
    weight: Optional[float]
    mrp: Optional[float]
    price: Optional[float]
    save_amount: Optional[float]
    save_percentage: Optional[float]
    quantity: Optional[int]
    barcode: Optional[str]
    category_name: str


class DynamicSearchResponse(BaseModel):
    query: str
    total_items: int
    items: List[SearchItem]


# -------------------------------------------------
# Tool
# -------------------------------------------------

@mcp.tool()
async def dynamic_product_search(
    q: str = Field(..., min_length=1, description="Search keyword"),
    session_id: str = Field(
        ...,
        description="User session ID (required for token-based access)",
    ),
) -> DynamicSearchResponse:
    """
    Search products dynamically by keyword using authenticated access.
    """

    # ---------------------------------------------
    # Resolve access token from session
    # ---------------------------------------------
    access_token = get_token_by_session(session_id)
    if not access_token:
        raise ValueError("Invalid or expired session. Please login again.")

    # ---------------------------------------------
    # Call backend API with Bearer token
    # ---------------------------------------------
    data = await get(
        "/api/product-service/dynamicSearch",
        params={"q": q},
        bearer_token=access_token,
    )

    results: List[SearchItem] = []

    for category in data.get("items", []):
        category_name = category.get("categoryName")

        for item in category.get("itemsResponseDtoList", []):
            results.append(
                SearchItem(
                    item_id=item.get("itemId"),
                    item_name=item.get("itemName"),
                    description=item.get("itemDescription"),
                    image=item.get("itemImage"),
                    units=item.get("units"),
                    weight=item.get("weight"),
                    mrp=item.get("itemMrp"),
                    price=item.get("itemPrice"),
                    save_amount=item.get("saveAmount"),
                    save_percentage=item.get("savePercentage"),
                    quantity=item.get("quantity"),
                    barcode=item.get("barcodeValue"),
                    category_name=category_name,
                )
            )

    return DynamicSearchResponse(
        query=q,
        total_items=len(results),
        items=results,
    )
