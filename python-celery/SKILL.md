---
name: python-celery
description: Python Celery patterns covering task queues, periodic tasks, task chains, error handling, rate limiting, result backends, monitoring, and production deployment.
---

# Python Celery

This skill should be used when building background task processing with Python Celery. It covers task queues, periodic tasks, chains, error handling, and monitoring.

## When to Use This Skill

Use this skill when you need to:

- Process background tasks asynchronously
- Schedule periodic/cron tasks with Celery Beat
- Chain and group tasks for complex workflows
- Handle task retries and error recovery
- Monitor tasks with Flower or custom backends

## Setup

```bash
pip install celery[redis] celery[sqlalchemy]
```

## Basic Configuration

```python
# celery_app.py
from celery import Celery

app = Celery(
    "myapp",
    broker="redis://localhost:6379/0",
    backend="redis://localhost:6379/1",
)

app.conf.update(
    task_serializer="json",
    result_serializer="json",
    accept_content=["json"],
    timezone="UTC",
    task_track_started=True,
    task_time_limit=300,
    task_soft_time_limit=240,
)
```

## Defining Tasks

```python
from celery_app import app
from celery.utils.log import get_task_logger

logger = get_task_logger(__name__)

@app.task(bind=True, max_retries=3)
def send_email(self, to: str, subject: str, body: str):
    try:
        email_service.send(to=to, subject=subject, body=body)
        logger.info(f"Email sent to {to}")
    except ConnectionError as exc:
        raise self.retry(exc=exc, countdown=60)

@app.task
def process_image(image_id: int, size: tuple):
    image = Image.objects.get(id=image_id)
    resized = resize(image.file, size)
    image.thumbnail = resized
    image.save()
    return {"id": image_id, "status": "processed"}

@app.task(rate_limit="10/m")
def call_external_api(url: str, params: dict):
    response = requests.get(url, params=params)
    return response.json()
```

## Calling Tasks

```python
# Async call
result = send_email.delay("user@example.com", "Welcome", "Hello!")

# With options
result = send_email.apply_async(
    args=["user@example.com", "Welcome", "Hello!"],
    countdown=60,        # delay 60 seconds
    expires=3600,        # expire after 1 hour
    queue="emails",      # specific queue
)

# Check result
print(result.id)
print(result.status)    # PENDING, STARTED, SUCCESS, FAILURE
print(result.get(timeout=10))  # wait for result
```

## Task Chains and Groups

```python
from celery import chain, group, chord

# Chain: sequential tasks
workflow = chain(
    fetch_data.s(url),
    process_data.s(),
    save_results.s(output_path),
)
result = workflow.apply_async()

# Group: parallel tasks
job = group(
    process_image.s(img_id, (100, 100)) for img_id in image_ids
)
result = job.apply_async()

# Chord: group + callback when all complete
callback = generate_report.s()
job = chord(
    [process_item.s(item_id) for item_id in item_ids],
    callback,
)
result = job.apply_async()
```

## Periodic Tasks (Celery Beat)

```python
from celery.schedules import crontab

app.conf.beat_schedule = {
    "cleanup-every-hour": {
        "task": "tasks.cleanup_expired",
        "schedule": 3600.0,  # every hour
    },
    "daily-report": {
        "task": "tasks.generate_daily_report",
        "schedule": crontab(hour=9, minute=0),  # 9 AM daily
    },
    "weekly-digest": {
        "task": "tasks.send_weekly_digest",
        "schedule": crontab(hour=8, minute=0, day_of_week=1),  # Monday 8 AM
    },
}
```

## Error Handling

```python
@app.task(bind=True, max_retries=5, default_retry_delay=30)
def unreliable_task(self, data):
    try:
        result = external_service.process(data)
        return result
    except ServiceUnavailable as exc:
        raise self.retry(exc=exc, countdown=2 ** self.request.retries * 30)
    except InvalidData:
        # Don't retry on bad data
        logger.error(f"Invalid data: {data}")
        return {"error": "invalid data"}

@app.task(bind=True, autoretry_for=(ConnectionError,), retry_backoff=True)
def auto_retry_task(self, url):
    return requests.get(url).json()
```

## Running

```bash
# Worker
celery -A celery_app worker --loglevel=info --concurrency=4

# Beat scheduler
celery -A celery_app beat --loglevel=info

# Monitoring with Flower
pip install flower
celery -A celery_app flower --port=5555
```

## Additional Resources

- Celery: https://docs.celeryq.dev/
- User Guide: https://docs.celeryq.dev/en/stable/userguide/
- Best Practices: https://docs.celeryq.dev/en/stable/userguide/tasks.html#best-practices
