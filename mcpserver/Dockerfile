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

# Run the scheduler which runs start.py and restarts it every 13 mins
CMD ["uv", "run", "python", "scheduler.py"]