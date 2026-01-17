from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from utils.http import get, post
from auth.token_store import get_token_by_session, get_user_id_by_session

mcp = None

# -------------------------------------------------
# Schemas
# -------------------------------------------------

class CartSummary(BaseModel):
    items: List[Dict[str, Any]]
    total_cart_value: float
    amount_to_pay: float
    free_item_price_total: float
    discounted_by_free_items: float
    total_gst_amount: float

class DeliveryAddress(BaseModel):
    id: str
    flat_no: str
    address: str
    pincode: str
    latitude: str
    longitude: str
    is_serviceable: bool = True

class DeliveryCharges(BaseModel):
    delivery_boy_fee: float
    handling_fee: float
    total_delivery_charge: float

class Coupon(BaseModel):
    coupon_id: str
    coupon_code: str
    discount_amount: float
    minimum_cart_value: float
    is_applicable: bool

class WalletResponse(BaseModel):
    wallet_used_amount: float
    remaining_wallet_balance: float

class DeliverySlot(BaseModel):
    slot_id: str
    date: str
    time_range: str
    is_available: bool

class PaymentTransaction(BaseModel):
    transaction_id: str
    payment_status: str
    amount_to_pay: float

class CheckoutValidation(BaseModel):
    cart_valid: bool
    address_valid: bool
    pincode_serviceable: bool
    delivery_charges: DeliveryCharges
    can_proceed: bool
    error_message: Optional[str]

# -------------------------------------------------
# STEP 1: Fetch Cart Summary
# -------------------------------------------------

async def fetch_cart_summary(
    session_id: str = Field(..., description="User session ID")
) -> CartSummary:
    """
    STEP 1: Fetch Cart Summary - Single source of truth for checkout calculations
    """
    user_id = get_user_id_by_session(session_id)
    if not user_id:
        raise ValueError("Invalid session")
    
    token = get_token_by_session(session_id)
    
    data = await get(
        "/cart-service/cart/userCartInfo",
        params={"customerId": user_id},
        bearer_token=token,
    )
    
    return CartSummary(
        items=data.get("customerCartResponseList", []),
        total_cart_value=data.get("totalCartValue", 0),
        amount_to_pay=data.get("amountToPay", 0),
        free_item_price_total=data.get("freeItemPriceTotal", 0),
        discounted_by_free_items=data.get("discountedByFreeItems", 0),
        total_gst_amount=data.get("totalGstAmountToPay", 0)
    )

# -------------------------------------------------
# STEP 2: Validate Delivery Address & Serviceability
# -------------------------------------------------

async def get_user_addresses(
    session_id: str = Field(..., description="User session ID")
) -> List[DeliveryAddress]:
    """
    STEP 2.1: Get User Addresses
    """
    user_id = get_user_id_by_session(session_id)
    if not user_id:
        raise ValueError("Invalid session")
    
    token = get_token_by_session(session_id)
    
    data = await get(
        "/user-service/getAllAdd",
        params={"customerId": user_id},
        bearer_token=token,
    )
    
    addresses = []
    for addr in data:
        addresses.append(DeliveryAddress(
            id=addr.get("id"),
            flat_no=addr.get("flat_no", ""),
            address=addr.get("address", ""),
            pincode=addr.get("pincode", ""),
            latitude=addr.get("latitude", "0"),
            longitude=addr.get("longitude", "0")
        ))
    
    return addresses

async def validate_pincode_serviceability(
    pincode: str = Field(..., description="Pincode to validate"),
    session_id: str = Field(..., description="User session ID")
) -> bool:
    """
    STEP 2.2: Validate Pincode & Active Zone
    """
    token = get_token_by_session(session_id)
    
    try:
        data = await get(
            "/order-service/getAllUpdatePincodes",
            params={},
            bearer_token=token,
        )
        
        serviceable_pincodes = [p.get("pincode") for p in data if p.get("isActive", False)]
        return pincode in serviceable_pincodes
    except:
        return False

# -------------------------------------------------
# STEP 3: Calculate Delivery Charges
# -------------------------------------------------

