import subprocess
import time
import sys
import os
import signal
import threading
try:
    import httpx
except ImportError:
    print("httpx module not found. Please install it with 'pip install httpx'")
    sys.exit(1)

# The script that starts the actual web/mcp server
SERVER_SCRIPT = "start.py"
PING_INTERVAL_MINUTES = 13
PING_INTERVAL_SECONDS = PING_INTERVAL_MINUTES * 60

current_process = None
shutdown_requested = False

def cleanup_process():
    global current_process
    if current_process:
        if current_process.poll() is None:
            print(f"Terminating server process PID {current_process.pid}...")
            current_process.terminate()
            try:
                current_process.wait(timeout=10)
            except subprocess.TimeoutExpired:
                print("Force killing server process...")
                current_process.kill()
                current_process.wait()
    print("Cleanup complete.")

def signal_handler(signum, frame):
    global shutdown_requested
    print(f"\nReceived signal {signum}. Shutting down...")
    shutdown_requested = True

def run_server_process():
    print(f"--- Starting {SERVER_SCRIPT} ---")
    env = os.environ.copy()
    
    # Start the server process
    process = subprocess.Popen(
        [sys.executable, SERVER_SCRIPT],
        env=env,
        cwd=os.path.dirname(os.path.abspath(__file__))
    )
    return process

def pinger_thread_func(port):
    """Periodically hits the health endpoint to keep the server active."""
    global shutdown_requested
    
    # Give the server some time to start up
    print("Pinger: Waiting 30 seconds for server to start...")
    for _ in range(30):
        if shutdown_requested: return
        time.sleep(1)
        
    url = f"http://127.0.0.1:{port}/health" # unified_server/start.py usually has this
    # Fallback if running pure MCP mode might differ, but start.py 'both'/'web' has /health or /
    
    # Ideally logic should detect if /health exists, otherwise try /
    
    print(f"Pinger: Started. Will ping '{url}' every {PING_INTERVAL_MINUTES} minutes.")

    while not shutdown_requested:
        # Wait for interval (in small chunks to allow checking shutdown_flag)
        slept = 0
        while slept < PING_INTERVAL_SECONDS:
            if shutdown_requested:
                return
            time.sleep(1)
            slept += 1
            
        # Time to ping
        try:
            print(f"Pinger: Sending keep-alive request to {url}...")
            response = httpx.get(url, timeout=10)
            print(f"Pinger: Response {response.status_code}")
        except Exception as e:
            print(f"Pinger: Request failed: {e}")

def main():
    global current_process, shutdown_requested
    
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    port = int(os.environ.get("PORT", 8001))
    
    # 1. Start the server
    current_process = run_server_process()
    print(f"Server process started with PID {current_process.pid}")

    # 2. Start the pinger thread
    pinger = threading.Thread(target=pinger_thread_func, args=(port,), daemon=True)
    pinger.start()

    # 3. Monitor the server process
    try:
        while not shutdown_requested:
            ret_code = current_process.poll()
            if ret_code is not None:
                print(f"Server process exited unexpectedly with code {ret_code}. Exiting wrapper.")
                shutdown_requested = True
                break
            time.sleep(1)
    finally:
        cleanup_process()
        print("Wrapper exited.")

if __name__ == "__main__":
    main()
