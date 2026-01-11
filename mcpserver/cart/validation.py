from ..utils.http import get
from ..auth.token_store import get_token_by_session

async def validate_profile_before_cart(session_id: str, customer_id: str):
    token = get_token_by_session(session_id)
    if not token:
        raise ValueError("Invalid session")

    profile = await get(
        "/api/user-service/customerProfileDetails",
        params={"customerId": customer_id},
        bearer_token=token,
    )

    if not profile.get("firstName") or not profile.get("mobileNumber"):
        raise ValueError(
            "Profile incomplete. Please update name and mobile number before adding items to cart."
        )
