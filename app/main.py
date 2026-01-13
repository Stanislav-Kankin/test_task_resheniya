from fastapi import FastAPI

from app.core.db import init_db

app = FastAPI(title="Deribit Prices API")


@app.on_event("startup")
async def on_startup() -> None:
    await init_db()


@app.get("/health")
async def health() -> dict:
    return {"status": "ok"}
