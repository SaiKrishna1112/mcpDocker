FROM python:3.11-slim

# -----------------------------
# Environment hardening
# -----------------------------
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# -----------------------------
# Working directory
# -----------------------------
WORKDIR /app

# -----------------------------
# Install uv (PATH-safe)
# -----------------------------
RUN pip install --no-cache-dir uv

# -----------------------------
# Copy dependency files first
# (better Docker layer caching)
# -----------------------------
COPY pyproject.toml uv.lock ./

# -----------------------------
# Install dependencies (locked)
# -----------------------------
RUN uv sync --frozen

# -----------------------------
# Copy application code
# -----------------------------
COPY mcpserver/ ./mcpserver/

# -----------------------------
# Expose MCP port
# -----------------------------
EXPOSE 8001

# -----------------------------
# Run MCP server
# -----------------------------
CMD ["uv", "run", "mcpserver/server.py"]
