from pydantic import BaseModel, Field
from typing import Optional, List
from utils.http import get, post
from auth.token_store import get_token_by_session, get_user_id_by_session

mcp = None

# -------------------------------------------------
# Schemas
# -------------------------------------------------

class OrderValidation(BaseModel):
    can_place_order: bool
    minimum_order_amount: float
    current_cart_value: float
    missing_amount: Optional[float]
    delivery_available: bool
    address_valid: bool
    payment_methods_available: List[str]
    estimated_delivery_time: Optional[str]
    message: str

class DeliveryCheck(BaseModel):
    pincode: str
    delivery_available: bool
    estimated_delivery_days: Optional[int]
    delivery_charge: Optional[float]
    cod_available: bool
    message: str

class OrderSummary(BaseModel):
    order_id: Optional[str]
    total_amount: float
    delivery_charge: float
    discount_amount: float
    final_amount: float
    payment_method: str
    delivery_address: str
    estimated_delivery: Optional[str]
    status: str

# -------------------------------------------------
# Tools
# -------------------------------------------------

async def check_order_conditions(
    session_id: str = Field(..., description="User session ID"),
    address_id: Optional[str] = Field(None, description="Delivery address ID")
) -> OrderValidation:
    """
    Check all conditions required to place an order including cart value, delivery availability, and payment options.
    """
    user_id = get_user_id_by_session(session_id)
    if not user_id:
        raise ValueError("Invalid session")
    
    token = get_token_by_session(session_id)
    
    # Get cart details
    cart_data = await get(
        "/cart-service/cart/userCartInfo",
        params={"customerId": user_id},
        bearer_token=token,
    )
    
    current_cart_value = cart_data.get("amountToPay", 0)
    minimum_order_amount = 200.0  # Default minimum order
    
    # Check delivery availability if address provided
    delivery_available = True
    address_valid = True
    
    if address_id:
        try:
            # Get address details
            address_data = await get(
                "/user-service/address/details",
                params={"addressId": address_id},
                bearer_token=token,
            )
            pincode = address_data.get("pincode")
            
            # Check delivery availability for pincode
            delivery_check = await get(
                "/delivery-service/check",
                params={"pincode": pincode},
                bearer_token=token,
            )
            delivery_available = delivery_check.get("available", True)
        except:
            address_valid = False
            delivery_available = False
    
    can_place_order = (
        current_cart_value >= minimum_order_amount and
        delivery_available and
        address_valid and
        len(cart_data.get("customerCartResponseList", [])) > 0
    )
    
    missing_amount = max(0, minimum_order_amount - current_cart_value) if current_cart_value < minimum_order_amount else None
    
    payment_methods = ["COD", "UPI", "Card", "Wallet"]
    
    message = "Order can be placed" if can_place_order else "Order conditions not met"
    if missing_amount:
        message = f"Add items worth ₹{missing_amount:.2f} more to place order"
    elif not delivery_available:
        message = "Delivery not available for selected address"
    elif not address_valid:
        message = "Please select a valid delivery address"
    
    return OrderValidation(
        can_place_order=can_place_order,
        minimum_order_amount=minimum_order_amount,
        current_cart_value=current_cart_value,
        missing_amount=missing_amount,
        delivery_available=delivery_available,
        address_valid=address_valid,
        payment_methods_available=payment_methods,
        estimated_delivery_time="2-3 business days" if delivery_available else None,
        message=message
    )

async def check_delivery_availability(
    pincode: str = Field(..., description="Pincode to check delivery"),
    session_id: str = Field(..., description="User session ID")
) -> DeliveryCheck:
    """
    Check if delivery is available for a specific pincode and get delivery details.
    """
    token = get_token_by_session(session_id)
    
    try:
        delivery_data = await get(
            "/delivery-service/pincode/check",
            params={"pincode": pincode},
            bearer_token=token,
        )
        
        return DeliveryCheck(
            pincode=pincode,
            delivery_available=delivery_data.get("available", True),
            estimated_delivery_days=delivery_data.get("deliveryDays", 3),
            delivery_charge=delivery_data.get("deliveryCharge", 50.0),
            cod_available=delivery_data.get("codAvailable", True),
            message=delivery_data.get("message", "Delivery available")
        )
    except:
        # Default response if service unavailable
        return DeliveryCheck(
            pincode=pincode,
            delivery_available=True,
            estimated_delivery_days=3,
            delivery_charge=50.0,
            cod_available=True,
            message="Delivery available (default)"
        )

async def place_order(
    session_id: str = Field(..., description="User session ID"),
    address_id: str = Field(..., description="Delivery address ID"),
    payment_method: str = Field(..., description="Payment method (COD, UPI, Card, Wallet)"),
    special_instructions: Optional[str] = Field(None, description="Special delivery instructions")
) -> OrderSummary:
    """
    Place an order with the items in cart using specified address and payment method.
    """
    user_id = get_user_id_by_session(session_id)
    if not user_id:
        raise ValueError("Invalid session")
    
    token = get_token_by_session(session_id)
    
    # First validate order conditions
    validation = await check_order_conditions(session_id, address_id)
    if not validation.can_place_order:
        raise ValueError(f"Cannot place order: {validation.message}")
    
    # Get cart details for order
    cart_data = await get(
        "/cart-service/cart/userCartInfo",
        params={"customerId": user_id},
        bearer_token=token,
    )
    
    # Get address details
    address_data = await get(
        "/user-service/address/details",
        params={"addressId": address_id},
        bearer_token=token,
    )
    
    order_payload = {
        "customerId": user_id,
        "addressId": address_id,
        "paymentMethod": payment_method,
        "totalAmount": cart_data.get("amountToPay", 0),
        "items": cart_data.get("customerCartResponseList", []),
        "specialInstructions": special_instructions,
        "deliveryCharge": 50.0,  # Default delivery charge
    }
    
    try:
        order_response = await post(
            "/order-service/place",
            order_payload,
            bearer_token=token,
        )
        
        delivery_address = f"{address_data.get('flatNo', '')}, {address_data.get('address', '')}, {address_data.get('pincode', '')}"
        
        return OrderSummary(
            order_id=order_response.get("orderId"),
            total_amount=cart_data.get("totalCartValue", 0),
            delivery_charge=50.0,
            discount_amount=cart_data.get("discountedByFreeItems", 0),
            final_amount=cart_data.get("amountToPay", 0) + 50.0,
            payment_method=payment_method,
            delivery_address=delivery_address,
            estimated_delivery="2-3 business days",
            status="Order Placed Successfully"
        )
    except Exception as e:
        raise ValueError(f"Failed to place order: {str(e)}")

def register_tools(mcp_instance):
    global mcp
    mcp = mcp_instance
    mcp.tool()(check_order_conditions)
    mcp.tool()(check_delivery_availability)
    mcp.tool()(place_order)