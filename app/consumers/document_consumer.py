import logging

from aio_pika.abc import AbstractIncomingMessage, AbstractRobustConnection

from app.services.document_processor import process_document

logger = logging.getLogger(__name__)

QUEUE_NAME = "ai.document-processing"


async def handle_message(message: AbstractIncomingMessage) -> None:
    async with message.process():
        data = message.body.decode()
        logger.info("received: %s", data)
        await process_document(data)


async def start_consuming(connection: AbstractRobustConnection) -> None:
    channel = await connection.channel()
    await channel.set_qos(prefetch_count=10)
    queue = await channel.declare_queue(QUEUE_NAME, durable=True)
    await queue.consume(handle_message)
