from pydantic import BaseModel, Field
from utils.http import post
from auth.token_store import create_session

mcp = None  # injected from server.py

class SimpleLoginResponse(BaseModel):
    user_id: str
    mobile_number: str
    session_id: str
    message: str

async def simple_login(
    mobile_number: str = Field(..., description="Mobile number"),
    country_code: str = Field("+91", description="Country code"),
) -> SimpleLoginResponse:
    """
    Simple login/register without OTP verification.
    """
    payload = {
        "countryCode": country_code,
        "mobileNumber": mobile_number,
        "registerFrom": "MOBILE"
    }

    data = await post(
        "/user-service/onlineRegistration",
        payload,
    )

    access_token = data["accessToken"]
    user_id = data["userId"]
    
    session_id = create_session(user_id, access_token)

    return SimpleLoginResponse(
        user_id=user_id,
        mobile_number=data["mobileNumber"],
        session_id=session_id,
        message=data["message"]
    )

def register_tools(mcp_instance):
    global mcp
    mcp = mcp_instance
    mcp.tool()(simple_login)
