"""
OxyLoans MCP Server for ChatGPT Integration

This server implements the Model Context Protocol (MCP) with search and fetch
capabilities designed to work with ChatGPT's chat and deep research features.
"""

import logging
import json
import httpx
from typing import Dict, List, Any
from fastmcp import FastMCP

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# OxyLoans API configuration
BASE_URL = "https://meta.oxyloans.com/api"

server_instructions = """
This MCP server provides search and document retrieval capabilities
for OxyLoans e-commerce platform. Use the search tool to find products,
then use the fetch tool to retrieve complete product details.
"""

async def make_api_request(url: str, method: str = "GET", data: dict = None):
    """Make API request to OxyLoans backend"""
    async with httpx.AsyncClient(timeout=30.0) as client:
        try:
            if method == "GET":
                response = await client.get(url)
            elif method == "POST":
                response = await client.post(url, json=data)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"API request failed: {e}")
            return None

def create_server():
    """Create and configure the MCP server with search and fetch tools."""
    
    mcp = FastMCP(
        name="OxyLoans MCP Server",
        instructions=server_instructions
    )

    @mcp.tool()
    async def search(query: str) -> str:
        """
        Search for products in OxyLoans catalog.
        
        Args:
            query: Search query string for products
            
        Returns:
            JSON string with results array containing product matches
        """
        if not query or not query.strip():
            return json.dumps({"results": []})
        
        logger.info(f"Searching products for query: '{query}'")
        
        # Get all products from OxyLoans
        url = f"{BASE_URL}/product-service/showGroupItemsForCustomrs"
        data = await make_api_request(url)
        
        if not data:
            return json.dumps({"results": []})
        
        results = []
        query_lower = query.lower()
        
        try:
            for category in data:
                for cat in category.get("categories", []):
                    for item in cat.get("itemsResponseDtoList", []):
                        item_name = item.get("itemName", "").lower()
                        item_desc = item.get("itemDescription", "").lower()
                        category_name = cat.get("categoryName", "").lower()
                        
                        # Simple search matching
                        if (query_lower in item_name or 
                            query_lower in item_desc or 
                            query_lower in category_name):
                            
                            result = {
                                "id": str(item.get("itemId", "")),
                                "title": item.get("itemName", "Unknown Product"),
                                "url": f"https://meta.oxyloans.com/product/{item.get('itemId', '')}"
                            }
                            results.append(result)
                            
                            # Limit results to avoid overwhelming response
                            if len(results) >= 10:
                                break
                    if len(results) >= 10:
                        break
                if len(results) >= 10:
                    break
                    
        except Exception as e:
            logger.error(f"Error processing search results: {e}")
            return json.dumps({"results": []})
        
        logger.info(f"Search returned {len(results)} results")
        return json.dumps({"results": results})

    @mcp.tool()
    async def fetch(id: str) -> str:
        """
        Retrieve complete product details by ID.
        
        Args:
            id: Product ID to fetch details for
            
        Returns:
            JSON string with complete product information
        """
        if not id:
            raise ValueError("Product ID is required")
        
        logger.info(f"Fetching product details for ID: {id}")
        
        # Get all products to find the specific one
        url = f"{BASE_URL}/product-service/showGroupItemsForCustomrs"
        data = await make_api_request(url)
        
        if not data:
            raise ValueError(f"Product with ID {id} not found")
        
        # Find the specific product
        for category in data:
            for cat in category.get("categories", []):
                for item in cat.get("itemsResponseDtoList", []):
                    if str(item.get("itemId", "")) == str(id):
                        result = {
                            "id": str(item.get("itemId", "")),
                            "title": item.get("itemName", "Unknown Product"),
                            "text": f"""Product Details:
Name: {item.get('itemName', 'N/A')}
Price: ₹{item.get('itemPrice', 'N/A')}
MRP: ₹{item.get('itemMrp', 'N/A')}
Description: {item.get('itemDescription', 'No description available')}
Category: {cat.get('categoryName', 'N/A')}
Weight: {item.get('weight', 'N/A')} {item.get('units', '')}
Quantity Available: {item.get('quantity', 'N/A')}
Save Amount: ₹{item.get('saveAmount', '0')}
Save Percentage: {item.get('savePercentage', '0')}%
""",
                            "url": f"https://meta.oxyloans.com/product/{item.get('itemId', '')}",
                            "metadata": {
                                "category": cat.get("categoryName"),
                                "price": item.get("itemPrice"),
                                "mrp": item.get("itemMrp"),
                                "weight": item.get("weight"),
                                "units": item.get("units"),
                                "saveAmount": item.get("saveAmount"),
                                "savePercentage": item.get("savePercentage")
                            }
                        }
                        logger.info(f"Fetched product: {id}")
                        return json.dumps(result)
        
        raise ValueError(f"Product with ID {id} not found")

    return mcp

def main():
    """Main function to start the MCP server."""
    logger.info("Starting OxyLoans MCP server")
    
    # Create the MCP server
    server = create_server()
    
    # Configure and start the server
    logger.info("Starting MCP server on 0.0.0.0:8000")
    logger.info("Server will be accessible via SSE transport")
    
    try:
        server.run(transport="sse", host="0.0.0.0", port=8000)
    except KeyboardInterrupt:
        logger.info("Server stopped by user")
    except Exception as e:
        logger.error(f"Server error: {e}")
        raise

if __name__ == "__main__":
    main()