from pydantic import BaseModel, Field
from mcp.server.fastmcp import FastMCP
from utils.http import post
from auth.token_store import create_session

# mcp: FastMCP  # injected from server.py
mcp = FastMCP(
    name="oxyloans-api"
)

# -------------------------------------------------
# Schemas
# -------------------------------------------------

class VerifyOTPAndAuthResponse(BaseModel):
    message: str
    session_id: str
    user_status: str


# -------------------------------------------------
# Tool
# -------------------------------------------------

@mcp.tool()
async def verify_otp_and_authenticate(
    country_code: str = Field(..., example="+91"),
    contact: str = Field(..., description="Mobile or WhatsApp number"),
    otp_session: str = Field(..., description="OTP session from send OTP"),
    otp_value: str = Field(..., description="OTP entered by user"),
    salt: str = Field(...),
    expiry_time: str = Field(..., description="OTP expiry time from backend"),
    registration_type: str = Field(..., pattern="^(mobile|whatsapp)$"),
    user_type: str = Field(..., pattern="^(Login|Register)$"),
) -> VerifyOTPAndAuthResponse:
    """
    Verify OTP for Login or Register and authenticate user.
    """

    payload = {
        "countryCode": country_code,
        "userType": user_type,
        "salt": salt,
        "expiryTime": expiry_time,
        "registrationType": registration_type,
    }

    if registration_type == "mobile":
        payload.update(
            {
                "mobileNumber": contact,
                "mobileOtpSession": otp_session,
                "mobileOtpValue": otp_value,
            }
        )
    else:
        payload.update(
            {
                "whatsappNumber": contact,
                "whatsappOtpSession": otp_session,
                "whatsappOtpValue": otp_value,
            }
        )

    data = await post(
        "/user-service/registerwithMobileAndWhatsappNumber",
        payload,
    )

    # -------------------------------------------------
    # Enforce CUSTOMER-only login
    # -------------------------------------------------
    if data.get("primaryType") != "CUSTOMER":
        raise ValueError("Only CUSTOMER users are allowed to login")

    access_token = data["accessToken"]
    user_status = data.get("userStatus", "UNKNOWN")

    # -------------------------------------------------
    # Create MCP session
    # -------------------------------------------------
    # Backend does not return userId explicitly.
    # Identity is embedded in the token.
    session_id = create_session(
        user_id="CUSTOMER",
        access_token=access_token,
    )

    return VerifyOTPAndAuthResponse(
        message="Authentication successful",
        session_id=session_id,
        user_status=user_status,
    )
