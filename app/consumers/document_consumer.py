import logging

from aio_pika.abc import AbstractIncomingMessage, AbstractRobustConnection

logger = logging.getLogger(__name__)

QUEUE_NAME = "ai.document-processing"


async def handle_message(message: AbstractIncomingMessage) -> None:
    async with message.process():
        logger.info("received: %s", message.body.decode())


async def start_consuming(connection: AbstractRobustConnection) -> None:
    channel = await connection.channel()
    await channel.set_qos(prefetch_count=10)
    queue = await channel.declare_queue(QUEUE_NAME, durable=True)
    await queue.consume(handle_message)
