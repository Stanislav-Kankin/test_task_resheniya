from dataclasses import dataclass
from typing import Optional, List

import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.api.prices import get_repo


@dataclass
class PriceRow:
    ticker: str
    price: float
    ts_unix: int


class FakeRepo:
    def __init__(self, data: List[PriceRow]):
        self._data = data

    async def get_all(self, ticker: str, limit: int = 10_000, offset: int = 0):
        rows = [r for r in self._data if r.ticker == ticker]
        return rows[offset: offset + limit]

    async def get_latest(self, ticker: str):
        rows = [r for r in self._data if r.ticker == ticker]
        if not rows:
            return None
        return max(rows, key=lambda r: r.ts_unix)

    async def get_range(self, ticker: str, from_ts: Optional[int], to_ts: Optional[int]):
        rows = [r for r in self._data if r.ticker == ticker]
        if from_ts is not None:
            rows = [r for r in rows if r.ts_unix >= from_ts]
        if to_ts is not None:
            rows = [r for r in rows if r.ts_unix <= to_ts]
        return sorted(rows, key=lambda r: r.ts_unix)


@pytest.fixture()
def client():
    data = [
        PriceRow(ticker="btc_usd", price=100.0, ts_unix=10),
        PriceRow(ticker="btc_usd", price=110.0, ts_unix=20),
        PriceRow(ticker="eth_usd", price=200.0, ts_unix=15),
    ]

    async def _override_repo():
        return FakeRepo(data)

    app.dependency_overrides[get_repo] = _override_repo
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


def test_latest_ok(client: TestClient):
    r = client.get("/prices/latest", params={"ticker": "btc_usd"})
    assert r.status_code == 200
    body = r.json()
    assert body["ticker"] == "btc_usd"
    assert body["price"] == 110.0
    assert body["ts_unix"] == 20


def test_latest_404_when_no_data(client: TestClient):
    # temporarily override repo to simulate 'allowed ticker but no rows'
    old = app.dependency_overrides[get_repo]

    async def _override_repo_empty():
        return FakeRepo([])

    app.dependency_overrides[get_repo] = _override_repo_empty
    r = client.get("/prices/latest", params={"ticker": "btc_usd"})
    assert r.status_code == 404

    app.dependency_overrides[get_repo] = old


def test_invalid_ticker_validation(client: TestClient):
    r = client.get("/prices/latest", params={"ticker": "btc_usd2"})
    assert r.status_code == 422


def test_get_all_ok(client: TestClient):
    r = client.get("/prices", params={"ticker": "btc_usd", "limit": 100, "offset": 0})
    assert r.status_code == 200
    body = r.json()
    assert isinstance(body, list)
    assert len(body) == 2
    assert body[0]["ticker"] == "btc_usd"


def test_range_ok(client: TestClient):
    r = client.get("/prices/range", params={"ticker": "btc_usd", "from_ts": 15, "to_ts": 30})
    assert r.status_code == 200
    body = r.json()
    assert len(body) == 1
    assert body[0]["ts_unix"] == 20


def test_ticker_required(client: TestClient):
    r = client.get("/prices/latest")
    assert r.status_code == 422
