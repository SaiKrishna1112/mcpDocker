from typing import List
from pydantic import BaseModel
from utils.http import get
from auth.token_store import get_token_by_session, get_user_id_by_session

mcp = None

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


async def view_user_cart(
    session_id: str,
) -> ViewCartResponse:
    user_id = get_user_id_by_session(session_id)
    if not user_id:
        raise ValueError("Invalid session")
    
    token = get_token_by_session(session_id)

    data = await get(
        "/cart-service/cart/userCartInfo",
        params={"customerId": user_id},
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


def register_tools(mcp_instance):
    global mcp
    mcp = mcp_instance
    mcp.tool()(view_user_cart)
