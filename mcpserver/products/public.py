from typing import List, Optional
from pydantic import BaseModel, Field
from fastmcp import FastMCP
from utils.http import get

mcp = FastMCP(
    name="oxyloans-api"
)

class Product(BaseModel):
    item_id: str
    name: str
    price: float
    mrp: float
    image: Optional[str]
    description: Optional[str]
    category: Optional[str]

class TrendingProductsResponse(BaseModel):
    products: List[Product]
    count: int

@mcp.tool()
async def get_trending_products(
    limit: int = Field(20, ge=1, le=100, description="Number of products to return")
) -> TrendingProductsResponse:
    """
    Get trending products (public access, no authentication required).
    """
    data = await get(
        "/product-service/showGroupItemsForCustomrs",
        params={},
    )

    products: List[Product] = []

    for group in data:
        for category in group.get("categories", []):
            for item in category.get("itemsResponseDtoList", []):
                products.append(
                    Product(
                        item_id=item.get("itemId"),
                        name=item.get("itemName"),
                        price=item.get("itemPrice", 0),
                        mrp=item.get("itemMrp", 0),
                        image=item.get("itemImage"),
                        description=item.get("itemDescription"),
                        category=category.get("categoryName"),
                    )
                )

    products = products[:limit]
    return TrendingProductsResponse(products=products, count=len(products))