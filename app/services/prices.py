import time

from app.clients.deribit import DeribitClient
from app.repositories.price_repo import PriceRepository


ALLOWED_TICKERS = {"btc_usd", "eth_usd"}


class PricesService:
    def __init__(self, client: DeribitClient, repo: PriceRepository):
        self.client = client
        self.repo = repo

    async def fetch_and_store(self, ticker: str) -> None:
        t = ticker.lower()
        if t not in ALLOWED_TICKERS:
            raise ValueError(f"Unsupported ticker: {ticker}")

        price = await self.client.get_index_price(t)
        ts = int(time.time())
        await self.repo.add_price(ticker=t, price=price, ts_unix=ts)
