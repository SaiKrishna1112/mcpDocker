import httpx
from typing import Optional

BASE_URL = "https://meta.oxyloans.com/api"


async def post(
    path: str,
    payload: dict,
    bearer_token: Optional[str] = None,
):
    headers = {"Content-Type": "application/json"}

    if bearer_token:
        headers["Authorization"] = f"Bearer {bearer_token}"

    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.post(
            f"{BASE_URL}{path}",
            json=payload,
            headers=headers,
        )

        if response.status_code in (400, 409):
            raise ValueError(response.json())

        response.raise_for_status()
        return response.json()


async def get(
    path: str,
    params: dict,
    bearer_token: Optional[str] = None,
):
    headers = {}

    if bearer_token:
        headers["Authorization"] = f"Bearer {bearer_token}"

    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.get(
            f"{BASE_URL}{path}",
            params=params,
            headers=headers,
        )

        if response.status_code in (400, 409):
            raise ValueError(response.json())

        response.raise_for_status()
        return response.json()
