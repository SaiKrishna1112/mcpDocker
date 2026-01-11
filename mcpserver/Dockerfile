FROM python:3.11-slim

WORKDIR /app

# Install uv
RUN pip install uv

# Copy project files
COPY pyproject.toml .
COPY uv.lock .

# Install dependencies
RUN uv sync --frozen

# Copy application code
COPY mcpserver/ ./mcpserver/

EXPOSE 8001

CMD ["uv", "run", "python", "mcpserver/server.py"]