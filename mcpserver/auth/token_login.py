from pydantic import BaseModel, Field
from auth.token_store import create_session

mcp = None  # injected from server.py


class TokenLoginResponse(BaseModel):
    session_id: str
    message: str


async def set_user_session(
    user_id: str = Field(..., description="User ID from the client"),
    token: str = Field(..., description="Access token from the client"),
) -> TokenLoginResponse:
    """
    Authenticate user directly using a pre-existing token and user_id.
    Use this when the caller has already authenticated externally (e.g. via frontend login)
    and passes token + user_id instead of going through the OTP flow.
    """
    session_id = create_session(user_id=user_id, access_token=token)
    return TokenLoginResponse(session_id=session_id, message="Session created successfully")


def register_tools(mcp_instance):
    global mcp
    mcp = mcp_instance
    mcp.tool()(set_user_session)
