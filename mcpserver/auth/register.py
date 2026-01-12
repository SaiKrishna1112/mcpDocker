from pydantic import BaseModel, Field
from fastmcp import FastMCP
from utils.http import post

# mcp: FastMCP  # injected from server.py
mcp = FastMCP(
    name="oxyloans-api"
)

# -------------------------
# Schemas
# -------------------------

class RegisterSendOTPResponse(BaseModel):
    otpSession: str
    salt: str
    otpGeneratedTime: str


# -------------------------
# Tool
# -------------------------

@mcp.tool(read_only=False)
async def send_register_otp(
    country_code: str = Field(..., json_schema_extra={"example": "+91"}),
    mobile_or_whatsapp: str = Field(..., description="Mobile or WhatsApp number"),
    registration_type: str = Field(..., pattern="^(sms|whatsapp)$"),
    referrer_id: str | None = Field(
        None,
        description="Optional referral ID",
    ),
) -> RegisterSendOTPResponse:
    """
    Send OTP for user registration via SMS or WhatsApp.
    """
    payload = {
        "countryCode": country_code,
        "userType": "Register",
        "registrationType": registration_type,
        "referrerIdForMobile": referrer_id,
    }

    if registration_type == "sms":
        payload["mobileNumber"] = mobile_or_whatsapp
    else:
        payload["whatsappNumber"] = mobile_or_whatsapp

    data = await post(
        "/user-service/registerwithMobileAndWhatsappNumber",
        payload,
    )

    return RegisterSendOTPResponse(
        otpSession=data.get("mobileOtpSession")
        or data.get("whatsappOtpSession"),
        salt=data["salt"],
        otpGeneratedTime=data["otpGeneratedTime"],
    )
