from pydantic import BaseModel
from mcp.server.fastmcp import FastMCP
from utils.http import get

# mcp: FastMCP
mcp = FastMCP(
    name="oxyloans-api"
)

class ProductImage(BaseModel):
    imageUrl: str


@mcp.tool()
async def get_product_images(item_id: str) -> list[ProductImage]:
    data = await get(
        "/api/product-service/ImagesViewBasedOnItemId",
        params={"itemId": item_id},
    )
    return [ProductImage(**img) for img in data]
