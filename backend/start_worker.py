"""
Start Celery worker for processing background tasks.

Usage:
    python start_worker.py

This will start a Celery worker that processes tasks from the Redis queue.
"""
import sys
import subprocess

if __name__ == "__main__":
    # Run Celery worker
    cmd = [
        sys.executable,
        "-m",
        "celery",
        "-A",
        "app.celery_app",
        "worker",
        "--loglevel=info",
        "--concurrency=2",  # Number of worker processes
        "--pool=solo" if sys.platform == "win32" else "--pool=prefork",  # Windows uses solo pool
    ]

    print(f"Starting Celery worker...")
    print(f"Command: {' '.join(cmd)}")
    subprocess.run(cmd)
