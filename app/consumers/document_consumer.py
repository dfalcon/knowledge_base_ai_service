import logging
from functools import partial

import asyncpg
from aio_pika.abc import AbstractExchange, AbstractIncomingMessage, AbstractRobustConnection
from pydantic import ValidationError

from app.clients.publisher import declare_exchange, publish_indexed
from app.schemas.document import DocumentUploadedEvent
from app.services.document_processor import process_document

logger = logging.getLogger(__name__)

QUEUE_NAME = "ai.document-processing"
ROUTING_KEY_UPLOADED = "document.uploaded"
SUPPORTED_VERSION = "1.0"


async def handle_message(
    message: AbstractIncomingMessage, pool: asyncpg.Pool, exchange: AbstractExchange
) -> None:
    async with message.process():
        try:
            event = DocumentUploadedEvent.model_validate_json(message.body)
        except ValidationError as e:
            logger.warning("malformed document.uploaded: %s | body=%r", e, message.body)
            return

        if event.version != SUPPORTED_VERSION:
            logger.warning("unexpected event version: %s", event.version)

        logger.info("received: document:%s", event)
        await process_document(event, pool)
        await publish_indexed(exchange, event.document_id)


async def start_consuming(connection: AbstractRobustConnection, pool: asyncpg.Pool) -> None:
    channel = await connection.channel()
    await channel.set_qos(prefetch_count=10)
    exchange = await declare_exchange(channel)
    queue = await channel.declare_queue(QUEUE_NAME, durable=True)

    await queue.bind(exchange, ROUTING_KEY_UPLOADED)
    await queue.consume(partial(handle_message, pool=pool, exchange=exchange))
