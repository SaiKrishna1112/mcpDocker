#!/usr/bin/env python3
"""
External scheduler - Run this on cron services like cron-job.org or EasyCron
Schedule: Every 10 minutes
"""

import httpx
import os
import sys

def ping():
    url = os.environ.get("SERVER_URL", "https://testingmcp-kulj.onrender.com")
    try:
        response = httpx.get(f"{url}/health", timeout=10)
        print(f"✓ {response.status_code}")
        sys.exit(0)
    except Exception as e:
        print(f"✗ {e}")
        sys.exit(1)

if __name__ == "__main__":
    ping()
