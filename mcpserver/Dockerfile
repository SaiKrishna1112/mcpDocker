FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV SERVER_MODE=both

WORKDIR /app

COPY requirements.txt .

RUN pip install uv
RUN uv venv
RUN uv pip install -r requirements.txt

COPY . .

EXPOSE 8001 8002

# Health check every 10 minutes
HEALTHCHECK --interval=10m --timeout=10s --start-period=30s --retries=3 \
  CMD python -c "import urllib.request, os; port = os.environ.get('PORT', '8001'); urllib.request.urlopen(f'http://localhost:{port}/health')" || exit 1

# Run the server (scheduler runs automatically in background)
CMD ["uv", "run", "python", "start.py"]