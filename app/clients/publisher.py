import uuid
from datetime import UTC, datetime

import aio_pika
from aio_pika.abc import AbstractChannel, AbstractExchange

from app.schemas.document import DocumentIndexedEvent

EXCHANGE = "intellibase.events"
ROUTING_KEY = "document.indexed"


async def declare_exchange(channel: AbstractChannel) -> AbstractExchange:
    return await channel.declare_exchange(EXCHANGE, aio_pika.ExchangeType.TOPIC, durable=True)


async def publish_indexed(exchange: AbstractExchange, document_id: uuid.UUID) -> None:
    event = DocumentIndexedEvent(
        version="1.0",
        event=ROUTING_KEY,
        document_id=document_id,
        message_id=uuid.uuid4(),
        timestamp=datetime.now(UTC),
    )
    await exchange.publish(
        aio_pika.Message(
            event.model_dump_json().encode(),
            content_type="application/json",
            delivery_mode=aio_pika.DeliveryMode.PERSISTENT,
        ),
        routing_key=ROUTING_KEY,
    )
