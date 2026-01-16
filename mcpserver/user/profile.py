from pydantic import BaseModel, Field
from typing import Optional
from utils.http import get, post
from auth.token_store import get_token_by_session

mcp = None

# -------------------------------------------------
# Schemas
# -------------------------------------------------

class CustomerProfile(BaseModel):
    id: str
    first_name: Optional[str]
    last_name: Optional[str]
    email: Optional[str]
    mobile_number: Optional[str]
    whatsapp_number: Optional[str]
    alternate_mobile_number: Optional[str]
    country_code: Optional[str]

    mobile_verified: bool
    whatsapp_verified: bool
    is_active: Optional[bool]

    address: Optional[str]
    flat_no: Optional[str]
    pincode: Optional[str]

    created_at: Optional[str]
    error_message: Optional[str]


class UpdateProfileResponse(BaseModel):
    success: bool
    message: str


# -------------------------------------------------
# Tools
# -------------------------------------------------

async def get_customer_profile(
    customer_id: str = Field(...),
) -> CustomerProfile:
    """
    Fetch customer profile details.
    """
    token = get_token_by_session(customer_id)
    if not token:
        raise ValueError("Invalid session")

    data = await get(
        "/api/user-service/customerProfileDetails",
        params={"customerId": customer_id},
        bearer_token=token,
    )

    return CustomerProfile(
        id=data.get("id"),
        first_name=data.get("firstName"),
        last_name=data.get("lastName"),
        email=data.get("email"),
        mobile_number=data.get("mobileNumber"),
        whatsapp_number=data.get("whatsappNumber"),
        alternate_mobile_number=data.get("alterMobileNumber"),
        country_code=data.get("countryCode"),
        mobile_verified=data.get("mobileVerified", False),
        whatsapp_verified=data.get("whatsappVerified", False),
        is_active=data.get("isActive"),
        address=data.get("address"),
        flat_no=data.get("flatNo"),
        pincode=data.get("pincode"),
        created_at=data.get("created_at"),
        error_message=data.get("errorMessage") or data.get("errorMeassage"),
    )


async def update_customer_profile(
    customer_id: str,
    first_name: str,
    last_name: str,
    email: str,
    mobile_number: str,
    whatsapp_number: str,
    alternate_mobile_number: Optional[str] = None,
) -> UpdateProfileResponse:
    """
    Update customer profile details.
    """
    token = get_token_by_session(customer_id)
    if not token:
        raise ValueError("Invalid session")

    payload = {
        "customerId": customer_id,
        "userFirstName": first_name,
        "userLastName": last_name,
        "customerEmail": email,
        "mobileNumber": mobile_number,
        "whatsappNumber": whatsapp_number,
        "alterMobileNumber": alternate_mobile_number,
    }

    data = await post(
        "/api/user-service/profileUpdate",
        payload,
        bearer_token=token,
    )

    return UpdateProfileResponse(
        success=data.get("success", True),
        message=data.get("message", "Profile updated successfully"),
    )


def register_tools(mcp_instance):
    global mcp
    mcp = mcp_instance
    mcp.tool()(get_customer_profile)
    mcp.tool()(update_customer_profile)
