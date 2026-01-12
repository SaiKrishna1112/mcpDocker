import os
import httpx
from typing import List, Optional
from pydantic import BaseModel, Field
from fastmcp import FastMCP
from utils.http import get, post
from auth.token_store import get_token_by_session

# mcp: FastMCP  # injected from server.py
mcp = FastMCP(
    name="oxyloans-api"
)

GOOGLE_API_KEY = os.getenv("GOOGLE_MAPS_API_KEY")


# -------------------------------------------------
# Schemas
# -------------------------------------------------

class Address(BaseModel):
    id: str
    user_id: str
    flat_no: str
    address: str
    landmark: str
    area: Optional[str]
    residence_name: Optional[str]
    address_type: str
    house_type: Optional[str]
    pincode: str
    latitude: str
    longitude: str
    created_at: Optional[str]


class AddAddressResponse(BaseModel):
    success: bool
    message: str


# -------------------------------------------------
# Google Geocoding Helper
# -------------------------------------------------

async def geocode_address(address: str, pincode: str) -> tuple[str, str]:
    async with httpx.AsyncClient(timeout=30.0) as client:
        resp = await client.get(
            "https://maps.googleapis.com/maps/api/geocode/json",
            params={
                "address": address,
                "key": GOOGLE_API_KEY,
            },
        )
        resp.raise_for_status()
        data = resp.json()

    for result in data.get("results", []):
        components = result.get("address_components", [])

        country_ok = any(
            c["types"] == ["country"] and c["short_name"] == "IN"
            for c in components
        )

        pincode_ok = any(
            "postal_code" in c["types"] and c["long_name"] == pincode
            for c in components
        )

        if country_ok and pincode_ok:
            loc = result["geometry"]["location"]
            return str(loc["lat"]), str(loc["lng"])

    raise ValueError("Unable to resolve valid Indian coordinates")


# -------------------------------------------------
# Tools
# -------------------------------------------------

@mcp.tool()
async def view_address_list(
    session_id: str,
    customer_id: str,
) -> List[Address]:
    """
    View all saved addresses for a customer.
    """
    token = get_token_by_session(session_id)
    if not token:
        raise ValueError("Invalid session")

    data = await get(
        "/api/user-service/getAllAdd",
        params={"customerId": customer_id},
        bearer_token=token,
    )

    return [
        Address(
            id=a.get("id"),
            user_id=a.get("userId"),
            flat_no=a.get("flatNo"),
            address=a.get("address"),
            landmark=a.get("landMark"),
            area=a.get("area"),
            residence_name=a.get("residenceName"),
            address_type=a.get("addressType"),
            house_type=a.get("houseType"),
            pincode=a.get("pincode"),
            latitude=a.get("latitude"),
            longitude=a.get("longitude"),
            created_at=a.get("createdAt"),
        )
        for a in data
    ]


@mcp.tool()
async def add_address(
    session_id: str,
    customer_id: str,
    flat_no: str,
    address: str,
    landmark: str,
    pincode: str,
    address_type: str,
) -> AddAddressResponse:
    """
    Add a new address after resolving coordinates (India only).
    """
    token = get_token_by_session(session_id)
    if not token:
        raise ValueError("Invalid session")

    latitude, longitude = await geocode_address(address, pincode)

    payload = {
        "userId": customer_id,
        "flatNo": flat_no,
        "landMark": landmark,
        "address": address,
        "pincode": pincode,
        "addressType": address_type,
        "latitude": latitude,
        "longitude": longitude,
    }

    data = await post(
        "/api/user-service/addAddress",
        payload,
        bearer_token=token,
    )

    return AddAddressResponse(
        success=data.get("success", True),
        message=data.get("message", "Address added successfully"),
    )