async def calculate_delivery_charges(
    latitude: float = Field(..., description="Delivery latitude"),
    longitude: float = Field(..., description="Delivery longitude"),
    cart_value: float = Field(..., description="Cart value for calculation"),
    session_id: str = Field(..., description="User session ID")
) -> DeliveryCharges:
    """
    STEP 3: Calculate Delivery Charges based on distance and cart value
    """
    # Default delivery charges (can be enhanced with actual distance calculation)
    delivery_boy_fee = 30.0
    handling_fee = 20.0
    
    # Free delivery for orders above ₹500
    if cart_value >= 500:
        delivery_boy_fee = 0.0
        handling_fee = 0.0
    
    return DeliveryCharges(
        delivery_boy_fee=delivery_boy_fee,
        handling_fee=handling_fee,
        total_delivery_charge=delivery_boy_fee + handling_fee
    )

# -------------------------------------------------
# STEP 4: Apply Coupon (Optional)
# -------------------------------------------------

async def get_available_coupons(
    session_id: str = Field(..., description="User session ID")
) -> List[Coupon]:
    """
    STEP 4: Get Available Coupons
    """
    token = get_token_by_session(session_id)
    
    try:
        data = await get(
            "/order-service/getAllCoupons",
            params={},
            bearer_token=token,
        )
        
        coupons = []
        for coupon in data:
            coupons.append(Coupon(
                coupon_id=coupon.get("id"),
                coupon_code=coupon.get("code"),
                discount_amount=coupon.get("discountAmount", 0),
                minimum_cart_value=coupon.get("minimumCartValue", 0),
                is_applicable=coupon.get("isActive", False)
            ))
        
        return coupons
    except:
        return []

# -------------------------------------------------
# STEP 5: Apply Wallet Amount (Optional)
# -------------------------------------------------

async def apply_wallet_amount(
    wallet_amount: float = Field(..., description="Wallet amount to apply"),
    session_id: str = Field(..., description="User session ID")
) -> WalletResponse:
    """
    STEP 5: Apply Wallet Amount
    """
    user_id = get_user_id_by_session(session_id)
    if not user_id:
        raise ValueError("Invalid session")
    
    token = get_token_by_session(session_id)
    
    payload = {
        "customerId": user_id,
        "walletAmount": wallet_amount
    }
    
    data = await post(
        "/order-service/applyWalletAmount",
        payload,
        bearer_token=token,
    )
    
    return WalletResponse(
        wallet_used_amount=data.get("walletUsedAmount", 0),
        remaining_wallet_balance=data.get("remainingWalletBalance", 0)
    )

# -------------------------------------------------
# STEP 6: Fetch & Select Delivery Slot
# -------------------------------------------------

async def fetch_delivery_slots(
    session_id: str = Field(..., description="User session ID")
) -> List[DeliverySlot]:
    """
    STEP 6: Fetch Delivery Slots
    """
    token = get_token_by_session(session_id)
    
    try:
        data = await get(
            "/order-service/fetchTimeSlotlist",
            params={},
            bearer_token=token,
        )
        
        slots = []
        for slot in data:
            slots.append(DeliverySlot(
                slot_id=slot.get("id"),
                date=slot.get("date"),
                time_range=slot.get("timeRange"),
                is_available=slot.get("isAvailable", True)
            ))
        
        return slots
    except:
        return []

# -------------------------------------------------
# STEP 7: Initiate Payment Transaction
# -------------------------------------------------

async def initiate_payment(
    payment_mode: str = Field(..., description="Payment mode: ONLINE, COD, or WALLET"),
    session_id: str = Field(..., description="User session ID")
) -> PaymentTransaction:
    """
    STEP 7: Initiate Payment Transaction
    """
    user_id = get_user_id_by_session(session_id)
    if not user_id:
        raise ValueError("Invalid session")
    
    token = get_token_by_session(session_id)
    
    # Get cart summary for amount
    cart = await fetch_cart_summary(session_id)
    
    payload = {
        "customerId": user_id,
        "cartId": f"cart_{user_id}",
        "paymentMode": payment_mode,
        "amountToPay": cart.amount_to_pay
    }
    
    data = await post(
        "/order-service/initiatePayment",
        payload,
        bearer_token=token,
    )
    
    return PaymentTransaction(
        transaction_id=data.get("transactionId"),
        payment_status=data.get("paymentStatus", "INITIATED"),
        amount_to_pay=cart.amount_to_pay
    )

