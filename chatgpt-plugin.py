from flask import Flask, jsonify, request
import httpx
import asyncio

app = Flask(__name__)
BASE_URL = "https://meta.oxyloans.com/api"

async def make_request(url):
    async with httpx.AsyncClient() as client:
        response = await client.get(url)
        return response.json()

@app.route("/products", methods=["GET"])
def get_products():
    """Get trending products for ChatGPT"""
    url = f"{BASE_URL}/product-service/showGroupItemsForCustomrs"
    data = asyncio.run(make_request(url))
    return jsonify(data)

@app.route("/cart/<customer_id>", methods=["GET"])
def get_cart(customer_id):
    """Get user cart for ChatGPT"""
    url = f"{BASE_URL}/cart-service/cart/userCartInfo?customerId={customer_id}"
    data = asyncio.run(make_request(url))
    return jsonify(data)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)