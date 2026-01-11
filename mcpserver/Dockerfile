FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Copy requirements
COPY mcpserver/requirements.txt ./requirements.txt

# Install uv + deps
RUN pip install --no-cache-dir uv
RUN uv pip install -r requirements.txt

# Copy entire MCP server package
COPY mcpserver/ ./mcpserver/

EXPOSE 8001

# Run MCP server
CMD ["uv", "run", "python", "mcpserver/server.py"]
