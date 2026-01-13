from celery import Celery
from celery.schedules import crontab

from app.core.config import settings

celery_app = Celery(
    "deribit_prices",
    broker=settings.celery_broker_url,
    backend=settings.celery_result_backend,
    include=["app.tasks.tasks"],
)

celery_app.conf.timezone = "UTC"

celery_app.conf.beat_schedule = {
    "fetch-btc-usd-every-minute": {
        "task": "app.tasks.tasks.fetch_price",
        "schedule": crontab(minute="*/1"),
        "args": ("btc_usd",),
    },
    "fetch-eth-usd-every-minute": {
        "task": "app.tasks.tasks.fetch_price",
        "schedule": crontab(minute="*/1"),
        "args": ("eth_usd",),
    },
}
