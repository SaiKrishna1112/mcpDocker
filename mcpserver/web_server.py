#!/usr/bin/env python3
"""
Simple web server to serve .well-known directory for OpenAI app verification
"""

from fastapi import FastAPI
from fastapi.responses import PlainTextResponse
import os
import uvicorn
from fastapi import FastAPI, Request, HTTPException
import time
import os
import httpx


app = FastAPI()

@app.get("/.well-known/openai-apps-challenge")
async def openai_apps_challenge():
    """Serve OpenAI apps challenge token"""
    return PlainTextResponse("lCG1ME4nDMF4SQ5WN34e_mRcJ2671QubLKki1faFH8o")

@app.get("/")
async def root():
    """Root endpoint"""
    return {"message": "OxyLoans Web Server", "status": "running"}

@app.get("/health")
async def health():
    """Health check endpoint"""
    return {"status": "healthy"}

# --------------------------------------------------
# Configuration
# --------------------------------------------------
IDLE_THRESHOLD_SECONDS = 13 * 60  # 13 minutes
CRON_SECRET = os.environ.get("CRON_SECRET", "changeme")
BASE_URL = os.environ.get(
    "BASE_URL",
    "https://your-app.onrender.com"
)

# --------------------------------------------------
# Idle tracking
# --------------------------------------------------
last_request_at = time.time()

@app.middleware("http")
async def track_activity(request: Request, call_next):
    """
    Track only REAL user traffic.
    Cron endpoints must NOT reset idle timer.
    """
    global last_request_at

    if request.url.path not in ("/idle-status", "/idle-ping"):
        last_request_at = time.time()

    return await call_next(request)

# --------------------------------------------------
# Idle status check (called by external cron)
# --------------------------------------------------
@app.get("/idle-status")
def idle_status(x_cron_key: str | None = None):
    if x_cron_key != CRON_SECRET:
        raise HTTPException(status_code=401, detail="Unauthorized")

    idle_seconds = int(time.time() - last_request_at)

    return {
        "idle": idle_seconds >= IDLE_THRESHOLD_SECONDS,
        "idle_seconds": idle_seconds
    }

# --------------------------------------------------
# Idle ping (hits `/` only when idle)
# --------------------------------------------------
@app.get("/idle-ping")
async def idle_ping(x_cron_key: str | None = None):
    if x_cron_key != CRON_SECRET:
        raise HTTPException(status_code=401, detail="Unauthorized")

    async with httpx.AsyncClient(timeout=10) as client:
        response = await client.get(f"{BASE_URL}/")

    return {
        "idle_triggered": True,
        "root_response": response.json()
    }


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8002))
    print(f"🌐 Starting web server on port {port}")
    print(f"✅ Challenge file available at: /.well-known/openai-apps-challenge")
    uvicorn.run(app, host="0.0.0.0", port=port)