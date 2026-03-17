import os
from celery import Celery
from dotenv import load_dotenv

load_dotenv()

REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")

celery_app = Celery(
    "ai_landing_generator",
    broker=REDIS_URL,
    backend=REDIS_URL,
    include=[
        "app.tasks.email_tasks",
        "app.tasks.subscription_tasks",  # ДОБАВЬТЕ СЮДА ПУТЬ К ВАШЕМУ ФАЙЛУ С ЗАДАЧЕЙ
    ]
)

celery_app.conf.update(
    result_backend=REDIS_URL,

    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    
    # Настройки воркеров
    worker_prefetch_multiplier=1,
    task_acks_late=True,
    
    # Настройки задач
    task_track_started=True,
    task_time_limit=30 * 60,  # 30 минут
    task_soft_time_limit=25 * 60,  # 25 минут
    
    # Настройки retry
    task_default_retry_delay=60,  # 1 минута
    task_max_retries=3,
)

celery_app.autodiscover_tasks(["app.tasks"])

celery_app.conf.beat_schedule = {
    "deactivate-expired-subscriptions-every-5-min": {
        "task": "subscriptions.deactivate_expired",
        "schedule": 300.0,
    },
}

if __name__ == "__main__":
    celery_app.start()
