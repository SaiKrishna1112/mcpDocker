from pydantic import BaseModel
from utils.http import get

mcp = None

class ProductImage(BaseModel):
    imageUrl: str


async def get_product_images(item_id: str) -> list[ProductImage]:
    data = await get(
        "/api/product-service/ImagesViewBasedOnItemId",
        params={"itemId": item_id},
    )
    return [ProductImage(**img) for img in data]


def register_tools(mcp_instance):
    global mcp
    mcp = mcp_instance
    mcp.tool()(get_product_images)
