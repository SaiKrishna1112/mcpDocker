# Deployment Guide

## Modes

| `SERVER_MODE` | What runs | Port |
|---------------|-----------|------|
| `mcp` | FastMCP SSE only | 8001 |
| `web` | FastAPI web server only | 8001 |
| `both` | Unified (MCP at `/mcp/sse`, web at `/`) | 8001 |

---

## Docker

### Build & Run

```bash
cd mcpserver
docker build -t askoxy-mcp .
docker run -p 8001:8001 -e SERVER_MODE=mcp askoxy-mcp
```

### Both servers

```bash
docker run -p 8001:8001 -e SERVER_MODE=both askoxy-mcp
```

Endpoints:
- MCP SSE: `http://localhost:8001/mcp/sse`
- Web: `http://localhost:8001/`

### Dockerfile summary

```
Base:    python:3.11-slim
Deps:    uv pip install -r requirements.txt
Expose:  8001, 8002
CMD:     uv run python start.py
```

---

## Render

`render.yaml` is pre-configured for a single web service.

1. Push repo to GitHub
2. Connect to [render.com](https://render.com)
3. Set environment variable: `SERVER_MODE=both`
4. Deploy — Render auto-assigns a public URL

For separate MCP + web services, use `render-single.yaml`.

---

## Local Development

```bash
cd mcpserver
cp .env.example .env
pip install -r requirements.txt
SERVER_MODE=mcp python start.py
```

Or with `uv`:

```bash
uv venv && uv pip install -r requirements.txt
SERVER_MODE=mcp uv run python start.py
```

---

## Amazon Q / MCP Client Config

Add to your MCP client configuration:

```json
{
  "mcpServers": {
    "askoxy": {
      "serverUrl": "https://<your-host>/mcp/sse",
      "transport": "sse"
    }
  }
}
```

For local dev:

```json
{
  "mcpServers": {
    "askoxy": {
      "serverUrl": "http://localhost:8001/sse",
      "transport": "sse"
    }
  }
}
```

---

## Environment Variables

Copy `.env.example` to `.env`:

```bash
SERVER_MODE=both
PORT=8001
MCP_PORT=8001
DEBUG=false
LOG_LEVEL=INFO
```

Never commit `.env` — it is in `.gitignore`.

---

## Health Check

```bash
curl http://localhost:8001/health
# or via MCP tool:
# hello_world() → "askoxy.ai MCP Server is running!"
```
