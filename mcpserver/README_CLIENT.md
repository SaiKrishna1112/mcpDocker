# OpenAI MCP Client Setup

This client integrates the OxyLoans MCP Server with OpenAI's API, allowing you to chat with the system and have it automatically call the appropriate tools.

## Prerequisites

1.  **OpenAI API Key**: You need an OpenAI API Key.
    *   Create a `.env` file in the `mcpserver` directory (if it doesn't exist).
    *   Add your key: `OPENAI_API_KEY=sk-...`

2.  **Dependencies**:
    *   Ensure you have the required packages installed.
    *   Run: `pip install -r requirements.txt` (or use `uv sync` if managing with uv).

## Running the System

You need two terminal windows:

**Terminal 1: Start the MCP Server**
```bash
cd mcpserver
python server.py
# Or if using uv:
# uv run server.py
```

**Terminal 2: Run the Client**
```bash
cd mcpserver
python openai_client.py
# Or if using uv:
# uv run openai_client.py
```

## Usage

Once the client connects, you can type queries like:
- "Show me trending products"
- "Search for shoes under 2000"
- "Add item 123 to cart for user user_1"

The client will:
1.  Send your query to OpenAI.
2.  OpenAI will decide which MCP tool to call.
3.  The client executes the tool on the local MCP server.
4.  The result is sent back to OpenAI to generate a natural language response.
