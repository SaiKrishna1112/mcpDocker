#!/usr/bin/env python3
"""
Simple web server to serve .well-known directory for OpenAI app verification
"""

from fastapi import FastAPI
from fastapi.responses import PlainTextResponse
import os
import uvicorn

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

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8002))
    print(f"🌐 Starting web server on port {port}")
    print(f"✅ Challenge file available at: /.well-known/openai-apps-challenge")
    uvicorn.run(app, host="0.0.0.0", port=port)