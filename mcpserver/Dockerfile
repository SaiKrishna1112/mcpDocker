#FROM python:3.11-slim
#
#WORKDIR /app
#
## Copy requirements file
#COPY requirements.txt .
#
## Install dependencies using uv
#RUN pip install uv
#RUN uv venv
#RUN uv pip install -r requirements.txt
#
## Copy application code
#COPY server.py .
#COPY client-sse.py .
#
## Expose the port the server runs on
#EXPOSE 8001
#
## Command to run the server
#CMD ["uv", "run", "python", "mcpserver/server.py"]

FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

COPY requirements.txt .

RUN pip install uv
RUN uv venv
RUN uv pip install -r requirements.txt

COPY . .

EXPOSE 8001

CMD ["uv", "run", "python", "server.py"]
