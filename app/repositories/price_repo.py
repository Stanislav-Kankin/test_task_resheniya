from sqlalchemy import Select, desc, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.price import Price


class PriceRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def add_price(self, ticker: str, price: float, ts_unix: int) -> Price:
        row = Price(ticker=ticker, price=price, ts_unix=ts_unix)
        self.session.add(row)
        await self.session.commit()
        await self.session.refresh(row)
        return row

    async def get_all(self, ticker: str, limit: int = 10_000, offset: int = 0) -> list[Price]:
        stmt: Select = (
            select(Price)
            .where(Price.ticker == ticker)
            .order_by(Price.ts_unix.asc())
            .limit(limit)
            .offset(offset)
        )
        res = await self.session.execute(stmt)
        return list(res.scalars().all())

    async def get_latest(self, ticker: str) -> Price | None:
        stmt = select(Price).where(Price.ticker == ticker).order_by(desc(Price.ts_unix)).limit(1)
        res = await self.session.execute(stmt)
        return res.scalars().first()

    async def get_range(self, ticker: str, from_ts: int | None, to_ts: int | None) -> list[Price]:
        stmt = select(Price).where(Price.ticker == ticker)
        if from_ts is not None:
            stmt = stmt.where(Price.ts_unix >= from_ts)
        if to_ts is not None:
            stmt = stmt.where(Price.ts_unix <= to_ts)
        stmt = stmt.order_by(Price.ts_unix.asc())

        res = await self.session.execute(stmt)
        return list(res.scalars().all())
