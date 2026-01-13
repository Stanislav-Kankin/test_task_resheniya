import asyncio

from app.clients.deribit import DeribitClient
from app.core.config import settings
from app.core.db import SessionLocal
from app.repositories.price_repo import PriceRepository
from app.services.prices import PricesService

from app.tasks.celery_app import celery_app


@celery_app.task(name="app.tasks.tasks.fetch_price")
def fetch_price(ticker: str) -> None:
    asyncio.run(_fetch_price_async(ticker))


async def _fetch_price_async(ticker: str) -> None:
    client = DeribitClient(base_url=settings.deribit_base_url)

    async with SessionLocal() as session:
        repo = PriceRepository(session)
        service = PricesService(client=client, repo=repo)
        await service.fetch_and_store(ticker)
