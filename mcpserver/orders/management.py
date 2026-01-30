from typing import Optional, List
from pydantic import BaseModel, Field
import json

from utils.http import get, post
from auth.token_store import get_token_by_session, get_user_id_by_session

mcp = None

# --------------------------------------------------
# MAPPINGS
# --------------------------------------------------

ORDER_STATUS_MAP = {
    "0": "Incomplete",
    "1": "Placed",
    "2": "Accepted",
    "3": "Assigned",
    "4": "Delivered",
    "5": "Rejected",
    "6": "Cancelled",
    "7": "Exchanged",
    "PickedUp": "Picked up",
}

PAYMENT_TYPE_MAP = {
    1: "COD",
    2: "Online",
}

def get_order_status(status):
    return ORDER_STATUS_MAP.get(str(status), "Unknown")

def get_payment_type(payment_type):
    return PAYMENT_TYPE_MAP.get(payment_type, "Unknown")

# --------------------------------------------------
# SCHEMAS
# --------------------------------------------------

class OrderItem(BaseModel):
    item_id: Optional[str] = None
    item_name: Optional[str] = None
    quantity: Optional[int] = None
    price: Optional[float] = None
    total_price: Optional[float] = None


class OrderDetails(BaseModel):
    order_id: str
    order_date: Optional[str] = None
    status: str

    total_amount: float
    delivery_charge: float
    final_amount: float

    payment_method: Optional[str] = None
    payment_status: Optional[str] = None
    delivery_address: Optional[str] = None

    estimated_delivery: Optional[str] = None
    actual_delivery: Optional[str] = None

    items: List[OrderItem] = Field(default_factory=list)
    tracking_number: Optional[str] = None


class OrderHistory(BaseModel):
    orders: List[OrderDetails]
    total_orders: int


class OrderStatus(BaseModel):
    order_id: str
    current_status: str
    status_history: List[dict]
    tracking_number: Optional[str] = None
    estimated_delivery: Optional[str] = None
    delivery_partner: Optional[str] = None

class OrderAddress(BaseModel):
    flatNo: Optional[str] = None
    landMark: Optional[str] = None
    address: Optional[str] = None
    pincode: Optional[int] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    houseType: Optional[str] = None


class OrderHistoryEvent(BaseModel):
    placedDate: Optional[str] = None
    assignedDate: Optional[str] = None
    deliveredDate: Optional[str] = None
    rejectedDate: Optional[str] = None
    canceledDate: Optional[str] = None


class OrderItemDetails(BaseModel):
    item_id: Optional[str] = None
    item_name: Optional[str] = None
    quantity: Optional[int] = None
    price: Optional[float] = None
    mrp_price: Optional[float] = None
    image_url: Optional[str] = None
    weight: Optional[float] = None


class OrderDetailsResponse(BaseModel):
    order_id: str
    order_date: Optional[str]
    status: str

    customer_name: Optional[str]
    customer_mobile: Optional[str]

    total_amount: float
    gst_amount: Optional[float]
    discount_amount: Optional[float]
    delivery_charge: float
    final_amount: float

    payment_method: str
    payment_status: Optional[str]

    address: Optional[OrderAddress]
    items: List[OrderItemDetails]

    order_history: List[OrderHistoryEvent]

    expected_delivery: Optional[str]
    time_slot: Optional[str]
    invoice_url: Optional[str]


# --------------------------------------------------
# TOOLS
# --------------------------------------------------

async def get_order_history(
    session_id: str = Field(..., description="User session ID"),
    limit: Optional[int] = Field(10, description="Number of orders to fetch"),
) -> OrderHistory:
    """
    Get user's order history with readable status and payment types.
    """

    user_id = get_user_id_by_session(session_id)
    if not user_id:
        raise ValueError("Invalid session")

    token = get_token_by_session(session_id)

    payload = {"userId": user_id}

    try:
        orders_data = await post(
            "/order-service/getAllOrders_customerId",
            payload,
            bearer_token=token,
        )

        print("orders history")
        print(json.dumps(orders_data, indent=2))

        if not isinstance(orders_data, list):
            return OrderHistory(orders=[], total_orders=0)

        orders: List[OrderDetails] = []

        for order in orders_data[:limit]:
            orders.append(
                OrderDetails(
                    order_id=order.get("orderId"),
                    order_date=order.get("orderDate"),
                    status=get_order_status(order.get("orderStatus")),

                    total_amount=order.get("subTotal", 0),
                    delivery_charge=order.get("deliveryFee", 0),
                    final_amount=order.get("grandTotal", 0),

                    payment_method=get_payment_type(order.get("paymentType")),
                    payment_status=order.get("paymentStatus"),
                    delivery_address=order.get("orderAddress"),

                    estimated_delivery=order.get("expectedDeliveryDate"),
                    actual_delivery=None,

                    items=[],
                    tracking_number=order.get("newOrderId"),
                )
            )

        return OrderHistory(orders=orders, total_orders=len(orders))

    except Exception as e:
        print("Order history error:", str(e.response))
        return OrderHistory(orders=[], total_orders=0)

