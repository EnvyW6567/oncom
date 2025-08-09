from fastapi import FastAPI

from app.infrastructure.database.postgres_db import engine
from app.infrastructure.model.model import Base
from app.presentation.accounting_controller import router

app = FastAPI(title="Accounting API", version="1.0.0")

app.include_router(router)


@app.on_event("startup")
async def startup():
    # DB 테이블 생성 (이미 있으면 무시)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
