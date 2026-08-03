import logging
from contextlib import asynccontextmanager

import aio_pika
from fastapi import FastAPI

from app.api.routers import health
from app.consumers.document_consumer import start_consuming

RABBITMQ_URL = "amqp://intellibase:secret@localhost/"
logging.basicConfig(level=logging.INFO)

@asynccontextmanager
async def lifespan(app: FastAPI):
    connection = await aio_pika.connect_robust(RABBITMQ_URL)
    await start_consuming(connection)
    try:
        yield
    finally:
        await connection.close()


app = FastAPI(lifespan=lifespan)
app.include_router(health.router)
