#!/usr/bin/env python3
"""
Scheduler to keep server active with periodic health checks
"""

import httpx
import time
import os
import asyncio
from datetime import datetime

async def ping_server():
    """Send health check to keep server active"""
    url = os.environ.get("SERVER_URL", "http://localhost:8001")
    try:
        async with httpx.AsyncClient(timeout=10) as client:
            response = await client.get(f"{url}/health")
            print(f"[{datetime.now()}] ✓ Ping: {response.status_code}")
    except Exception as e:
        print(f"[{datetime.now()}] ✗ Ping failed: {e}")

async def run_scheduler(interval_minutes=10):
    """Run scheduler with specified interval"""
    print(f"🕐 Scheduler started (interval: {interval_minutes}m)")
    await asyncio.sleep(30)  # Wait for server to start
    while True:
        await ping_server()
        await asyncio.sleep(interval_minutes * 60)

def start_scheduler_thread(interval_minutes=10):
    """Start scheduler in background thread"""
    import threading
    
    def run():
        asyncio.run(run_scheduler(interval_minutes))
    
    thread = threading.Thread(target=run, daemon=True)
    thread.start()
    print(f"🕐 Background scheduler started (interval: {interval_minutes}m)")

if __name__ == "__main__":
    interval = int(os.environ.get("PING_INTERVAL", 10))
    asyncio.run(run_scheduler(interval))
