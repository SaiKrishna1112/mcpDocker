from utils.http import post
from auth.token_store import create_session
import re
from pydantic import BaseModel, Field, field_validator

mcp = None  # injected from server.py

class SimpleLoginResponse(BaseModel):
    user_id: str
    mobile_number: str
    session_id: str
    message: str

class SimpleLoginInput(BaseModel):
    mobile_number: str = Field(..., description="10-digit mobile number")
    country_code: str = Field("+91", description="Country code")

    @field_validator("mobile_number")
    @classmethod
    def validate_mobile(cls, v: str) -> str:
        if not re.fullmatch(r"[0-9]{10}", v):
            raise ValueError("mobile_number must be exactly 10 digits")
        return v

async def simple_login(
    mobile_number: str = Field(..., description="10-digit mobile number"),
    country_code: str = Field("+91", description="Country code"),
) -> SimpleLoginResponse:
    SimpleLoginInput(
        mobile_number=mobile_number,
        country_code=country_code
    )

    payload = {
        "countryCode": country_code,
        "mobileNumber": mobile_number,
        "registerFrom": "MOBILE"
    }

    data = await post("/user-service/onlineRegistration", payload)

    session_id = create_session(data["userId"], data["accessToken"])

    return SimpleLoginResponse(
        user_id=data["userId"],
        mobile_number=data["mobileNumber"],
        session_id=session_id,
        message=data["message"]
    )


def register_tools(mcp_instance):
    global mcp
    mcp = mcp_instance
    mcp.tool()(simple_login)
