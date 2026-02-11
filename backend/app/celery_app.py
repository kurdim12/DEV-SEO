"""
Celery application configuration for DevSEO background tasks.

This module configures Celery with Redis as the broker and result backend.
"""
from celery import Celery
from app.config import settings

# Create Celery application
celery_app = Celery(
    "devseo",
    broker=settings.REDIS_URL,
    backend=settings.REDIS_URL,
    include=["app.tasks.crawl_tasks", "app.tasks.email_tasks"],
)

# Celery configuration
celery_app.conf.update(
    # Task settings
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,

    # Task execution settings
    task_track_started=True,
    task_time_limit=1800,  # 30 minutes hard limit
    task_soft_time_limit=1500,  # 25 minutes soft limit
    task_acks_late=True,  # Acknowledge after task completion
    task_reject_on_worker_lost=True,  # Reject task if worker dies

    # Result backend settings
    result_expires=3600,  # Results expire after 1 hour
    result_persistent=True,

    # Worker settings
    worker_prefetch_multiplier=1,  # One task at a time per worker
    worker_max_tasks_per_child=50,  # Restart worker after 50 tasks (prevent memory leaks)
    worker_disable_rate_limits=False,

    # Beat scheduler settings (for periodic tasks)
    beat_schedule={
        # Example: Clean up old results every day
        "cleanup-old-results": {
            "task": "app.tasks.crawl_tasks.cleanup_old_results",
            "schedule": 86400.0,  # Every 24 hours
        },
        # Example: Send daily digest emails
        "send-daily-digest": {
            "task": "app.tasks.email_tasks.send_daily_digest",
            "schedule": 86400.0,  # Every 24 hours
            "options": {"expires": 3600},  # Expire after 1 hour if not executed
        },
    },

    # Monitoring
    task_send_sent_event=True,
    worker_send_task_events=True,
)

# Optional: Task routes (send specific tasks to specific queues)
celery_app.conf.task_routes = {
    "app.tasks.crawl_tasks.*": {"queue": "crawl"},
    "app.tasks.email_tasks.*": {"queue": "email"},
}

# Optional: Rate limits
celery_app.conf.task_annotations = {
    "app.tasks.email_tasks.send_email": {"rate_limit": "10/m"},  # Max 10 emails per minute
    "app.tasks.crawl_tasks.process_crawl_job": {"rate_limit": "5/m"},  # Max 5 crawls per minute
}
