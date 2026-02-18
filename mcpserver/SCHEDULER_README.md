# Scheduler Setup - Keep Server Active

## Overview
The scheduler pings the server every 10 minutes to prevent it from sleeping on free hosting platforms.

## Built-in Scheduler (Automatic)
The scheduler is automatically integrated into:
- `start.py` (web and both modes)
- `unified_server.py`

No additional setup needed - it runs in the background automatically.

## External Scheduler Options

### Option 1: Render Cron Job
Use `render-scheduler.yaml` for deployment:
```bash
render deploy --config render-scheduler.yaml
```

### Option 2: Free Cron Services
Use services like:
- cron-job.org
- EasyCron
- UptimeRobot

**Setup:**
1. Create account on cron service
2. Add new job:
   - URL: `https://your-server.onrender.com/health`
   - Interval: Every 10 minutes
   - Method: GET

### Option 3: GitHub Actions
Create `.github/workflows/keep-alive.yml`:
```yaml
name: Keep Server Active
on:
  schedule:
    - cron: '*/10 * * * *'
jobs:
  ping:
    runs-on: ubuntu-latest
    steps:
      - run: curl https://your-server.onrender.com/health
```

## Environment Variables
- `SERVER_URL`: Your server URL (default: http://localhost:8001)
- `PING_INTERVAL`: Minutes between pings (default: 10)

## Verify Scheduler
Check logs for:
```
🕐 Background scheduler started (interval: 10m)
[timestamp] ✓ Ping: 200
```
