#FROM python:3.11-slim
#
#WORKDIR /app
#
## Install uv
#RUN pip install uv
#
## Copy project files
#COPY pyproject.toml .
#COPY uv.lock .
#
## Install dependencies
#RUN uv sync --frozen
#
## Copy application code
#COPY mcpserver/ ./mcpserver/
#
#EXPOSE 8001
#
#CMD ["uv", "run", "python", "mcpserver/server.py"]


# -----------------------------
# Base image
# -----------------------------
FROM python:3.11-slim

# -----------------------------
# Environment
# -----------------------------
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# -----------------------------
# Install system dependencies
# -----------------------------
RUN apt-get update && apt-get install -y \
    curl \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# -----------------------------
# Install uv
# -----------------------------
RUN curl -LsSf https://astral.sh/uv/install.sh | sh

# Make uv available in PATH
ENV PATH="/root/.cargo/bin:${PATH}"

# -----------------------------
# Set workdir
# -----------------------------
WORKDIR /app

# -----------------------------
# Copy dependency files first
# (better Docker cache)
# -----------------------------
COPY requirements.txt .

# -----------------------------
# Install dependencies with uv
# -----------------------------
RUN uv pip install --system -r requirements.txt

# -----------------------------
# Copy application code
# -----------------------------
COPY . .

# -----------------------------
# Expose port (Render / Docker)
# -----------------------------
EXPOSE 8001

# -----------------------------
# Start MCP server
# -----------------------------
CMD ["uv", "run", "server.py"]
