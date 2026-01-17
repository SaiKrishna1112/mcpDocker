# OxyLoans MCP Server - Complete API Reference

## 🔧 Server Status
- **Server Name**: oxyloans-api
- **Transport**: SSE (Server-Sent Events)
- **Host**: 0.0.0.0
- **Port**: 8001

## 📋 Complete API List

### 🔐 Authentication APIs (auth/)

#### Simple Authentication
- `simple_login(mobile_number, country_code="+91")` - Quick login without OTP

#### OTP-based Authentication
- `send_login_otp(country_code, mobile_or_whatsapp, registration_type)` - Send login OTP
- `verify_login_otp(country_code, mobile_or_whatsapp, otp_session, otp_value, salt, expiry_time, registration_type)` - Verify login OTP
- `send_register_otp(country_code, mobile_or_whatsapp, registration_type, referrer_id?)` - Send registration OTP
- `verify_otp_and_authenticate(country_code, contact, otp_session, otp_value, salt, expiry_time, registration_type, user_type)` - Verify OTP and authenticate

### 🛍️ Product APIs (products/)

#### Public Access
- `get_trending_products(limit=20)` - Get trending products (no auth required)

#### Authenticated Access
- `dynamic_product_search(q)` - Search products by keyword
- `get_product_images(item_id)` - Get product images
- `get_combo_item_details(item_id)` - Get combo item details

#### AI-Powered
- `get_product_suggestions(query, budget=1000)` - AI-powered product recommendations

### 👤 User Management APIs (user/)

#### Profile Management
- `get_customer_profile(session_id)` - Get user profile details
- `update_customer_profile(session_id, first_name, last_name, email, mobile_number, whatsapp_number, alternate_mobile_number?)` - Update profile

#### Address Management
- `view_address_list(session_id)` - View all saved addresses
- `add_address(session_id, flat_no, address, landmark, pincode, address_type)` - Add new address

### 🛒 Cart Management APIs (cart/)

- `add_to_cart(session_id, item_id, cart_quantity, status?)` - Add/increment item in cart
- `view_user_cart(session_id)` - View cart contents and totals
- `decrement_cart_item(session_id, item_id)` - Decrease item quantity
- `remove_cart_item(session_id, cart_id)` - Remove item from cart

### 📦 Order Management APIs (orders/)

#### Order Validation & Conditions
- `check_order_conditions(session_id, address_id?)` - Validate all order requirements
- `check_delivery_availability(pincode, session_id)` - Check delivery for pincode
- `place_order(session_id, address_id, payment_method, special_instructions?)` - Place order

#### Order Tracking & History
- `get_order_history(session_id, limit=10)` - Get user's order history
- `track_order(order_id, session_id)` - Track specific order status
- `cancel_order(order_id, session_id, reason?)` - Cancel order

#### Complete Checkout Flow
- `fetch_cart_summary(session_id)` - **STEP 1**: Get cart summary
- `get_user_addresses(session_id)` - **STEP 2.1**: Get user addresses
- `validate_pincode_serviceability(pincode, session_id)` - **STEP 2.2**: Validate pincode
- `calculate_delivery_charges(latitude, longitude, cart_value, session_id)` - **STEP 3**: Calculate delivery
- `get_available_coupons(session_id)` - **STEP 4**: Get coupons
- `apply_wallet_amount(wallet_amount, session_id)` - **STEP 5**: Apply wallet
- `fetch_delivery_slots(session_id)` - **STEP 6**: Get delivery slots
- `initiate_payment(payment_mode, session_id)` - **STEP 7**: Initiate payment
- `confirm_payment(transaction_id, payment_status, session_id)` - **STEP 8**: Confirm payment
- `validate_checkout(address_id, session_id)` - **Complete validation**: All-in-one checkout validation

### 🔧 Utility APIs

- `hello_world()` - Test server connectivity

## 📊 API Categories Summary

| Category | Count | Description |
|----------|-------|-------------|
| **Authentication** | 5 | Login, registration, OTP verification |
| **Products** | 4 | Search, browse, get details |
| **User Management** | 3 | Profile and address management |
| **Cart Operations** | 4 | Add, view, modify cart items |
| **Order Management** | 3 | Place, track, cancel orders |
| **Checkout Flow** | 10 | Complete checkout process |
| **Utility** | 1 | Server testing |
| **TOTAL** | **30** | **Complete e-commerce functionality** |

## 🚀 Quick Start Examples

### 1. Browse Products (No Auth)
```python
# Get trending products
products = await get_trending_products(limit=10)
```

### 2. User Authentication
```python
# Simple login
result = await simple_login(mobile_number="8125861874")
session_id = result["session_id"]

# Or OTP-based login
otp_response = await send_login_otp("+91", "8125861874", "sms")
login_result = await verify_login_otp("+91", "8125861874", otp_response.otpSession, "123456", otp_response.salt, otp_response.otpGeneratedTime, "mobile")
```

### 3. Shopping Flow
```python
# Search products
products = await dynamic_product_search("rice")

# Add to cart
await add_to_cart(session_id, "item_123", 2)

# View cart
cart = await view_user_cart(session_id)
```

### 4. Complete Checkout
```python
# Validate checkout
validation = await validate_checkout("address_123", session_id)

if validation.can_proceed:
    # Initiate payment
    payment = await initiate_payment("COD", session_id)
    
    # Confirm payment
    result = await confirm_payment(payment.transaction_id, "SUCCESS", session_id)
```

## ✅ All APIs Status: **IMPLEMENTED & REGISTERED**

All 30 APIs are properly implemented with:
- ✅ Proper schemas and validation
- ✅ Error handling
- ✅ Authentication integration
- ✅ Registered in server.py
- ✅ Complete documentation