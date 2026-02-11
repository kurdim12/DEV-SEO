# Celery Background Tasks - Setup & Usage

**Date:** February 10, 2026
**Status:** Implemented and Production Ready
**Version:** Celery 5.6.2 + Redis

---

## Overview

DevSEO now uses **Celery** for asynchronous background task processing, replacing the previous polling-based worker system. This provides better scalability, reliability, and monitoring capabilities.

### Key Benefits:

- **Async Processing**: Crawl jobs run in the background without blocking API requests
- **Scalability**: Can run multiple workers across multiple machines
- **Reliability**: Automatic retries, task acknowledgments, and error handling
- **Monitoring**: Built-in task tracking and status updates
- **Scheduling**: Periodic tasks (daily digests, cleanup) via Celery Beat
- **Queue Management**: Separate queues for different task types (crawl, email)

---

## Architecture

```
┌─────────────┐         ┌──────────┐         ┌────────────┐
│   FastAPI   │────────>│  Redis   │<────────│   Celery   │
│   (API)     │         │ (Broker) │         │  Workers   │
└─────────────┘         └──────────┘         └────────────┘
      │                       │                      │
      │                       │                      │
      v                       v                      v
┌─────────────────────────────────────────────────────────┐
│                  PostgreSQL Database                     │
└─────────────────────────────────────────────────────────┘
```

**Flow:**
1. User initiates scan via API
2. API creates `CrawlJob` in database (status: pending)
3. API sends task to Redis queue via Celery
4. Celery worker picks up task from queue
5. Worker processes crawl job (status: running)
6. Worker saves results to database (status: completed)
7. Worker sends completion email notification

---

## Components

### 1. Celery Application (`app/celery_app.py`)

Main Celery configuration with:
- Redis broker and result backend
- Task serialization (JSON)
- Worker settings (concurrency, timeouts)
- Task routing (crawl queue, email queue)
- Rate limiting per task type
- Beat scheduler for periodic tasks

### 2. Crawl Tasks (`app/tasks/crawl_tasks.py`)

**Tasks:**
- `process_crawl_job` - Main crawl and SEO analysis task
- `cancel_crawl_job` - Cancel a running crawl
- `cleanup_old_results` - Remove old data (runs daily)

**Features:**
- Async/await support
- Automatic retries (max 3 attempts)
- Progress tracking
- Cancellation support
- Error handling with database rollback

### 3. Email Tasks (`app/tasks/email_tasks.py`)

**Tasks:**
- `send_email` - Generic email sending
- `send_crawl_complete_notification` - Notify user when crawl finishes
- `send_daily_digest` - Daily summary emails (scheduled)

**Features:**
- SendGrid integration
- HTML email templates
- Rate limiting (10 emails/minute)
- Automatic retries

---

## Installation

### Prerequisites:

1. **Redis Server** - Message broker and result backend

**Install Redis:**

**Linux/macOS:**
```bash
# Ubuntu/Debian
sudo apt-get install redis-server
sudo systemctl start redis

# macOS (Homebrew)
brew install redis
brew services start redis
```

**Windows:**
```powershell
# Use Docker
docker run -d -p 6379:6379 redis:latest

# Or download Redis for Windows from:
# https://github.com/microsoftarchive/redis/releases
```

2. **Python Dependencies**

```bash
cd backend
pip install -r requirements.txt
```

**Key packages:**
- `celery==5.6.2` - Task queue
- `redis==5.2.0` - Redis client
- `kombu==5.4.2` - Messaging library

---

## Configuration

### Environment Variables (`.env`)

```bash
# Redis URL for Celery broker and result backend
REDIS_URL=redis://localhost:6379/0

# Database URL (PostgreSQL)
DATABASE_URL=postgresql+asyncpg://user:password@localhost:5432/devseo

# SendGrid (for email tasks)
SENDGRID_API_KEY=your_sendgrid_api_key
SENDGRID_FROM_EMAIL=noreply@devseo.io

# Anthropic (for AI recommendations)
ANTHROPIC_API_KEY=your_anthropic_api_key
```

### Celery Configuration

Configured in `app/celery_app.py`:

```python
# Task execution
task_time_limit=1800  # 30 minutes hard limit
task_soft_time_limit=1500  # 25 minutes soft limit
task_acks_late=True  # Acknowledge after completion
worker_prefetch_multiplier=1  # One task at a time

# Task queues
task_routes = {
    "app.tasks.crawl_tasks.*": {"queue": "crawl"},
    "app.tasks.email_tasks.*": {"queue": "email"},
}

# Rate limits
task_annotations = {
    "app.tasks.email_tasks.send_email": {"rate_limit": "10/m"},
    "app.tasks.crawl_tasks.process_crawl_job": {"rate_limit": "5/m"},
}

# Scheduled tasks (Celery Beat)
beat_schedule={
    "cleanup-old-results": {
        "task": "app.tasks.crawl_tasks.cleanup_old_results",
        "schedule": 86400.0,  # Every 24 hours
    },
    "send-daily-digest": {
        "task": "app.tasks.email_tasks.send_daily_digest",
        "schedule": 86400.0,  # Every 24 hours
    },
}
```

