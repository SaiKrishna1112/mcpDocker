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
  CMD python -c "import urllib.request, os; \
ports = [os.environ.get('PORT'), '10000', '8001', '8000', '8002']; \
success = False; \
for p in ports: \
    if p: \
        try: \
            urllib.request.urlopen(f'http://localhost:{p}/health', timeout=3); \
            success = True; \
            break; \
        except Exception: \
            pass; \
if not success: \
    exit(1)"

# Run the server (scheduler runs automatically in background)
CMD ["uv", "run", "python", "start.py"]