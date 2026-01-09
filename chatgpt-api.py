from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import httpx
from typing import Optional
import asyncio

app = FastAPI(title="OxyLoans API for ChatGPT", version="1.0.0")

# Enable CORS for ChatGPT
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://chat.openai.com", "https://chatgpt.com"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

BASE_URL = "https://meta.oxyloans.com/api"

async def make_request(url: str, method: str = "GET", data: dict = None):
    async with httpx.AsyncClient() as client:
        try:
            if method == "GET":
                response = await client.get(url, timeout=30.0)
            elif method == "POST":
                response = await client.post(url, json=data, timeout=30.0)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

@app.get("/products")
async def get_trending_products():
    """Get trending products"""
    url = f"{BASE_URL}/product-service/showGroupItemsForCustomrs"
    return await make_request(url)

@app.get("/cart/{customer_id}")
async def get_user_cart(customer_id: str):
    """Get user cart by customer ID"""
    url = f"{BASE_URL}/cart-service/cart/userCartInfo?customerId={customer_id}"
    return await make_request(url)

@app.get("/user/{user_id}")
async def get_user_profile(user_id: str):
    """Get user profile by user ID"""
    url = f"{BASE_URL}/users/{user_id}"
    return await make_request(url)

@app.get("/offers")
async def get_active_offers():
    """Get active offers"""
    url = f"{BASE_URL}/product-service/getComboActiveInfo"
    return await make_request(url)

@app.post("/cart/add")
async def add_to_cart(customer_id: str, item_id: str, quantity: int):
    """Add item to cart"""
    url = f"{BASE_URL}/cart-service/cart/addAndIncrementCart"
    data = {"customerId": customer_id, "itemId": item_id, "quantity": quantity}
    return await make_request(url, "POST", data)

@app.post("/cart/remove")
async def remove_from_cart(customer_id: str, item_id: str):
    """Remove item from cart"""
    url = f"{BASE_URL}/cart-service/cart/remove"
    data = {"customerId": customer_id, "itemId": item_id}
    return await make_request(url, "POST", data)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=3000)