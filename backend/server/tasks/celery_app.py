from __future__ import annotations
from celery import Celery
from ..core.config import settings

celery_app = Celery(
    "rag",
    broker=settings.REDIS_URL,
    backend=settings.REDIS_URL,
)

celery_app.conf.update(
    task_acks_late=True,
    worker_prefetch_multiplier=1,
    task_time_limit=600,
)