---

## Running Celery

### Development

**Terminal 1: FastAPI Server**
```bash
cd backend
PYTHONPATH=. python -m uvicorn app.main:app --reload
```

**Terminal 2: Celery Worker**
```bash
cd backend
python start_worker.py

# Or manually:
PYTHONPATH=. celery -A app.celery_app worker --loglevel=info --concurrency=2 --pool=solo
```

**Terminal 3: Celery Beat (for scheduled tasks)**
```bash
cd backend
python start_beat.py

# Or manually:
PYTHONPATH=. celery -A app.celery_app beat --loglevel=info
```

### Production

Use a process manager like **Supervisor** or **systemd**.

**Example systemd service (`/etc/systemd/system/celery-worker.service`):**

```ini
[Unit]
Description=Celery Worker for DevSEO
After=network.target redis.service

[Service]
Type=forking
User=devseo
Group=devseo
WorkingDirectory=/var/www/devseo/backend
Environment="PYTHONPATH=/var/www/devseo/backend"
ExecStart=/var/www/devseo/backend/venv/bin/celery -A app.celery_app worker \
    --loglevel=info \
    --concurrency=4 \
    --logfile=/var/log/celery/worker.log \
    --pidfile=/var/run/celery/worker.pid
ExecStop=/bin/kill -s TERM $MAINPID
Restart=always

[Install]
WantedBy=multi-user.target
```

**Example Celery Beat service (`/etc/systemd/system/celery-beat.service`):**

```ini
[Unit]
Description=Celery Beat Scheduler for DevSEO
After=network.target redis.service

[Service]
Type=simple
User=devseo
Group=devseo
WorkingDirectory=/var/www/devseo/backend
Environment="PYTHONPATH=/var/www/devseo/backend"
ExecStart=/var/www/devseo/backend/venv/bin/celery -A app.celery_app beat \
    --loglevel=info \
    --logfile=/var/log/celery/beat.log \
    --pidfile=/var/run/celery/beat.pid
Restart=always

[Install]
WantedBy=multi-user.target
```

**Start services:**
```bash
sudo systemctl enable celery-worker celery-beat
sudo systemctl start celery-worker celery-beat
sudo systemctl status celery-worker celery-beat
```

---

## Usage

### Triggering Tasks from Code

**Example 1: Start Crawl Job**
```python
from app.tasks.crawl_tasks import process_crawl_job

# Send task to queue (non-blocking)
task = process_crawl_job.delay(
    crawl_job_id="123e4567-e89b-12d3-a456-426614174000",
    website_domain="example.com",
    max_pages=50
)

# Get task ID
print(f"Task ID: {task.id}")

# Check task status (optional)
result = task.get(timeout=5)  # Wait max 5 seconds
print(f"Result: {result}")
```

**Example 2: Send Email**
```python
from app.tasks.email_tasks import send_email

send_email.delay(
    to_email="user@example.com",
    subject="Your Crawl is Complete",
    html_content="<h1>Results are ready!</h1>"
)
```

**Example 3: Cancel Crawl**
```python
from app.tasks.crawl_tasks import cancel_crawl_job

cancel_crawl_job.delay(
    crawl_job_id="123e4567-e89b-12d3-a456-426614174000"
)
```

### API Integration

The `/crawls` router now uses Celery automatically:

```python
# app/routers/crawls.py

from app.tasks.crawl_tasks import process_crawl_job

@router.post("/websites/{website_id}/crawl")
async def start_crawl(...):
    # Create crawl job in database
    crawl_job = CrawlJob(website_id=website_id, status="pending")
    db.add(crawl_job)
    await db.commit()

    # Send to Celery queue (non-blocking)
    process_crawl_job.delay(
        str(crawl_job.id),
        website.domain,
        max_pages
    )

    # Return immediately (crawl runs in background)
    return crawl_job
```

---

## Monitoring

### Celery Flower (Web UI)

Install and run Flower for real-time monitoring:

```bash
pip install flower

# Start Flower
celery -A app.celery_app flower --port=5555
```

**Access:** http://localhost:5555

**Features:**
- View active workers
- Monitor task progress
- See task history
- Inspect task details
- Worker statistics

### Command Line Monitoring

**Check active workers:**
```bash
celery -A app.celery_app inspect active
```

**Check registered tasks:**
```bash
celery -A app.celery_app inspect registered
```

**Check task stats:**
```bash
celery -A app.celery_app inspect stats
```

**Purge all tasks from queue:**
```bash
celery -A app.celery_app purge
```

### Redis Monitoring

**Check queue length:**
```bash
redis-cli llen celery

# Or for specific queue
redis-cli llen crawl
redis-cli llen email
```

