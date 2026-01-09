from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import httpx
import os
from typing import Optional

app = FastAPI(
    title="OxyLoans API Gateway",
    version="1.0.0",
    description="Live API gateway for OxyLoans services"
)

# CORS for production
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure specific domains in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

BASE_URL = "https://meta.oxyloans.com/api"

async def make_request(url: str, method: str = "GET", data: dict = None):
    async with httpx.AsyncClient(timeout=30.0) as client:
        try:
            if method == "GET":
                response = await client.get(url)
            elif method == "POST":
                response = await client.post(url, json=data)
            response.raise_for_status()
            return response.json()
        except httpx.HTTPError as e:
            raise HTTPException(status_code=500, detail=f"API Error: {str(e)}")
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

@app.get("/")
async def root():
    return {"message": "OxyLoans API Gateway Live", "docs": "/docs"}

@app.get("/products")
async def get_trending_products():
    """Get all trending products"""
    url = f"{BASE_URL}/product-service/showGroupItemsForCustomrs"
    data = await make_request(url)
    
    # Process and flatten the data
    items = []
    try:
        for category in data:
            for cat in category.get("categories", []):
                for item in cat.get("itemsResponseDtoList", []):
                    items.append({
                        "id": item.get("itemId"),
                        "name": item.get("itemName"),
                        "price": item.get("itemPrice"),
                        "mrp": item.get("itemMrp"),
                        "image": item.get("itemImage"),
                        "category": cat.get("categoryName"),
                        "saveAmount": item.get("saveAmount"),
                        "savePercentage": item.get("savePercentage")
                    })
        return {"products": items, "total": len(items)}
    except Exception:
        return {"products": data, "total": 0}

@app.get("/cart/{customer_id}")
async def get_user_cart(customer_id: str):
    """Get user cart information"""
    url = f"{BASE_URL}/cart-service/cart/userCartInfo?customerId={customer_id}"
    return await make_request(url)

@app.get("/user/{user_id}")
async def get_user_profile(user_id: str):
    """Get user profile"""
    url = f"{BASE_URL}/users/{user_id}"
    return await make_request(url)

@app.get("/offers")
async def get_active_offers():
    """Get active combo offers"""
    url = f"{BASE_URL}/product-service/getComboActiveInfo"
    return await make_request(url)

@app.post("/cart/add")
async def add_to_cart(customer_id: str, item_id: str, quantity: int = 1):
    """Add item to cart"""
    url = f"{BASE_URL}/cart-service/cart/addAndIncrementCart"
    data = {
        "customerId": customer_id,
        "itemId": item_id,
        "quantity": quantity
    }
    return await make_request(url, "POST", data)

@app.post("/cart/remove")
async def remove_from_cart(customer_id: str, item_id: str):
    """Remove item from cart"""
    url = f"{BASE_URL}/cart-service/cart/remove"
    data = {
        "customerId": customer_id,
        "itemId": item_id
    }
    return await make_request(url, "POST", data)

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "oxyloans-api-gateway"}

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)