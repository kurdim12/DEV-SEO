"""
Start Celery Beat scheduler for periodic tasks.

Usage:
    python start_beat.py

This will start Celery Beat which schedules periodic tasks like:
- Daily digest emails
- Cleanup of old results
"""
import sys
import subprocess

if __name__ == "__main__":
    # Run Celery beat
    cmd = [
        sys.executable,
        "-m",
        "celery",
        "-A",
        "app.celery_app",
        "beat",
        "--loglevel=info",
    ]

    print(f"Starting Celery Beat scheduler...")
    print(f"Command: {' '.join(cmd)}")
    subprocess.run(cmd)