async def get_order_details(
    order_id: str = Field(..., description="Order ID"),
    session_id: str = Field(..., description="User session ID"),
) -> OrderDetailsResponse:
    """
    Get complete order details by order ID.
    """

    user_id = get_user_id_by_session(session_id)
    if not user_id:
        raise ValueError("Invalid session")

    token = get_token_by_session(session_id)

    try:
        data = await get(
            f"/order-service/getOrdersByOrderId/{order_id}",
            params={},                 # ✅ FIXED
            bearer_token=token,
        )

        # API returns list with one object
        if not isinstance(data, list) or not data:
            raise ValueError("Order not found")

        order = data[0]

        return OrderDetailsResponse(
            order_id=order.get("orderId"),
            order_date=order.get("orderDate"),
            status=get_order_status(order.get("orderStatus")),

            customer_name=order.get("customerName"),
            customer_mobile=order.get("customerMobile"),

            total_amount=order.get("subTotal", 0),
            gst_amount=order.get("gstAmount"),
            discount_amount=order.get("discountAmount"),
            delivery_charge=order.get("deliveryFee", 0),
            final_amount=order.get("grandTotal", 0),

            payment_method=get_payment_type(order.get("paymentType")),
            payment_status=order.get("paymentStatus"),

            address=OrderAddress(**order["orderAddress"])
            if order.get("orderAddress") else None,

            items=[
                OrderItemDetails(
                    item_id=item.get("itemId"),
                    item_name=item.get("itemName"),
                    quantity=item.get("quantity"),
                    price=item.get("price"),
                    mrp_price=item.get("itemMrpPrice"),
                    image_url=item.get("itemUrl"),
                    weight=item.get("weight"),
                )
                for item in order.get("orderItems", []) or []
            ],

            order_history=[
                OrderHistoryEvent(
                    placedDate=h.get("placedDate"),
                    assignedDate=h.get("assignedDate"),
                    deliveredDate=h.get("deliveredDate"),
                    rejectedDate=h.get("rejectedDate"),
                    canceledDate=h.get("canceledDate"),
                )
                for h in order.get("orderHistory", []) or []
            ],

            expected_delivery=order.get("expectedDeliveryDate"),
            time_slot=order.get("timeSlot"),
            invoice_url=order.get("invoiceUrl"),
        )

    except Exception as e:
        raise ValueError(f"Failed to fetch order details: {str(e)}")


async def track_order(
    order_id: str = Field(..., description="Order ID to track"),
    session_id: str = Field(..., description="User session ID"),
) -> OrderStatus:

    user_id = get_user_id_by_session(session_id)
    if not user_id:
        raise ValueError("Invalid session")

    token = get_token_by_session(session_id)

    try:
        tracking_data = await get(
            "/order-service/track",
            params={"orderId": order_id, "customerId": user_id},
            bearer_token=token,
        )

        return OrderStatus(
            order_id=order_id,
            current_status=get_order_status(tracking_data.get("currentStatus")),
            status_history=tracking_data.get("statusHistory", []),
            tracking_number=tracking_data.get("trackingNumber"),
            estimated_delivery=tracking_data.get("estimatedDelivery"),
            delivery_partner=tracking_data.get("deliveryPartner"),
        )

    except Exception:
        return OrderStatus(
            order_id=order_id,
            current_status="Processing",
            status_history=[],
            tracking_number=None,
            estimated_delivery=None,
            delivery_partner=None,
        )


async def cancel_order(
    order_id: str = Field(...),
    session_id: str = Field(...),
    reason: Optional[str] = Field(None),
) -> dict:

    order_status = await track_order(order_id, session_id)

    if order_status.current_status in {"Delivered", "Cancelled"}:
        raise ValueError(f"Cannot cancel order. Current status: {order_status.current_status}")

    user_id = get_user_id_by_session(session_id)
    token = get_token_by_session(session_id)

    payload = {
        "orderId": order_id,
        "customerId": user_id,
        "reason": reason or "Customer requested cancellation",
    }

    response = await post(
        "/order-service/cancel",
        payload,
        bearer_token=token,
    )

    return {
        "success": True,
        "message": "Order cancelled successfully",
        "order_id": order_id,
        "refund_amount": response.get("refundAmount", 0),
        "refund_timeline": response.get("refundTimeline", "3-5 business days"),
    }


async def get_order_summary(session_id: str = Field(...)) -> dict:
    customer_id = get_user_id_by_session(session_id)
    token = get_token_by_session(session_id)

    return await get(
        "/api/cart-service/cart/customersCartItems",
        params={"customerId": customer_id},
        bearer_token=token,
    )


async def reorder_item(
    session_id: str = Field(...),
    item_id: str = Field(...),
) -> dict:

    customer_id = get_user_id_by_session(session_id)
    token = get_token_by_session(session_id)

    return await post(
        "/api/cart-service/cart/addAndIncrementCart",
        {"customerId": customer_id, "itemId": item_id},
        bearer_token=token,
    )


async def get_cancelled_orders(session_id: str = Field(...)) -> List[dict]:
    user_id = get_user_id_by_session(session_id)
    token = get_token_by_session(session_id)

    return await get(
        "/api/erice-service/order/userCancelOrdersList",
        params={"userId": user_id},
        bearer_token=token,
    )


async def get_exchange_orders(session_id: str = Field(...)) -> List[dict]:
    customer_id = get_user_id_by_session(session_id)
    token = get_token_by_session(session_id)

    return await get(
        f"/api/order-service/getExchangeOrders/{customer_id}",
        bearer_token=token,
    )


def register_tools(mcp_instance):
    global mcp
    mcp = mcp_instance

    mcp.tool()(get_order_history)
    mcp.tool()(get_order_details)
    mcp.tool()(track_order)
    mcp.tool()(cancel_order)
    mcp.tool()(get_order_summary)
    mcp.tool()(reorder_item)
    mcp.tool()(get_cancelled_orders)
    mcp.tool()(get_exchange_orders)