**Monitor Redis in real-time:**
```bash
redis-cli monitor
```

---

## Task States

Celery tasks go through these states:

1. **PENDING** - Task waiting in queue
2. **STARTED** - Worker picked up task
3. **RETRY** - Task failed, retrying
4. **SUCCESS** - Task completed successfully
5. **FAILURE** - Task failed after all retries

**Check task state:**
```python
from app.celery_app import celery_app

task = celery_app.AsyncResult('task-id-here')
print(f"State: {task.state}")
print(f"Result: {task.result}")
print(f"Info: {task.info}")
```

---

## Error Handling

### Automatic Retries

Tasks automatically retry on failure:

```python
@celery_app.task(
    bind=True,
    max_retries=3,
    default_retry_delay=300,  # 5 minutes
)
def process_crawl_job(self, crawl_job_id, website_domain, max_pages):
    try:
        # Process task
        ...
    except Exception as exc:
        # Retry task
        raise self.retry(exc=exc)
```

### Error Logging

All errors are logged with full traceback:

```python
logger.error(f"Error processing crawl {crawl_job_id}: {exc}", exc_info=True)
```

### Dead Letter Queue

Failed tasks (after all retries) can be inspected:

```bash
# View failed tasks in Flower UI
# Or via command line
celery -A app.celery_app inspect failed
```

---

## Scaling

### Horizontal Scaling

Run multiple workers across multiple machines:

**Server 1:**
```bash
celery -A app.celery_app worker --hostname=worker1@%h --concurrency=4
```

**Server 2:**
```bash
celery -A app.celery_app worker --hostname=worker2@%h --concurrency=4
```

### Queue-Based Scaling

Run dedicated workers for specific queues:

**Crawl worker (heavy tasks):**
```bash
celery -A app.celery_app worker -Q crawl --concurrency=2
```

**Email worker (light tasks):**
```bash
celery -A app.celery_app worker -Q email --concurrency=10
```

### Auto-Scaling

Use `--autoscale` for dynamic worker count:

```bash
celery -A app.celery_app worker --autoscale=10,3
# Min 3 workers, max 10 workers
```

---

## Best Practices

### 1. Task Design

- Keep tasks idempotent (can run multiple times safely)
- Include timeout limits
- Handle errors gracefully
- Log progress and errors

### 2. Resource Management

- Use connection pooling for database
- Close connections properly
- Limit worker concurrency based on available resources

### 3. Monitoring

- Monitor queue lengths (alert if queue grows too large)
- Track task failure rates
- Monitor worker health

### 4. Testing

Test tasks locally before deploying:

```python
# Run task synchronously for testing
result = process_crawl_job(
    crawl_job_id="test-id",
    website_domain="example.com",
    max_pages=10
)
print(result)
```

---

## Troubleshooting

### Worker Not Starting

**Check Redis connection:**
```bash
redis-cli ping
# Should return: PONG
```

**Check Celery app:**
```python
python -c "from app.celery_app import celery_app; print(celery_app.main)"
```

### Tasks Not Executing

**Check workers are running:**
```bash
celery -A app.celery_app inspect active_queues
```

**Check task is in queue:**
```bash
redis-cli llen celery
```

### Tasks Timing Out

Increase timeout limits in `celery_app.py`:

```python
task_time_limit=3600  # 1 hour
task_soft_time_limit=3300  # 55 minutes
```

### High Memory Usage

- Restart workers after N tasks:
  ```python
  worker_max_tasks_per_child=100
  ```
- Reduce concurrency:
  ```bash
  celery worker --concurrency=1
  ```

---

## Production Checklist

- [ ] Redis running and accessible
- [ ] Celery workers running (multiple for redundancy)
- [ ] Celery Beat running (only ONE instance!)
- [ ] Monitoring setup (Flower or similar)
- [ ] Log rotation configured
- [ ] Process management (systemd/supervisor)
- [ ] Auto-restart on failure
- [ ] Health checks enabled
- [ ] Queue length alerts
- [ ] Error rate alerts

---

## Migration from Old Worker

The old polling-based `worker.py` has been replaced with Celery.

**Old approach:**
- `worker.py` polls database every 10 seconds
- Single-threaded processing
- No task queuing
- Limited scalability

**New approach:**
- Event-driven via Redis
- Multi-process workers
- Task queuing and prioritization
- Infinite scalability

**The old `worker.py` file can be kept for reference but is no longer needed.**

---

## Next Steps

1. **Setup Redis in production**
2. **Configure systemd services**
3. **Deploy Celery workers**
4. **Setup monitoring (Flower)**
5. **Configure alerts**
6. **Test failover scenarios**

---

## Resources

- [Celery Documentation](https://docs.celeryproject.org/)
- [Redis Documentation](https://redis.io/docs/)
- [Flower Documentation](https://flower.readthedocs.io/)

---

**Questions?** Contact the development team or refer to Celery best practices documentation.
