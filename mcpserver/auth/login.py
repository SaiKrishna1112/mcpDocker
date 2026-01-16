from pydantic import BaseModel, Field
from utils.http import post
from auth.token_store import create_session

mcp = None  # Will be injected from server.py

class SendOTPResponse(BaseModel):
    otpSession: str
    salt: str
    otpGeneratedTime: str

class VerifyOTPResponse(BaseModel):
    message: str
    session_id: str

async def send_login_otp(
    country_code: str = Field(..., json_schema_extra={"example": "+91"}),
    mobile_or_whatsapp: str = Field(..., description="Mobile or WhatsApp number"),
    registration_type: str = Field(..., pattern="^(sms|whatsapp)$"),
) -> SendOTPResponse:
    """
    Send OTP via SMS or WhatsApp for login/registration.
    """
    payload = {
        "countryCode": country_code,
        "userType": "Login",
        "registrationType": registration_type,
    }

    if registration_type == "sms":
        payload["mobileNumber"] = mobile_or_whatsapp
    else:
        payload["whatsappNumber"] = mobile_or_whatsapp

    data = await post(
        "/user-service/registerwithMobileAndWhatsappNumber",
        payload,
    )

    return SendOTPResponse(
        otpSession=data.get("mobileOtpSession")
        or data.get("whatsappOtpSession"),
        salt=data["salt"],
        otpGeneratedTime=data["otpGeneratedTime"],
    )

async def verify_login_otp(
    country_code: str,
    mobile_or_whatsapp: str,
    otp_session: str,
    otp_value: str,
    salt: str,
    expiry_time: str,
    registration_type: str = Field(..., pattern="^(mobile|whatsapp)$"),
) -> VerifyOTPResponse:
    """
    Verify OTP and login/register user.
    """
    payload = {
        "countryCode": country_code,
        "userType": "Login",
        "salt": salt,
        "expiryTime": expiry_time,
        "registrationType": registration_type,
    }

    if registration_type == "mobile":
        payload.update(
            {
                "mobileNumber": mobile_or_whatsapp,
                "mobileOtpSession": otp_session,
                "mobileOtpValue": otp_value,
            }
        )
    else:
        payload.update(
            {
                "whatsappNumber": mobile_or_whatsapp,
                "whatsappOtpSession": otp_session,
                "whatsappOtpValue": otp_value,
            }
        )

    data = await post(
        "/user-service/registerwithMobileAndWhatsappNumber",
        payload,
    )

    if data.get("primaryType") != "CUSTOMER":
        raise ValueError("Only CUSTOMER users are allowed")

    access_token = data["accessToken"]
    session_id = create_session("CUSTOMER", access_token)

    return VerifyOTPResponse(
        message="Login successful",
        session_id=session_id,
    )

def register_tools(mcp_instance):
    global mcp
    mcp = mcp_instance
    mcp.tool()(send_login_otp)
    mcp.tool()(verify_login_otp)