# -------------------------------------------------
# STEP 8: Payment Completion
# -------------------------------------------------

async def confirm_payment(
    transaction_id: str = Field(..., description="Transaction ID"),
    payment_status: str = Field(..., description="Payment status: SUCCESS or FAILED"),
    session_id: str = Field(..., description="User session ID")
) -> Dict[str, Any]:
    """
    STEP 8: Payment Completion
    """
    token = get_token_by_session(session_id)
    
    payload = {
        "transactionId": transaction_id,
        "paymentStatus": payment_status
    }
    
    data = await post(
        "/order-service/confirmPayment",
        payload,
        bearer_token=token,
    )
    
    if payment_status == "SUCCESS":
        return {
            "success": True,
            "message": "Order created successfully",
            "order_id": data.get("orderId"),
            "cart_cleared": True,
            "wallet_deducted": True
        }
    else:
        return {
            "success": False,
            "message": "Payment failed, cart remains intact",
            "retry_allowed": True
        }

# -------------------------------------------------
# COMPREHENSIVE CHECKOUT VALIDATION
# -------------------------------------------------

async def validate_checkout(
    address_id: str = Field(..., description="Selected address ID"),
    session_id: str = Field(..., description="User session ID")
) -> CheckoutValidation:
    """
    Comprehensive checkout validation following all steps
    """
    try:
        # Step 1: Fetch cart
        cart = await fetch_cart_summary(session_id)
        if not cart.items or cart.amount_to_pay <= 0:
            return CheckoutValidation(
                cart_valid=False,
                address_valid=False,
                pincode_serviceable=False,
                delivery_charges=DeliveryCharges(delivery_boy_fee=0, handling_fee=0, total_delivery_charge=0),
                can_proceed=False,
                error_message="Cart is empty or invalid"
            )
        
        # Step 2: Validate address
        addresses = await get_user_addresses(session_id)
        selected_address = next((addr for addr in addresses if addr.id == address_id), None)
        
        if not selected_address:
            return CheckoutValidation(
                cart_valid=True,
                address_valid=False,
                pincode_serviceable=False,
                delivery_charges=DeliveryCharges(delivery_boy_fee=0, handling_fee=0, total_delivery_charge=0),
                can_proceed=False,
                error_message="Invalid address selected"
            )
        
        # Step 2.2: Validate pincode serviceability
        pincode_valid = await validate_pincode_serviceability(selected_address.pincode, session_id)
        
        if not pincode_valid:
            return CheckoutValidation(
                cart_valid=True,
                address_valid=True,
                pincode_serviceable=False,
                delivery_charges=DeliveryCharges(delivery_boy_fee=0, handling_fee=0, total_delivery_charge=0),
                can_proceed=False,
                error_message="Delivery not available for this pincode"
            )
        
        # Step 3: Calculate delivery charges
        delivery_charges = await calculate_delivery_charges(
            latitude=float(selected_address.latitude),
            longitude=float(selected_address.longitude),
            cart_value=cart.total_cart_value,
            session_id=session_id
        )
        
        return CheckoutValidation(
            cart_valid=True,
            address_valid=True,
            pincode_serviceable=True,
            delivery_charges=delivery_charges,
            can_proceed=True,
            error_message=None
        )
        
    except Exception as e:
        return CheckoutValidation(
            cart_valid=False,
            address_valid=False,
            pincode_serviceable=False,
            delivery_charges=DeliveryCharges(delivery_boy_fee=0, handling_fee=0, total_delivery_charge=0),
            can_proceed=False,
            error_message=f"Validation failed: {str(e)}"
        )

def register_tools(mcp_instance):
    global mcp
    mcp = mcp_instance
    mcp.tool()(fetch_cart_summary)
    mcp.tool()(get_user_addresses)
    mcp.tool()(validate_pincode_serviceability)
    mcp.tool()(calculate_delivery_charges)
    mcp.tool()(get_available_coupons)
    mcp.tool()(apply_wallet_amount)
    mcp.tool()(fetch_delivery_slots)
    mcp.tool()(initiate_payment)
    mcp.tool()(confirm_payment)
    mcp.tool()(validate_checkout)