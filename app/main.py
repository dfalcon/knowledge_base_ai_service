import logging
import os
from contextlib import asynccontextmanager

import aio_pika
import asyncpg
from fastapi import FastAPI

from app.api.routers import health
from app.consumers.document_consumer import start_consuming

RABBITMQ_URL = os.getenv("RABBITMQ_URL", "amqp://intellibase:secret@localhost/")
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://knowledge_base:secret@localhost:5432/knowledge_base")
logging.basicConfig(level=logging.INFO)


@asynccontextmanager
async def lifespan(app: FastAPI):
    pool = await asyncpg.create_pool(DATABASE_URL, min_size=2, max_size=10)
    connection = await aio_pika.connect_robust(RABBITMQ_URL)
    await start_consuming(connection, pool)
    try:
        yield
    finally:
        await connection.close()
        await pool.close()


app = FastAPI(lifespan=lifespan)
app.include_router(health.router)
