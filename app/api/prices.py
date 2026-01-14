from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db import SessionLocal
from app.schemas.price import PriceOut
from app.repositories.price_repo import PriceRepository

router = APIRouter(prefix="/prices", tags=["prices"])


async def get_session() -> AsyncSession:
    async with SessionLocal() as session:
        yield session


async def get_repo(session: AsyncSession = Depends(get_session)) -> PriceRepository:
    return PriceRepository(session)


ALLOWED_TICKERS = {"btc_usd", "eth_usd"}


def normalize_ticker(ticker: str) -> str:
    t = ticker.strip().lower()
    if t not in ALLOWED_TICKERS:
        raise HTTPException(
            status_code=422,
            detail="ticker must be one of: btc_usd, eth_usd",
        )
    return t


@router.get("", response_model=List[PriceOut])
async def get_all_prices(
    ticker: str = Query(..., description="Ticker, например btc_usd или eth_usd"),
    limit: int = Query(1000, ge=1, le=10000),
    offset: int = Query(0, ge=0),
    repo: PriceRepository = Depends(get_repo),
):
    t = normalize_ticker(ticker)
    rows = await repo.get_all(ticker=t, limit=limit, offset=offset)
    return [PriceOut.from_orm(r) for r in rows]


@router.get("/latest", response_model=PriceOut)
async def get_latest_price(
    ticker: str = Query(..., description="Ticker, например btc_usd или eth_usd"),
    repo: PriceRepository = Depends(get_repo),
):
    t = normalize_ticker(ticker)
    row = await repo.get_latest(ticker=t)
    if row is None:
        raise HTTPException(status_code=404, detail="No data for ticker")
    return PriceOut.from_orm(row)


@router.get("/range", response_model=List[PriceOut])
async def get_prices_range(
    ticker: str = Query(..., description="Ticker, например btc_usd или eth_usd"),
    from_ts: Optional[int] = Query(None, description="UNIX timestamp (inclusive)"),
    to_ts: Optional[int] = Query(None, description="UNIX timestamp (inclusive)"),
    repo: PriceRepository = Depends(get_repo),
):
    t = normalize_ticker(ticker)
    rows = await repo.get_range(ticker=t, from_ts=from_ts, to_ts=to_ts)
    return [PriceOut.from_orm(r) for r in rows]
