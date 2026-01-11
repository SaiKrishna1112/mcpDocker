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
COPY . .

# Expose ports
EXPOSE 8000 8001

# Default command (can be overridden)
CMD ["uv", "run", "live-api.py"]