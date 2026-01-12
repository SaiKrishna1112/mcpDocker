from pydantic import BaseModel
from mcp.server.fastmcp import FastMCP
from utils.http import get
from auth.token_store import get_token_by_session

# mcp: FastMCP
mcp = FastMCP(
    name="oxyloans-api"
)

class ComboItem(BaseModel):
    individualItemId: str
    itemName: str
    imageUrl: str
    quantity: int
    itemWeight: float
    units: str
    itemMrp: float
    itemPrice: float
    discountedPrice: float
    status: bool


class ComboResponse(BaseModel):
    comboItemId: str
    comboItemName: str
    minQty: int
    items: list[ComboItem]


@mcp.tool()
async def get_combo_item_details(
    session_id: str,
    item_id: str,
) -> ComboResponse:
    token = get_token_by_session(session_id)

    data = await get(
        f"/api/product-service/getComboInfo/{item_id}",
        params={},
        bearer_token=token,
    )

    return ComboResponse(
        comboItemId=data["comboItemId"],
        comboItemName=data["comboItemName"],
        minQty=data["minQty"],
        items=[ComboItem(**i) for i in data["items"]],
    )
