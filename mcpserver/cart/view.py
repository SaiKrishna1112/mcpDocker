from typing import List
from pydantic import BaseModel
from fastmcp import FastMCP
from utils.http import get
from auth.token_store import get_token_by_session

# mcp: FastMCP
mcp = FastMCP(
    name="oxyloans-api"
)

class CartItem(BaseModel):
    cartId: str
    itemId: str
    itemName: str
    units: str
    image: str
    weight: float
    priceMrp: float
    itemPrice: float
    totalPrice: float
    cartQuantity: int
    quantity: int
    saveAmount: float
    savePercentage: float
    gstAmount: float
    status: str
    combo: bool
    lowStock: bool


class ViewCartResponse(BaseModel):
    items: List[CartItem]
    totalCartValue: float
    freeItemPriceTotal: float
    amountToPay: float
    discountedByFreeItems: float
    totalGstAmountToPay: float


@mcp.tool()
async def view_user_cart(
    session_id: str,
    customer_id: str,
) -> ViewCartResponse:
    token = get_token_by_session(session_id)

    data = await get(
        "/api/cart-service/cart/userCartInfo",
        params={"customerId": customer_id},
        bearer_token=token,
    )

    items = [
        CartItem(
            **item,
            lowStock=item.get("quantity", 0) <= 5,
        )
        for item in data.get("customerCartResponseList", [])
    ]

    return ViewCartResponse(
        items=items,
        totalCartValue=data.get("totalCartValue"),
        freeItemPriceTotal=data.get("freeItemPriceTotal"),
        amountToPay=data.get("amountToPay"),
        discountedByFreeItems=data.get("discountedByFreeItems"),
        totalGstAmountToPay=data.get("totalGstAmountToPay"),
    )
