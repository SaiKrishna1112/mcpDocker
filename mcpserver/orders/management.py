from pydantic import BaseModel, Field
from typing import Optional, List
from utils.http import get, post
from auth.token_store import get_token_by_session, get_user_id_by_session

mcp = None

# -------------------------------------------------
# Schemas
# -------------------------------------------------

class OrderItem(BaseModel):
    item_id: str
    item_name: str
    quantity: int
    price: float
    total_price: float

class OrderDetails(BaseModel):
    order_id: str
    order_date: str
    status: str
    total_amount: float
    delivery_charge: float
    final_amount: float
    payment_method: str
    payment_status: str
    delivery_address: str
    estimated_delivery: Optional[str]
    actual_delivery: Optional[str]
    items: List[OrderItem]
    tracking_number: Optional[str]

class OrderHistory(BaseModel):
    orders: List[OrderDetails]
    total_orders: int

class OrderStatus(BaseModel):
    order_id: str
    current_status: str
    status_history: List[dict]
    tracking_number: Optional[str]
    estimated_delivery: Optional[str]
    delivery_partner: Optional[str]

# -------------------------------------------------
# Tools
# -------------------------------------------------

async def get_order_history(
    session_id: str = Field(..., description="User session ID"),
    limit: Optional[int] = Field(10, description="Number of orders to fetch")
) -> OrderHistory:
    """
    Get user's order history with details of all past orders.
    """
    user_id = get_user_id_by_session(session_id)
    if not user_id:
        raise ValueError("Invalid session")
    
    token = get_token_by_session(session_id)
    
    try:
        orders_data = await get(
            "/order-service/history",
            params={"customerId": user_id, "limit": limit},
            bearer_token=token,
        )
        
        orders = []
        for order in orders_data.get("orders", []):
            order_items = [
                OrderItem(
                    item_id=item.get("itemId"),
                    item_name=item.get("itemName"),
                    quantity=item.get("quantity"),
                    price=item.get("price"),
                    total_price=item.get("totalPrice")
                )
                for item in order.get("items", [])
            ]
            
            orders.append(OrderDetails(
                order_id=order.get("orderId"),
                order_date=order.get("orderDate"),
                status=order.get("status"),
                total_amount=order.get("totalAmount"),
                delivery_charge=order.get("deliveryCharge", 0),
                final_amount=order.get("finalAmount"),
                payment_method=order.get("paymentMethod"),
                payment_status=order.get("paymentStatus"),
                delivery_address=order.get("deliveryAddress"),
                estimated_delivery=order.get("estimatedDelivery"),
                actual_delivery=order.get("actualDelivery"),
                items=order_items,
                tracking_number=order.get("trackingNumber")
            ))
        
        return OrderHistory(
            orders=orders,
            total_orders=len(orders)
        )
    except Exception as e:
        # Return empty history if service unavailable
        return OrderHistory(orders=[], total_orders=0)

async def track_order(
    order_id: str = Field(..., description="Order ID to track"),
    session_id: str = Field(..., description="User session ID")
) -> OrderStatus:
    """
    Track a specific order and get its current status and tracking details.
    """
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
            current_status=tracking_data.get("currentStatus", "Processing"),
            status_history=tracking_data.get("statusHistory", []),
            tracking_number=tracking_data.get("trackingNumber"),
            estimated_delivery=tracking_data.get("estimatedDelivery"),
            delivery_partner=tracking_data.get("deliveryPartner")
        )
    except Exception as e:
        # Return default status if service unavailable
        return OrderStatus(
            order_id=order_id,
            current_status="Processing",
            status_history=[{"status": "Order Placed", "timestamp": "2024-01-01T10:00:00Z"}],
            tracking_number=None,
            estimated_delivery="2-3 business days",
            delivery_partner="Standard Delivery"
        )

async def cancel_order(
    order_id: str = Field(..., description="Order ID to cancel"),
    session_id: str = Field(..., description="User session ID"),
    reason: Optional[str] = Field(None, description="Reason for cancellation")
) -> dict:
    """
    Cancel an order if it's eligible for cancellation.
    """
    user_id = get_user_id_by_session(session_id)
    if not user_id:
        raise ValueError("Invalid session")
    
    token = get_token_by_session(session_id)
    
    # First check if order can be cancelled
    order_status = await track_order(order_id, session_id)
    
    if order_status.current_status in ["Delivered", "Cancelled", "Shipped"]:
        raise ValueError(f"Cannot cancel order. Current status: {order_status.current_status}")
    
    try:
        cancel_payload = {
            "orderId": order_id,
            "customerId": user_id,
            "reason": reason or "Customer requested cancellation"
        }
        
        cancel_response = await post(
            "/order-service/cancel",
            cancel_payload,
            bearer_token=token,
        )
        
        return {
            "success": True,
            "message": "Order cancelled successfully",
            "order_id": order_id,
            "refund_amount": cancel_response.get("refundAmount", 0),
            "refund_timeline": cancel_response.get("refundTimeline", "3-5 business days")
        }
    except Exception as e:
        raise ValueError(f"Failed to cancel order: {str(e)}")

async def get_order_summary(
    session_id: str = Field(...),
) -> dict:
    """
    Fetch cart items for order summary (Checkout Step 2).
    """
    customer_id = get_user_id_by_session(session_id)
    if not customer_id:
        raise ValueError("Invalid session")
        
    token = get_token_by_session(session_id)
    if not token:
        raise ValueError("No authentication token found")

    data = await get(
        "/api/cart-service/cart/customersCartItems",
        params={"customerId": customer_id},
        bearer_token=token,
    )

    return data

async def reorder_item(
    session_id: str = Field(...),
    item_id: str = Field(...),
) -> dict:
    """
    Add item to cart for reorder functionality.
    """
    customer_id = get_user_id_by_session(session_id)
    if not customer_id:
        raise ValueError("Invalid session")
        
    token = get_token_by_session(session_id)
    if not token:
        raise ValueError("No authentication token found")

    payload = {
        "customerId": customer_id,
        "itemId": item_id,
    }

    data = await post(
        "/api/cart-service/cart/addAndIncrementCart",
        payload,
        bearer_token=token,
    )

    return data

async def get_cancelled_orders(
    session_id: str = Field(...),
) -> List[dict]:
    """
    Fetch all cancelled orders for the user.
    """
    user_id = get_user_id_by_session(session_id)
    if not user_id:
        raise ValueError("Invalid session")
        
    token = get_token_by_session(session_id)
    if not token:
        raise ValueError("No authentication token found")

    data = await get(
        "/api/erice-service/order/userCancelOrdersList",
        params={"userId": user_id},
        bearer_token=token,
    )

    return data

async def get_exchange_orders(
    session_id: str = Field(...),
) -> List[dict]:
    """
    Fetch all exchange orders for the user.
    """
    customer_id = get_user_id_by_session(session_id)
    if not customer_id:
        raise ValueError("Invalid session")
        
    token = get_token_by_session(session_id)
    if not token:
        raise ValueError("No authentication token found")

    data = await get(
        f"/api/order-service/getExchangeOrders/{customer_id}",
        bearer_token=token,
    )

    return data

def register_tools(mcp_instance):
    global mcp
    mcp = mcp_instance
    mcp.tool()(get_order_history)
    mcp.tool()(track_order)
    mcp.tool()(cancel_order)
    mcp.tool()(get_order_summary)
    mcp.tool()(reorder_item)
    mcp.tool()(get_cancelled_orders)
    mcp.tool()(get_exchange_orders)