import asyncio
import os
import json
import aio_pika
import logging

logging.basicConfig(level=logging.INFO,
                    format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

RABBITMQ_URL = os.getenv(
    "RABBITMQ_URL", "amqp://user:password@localhost:5672/")


async def process_message(message: aio_pika.IncomingMessage):
    async with message.process():
        body = json.loads(message.body.decode())
        event = body.get("event")
        if event == "OrderCreated":
            email = body.get("customer_email")
            order_id = body.get("order_id")
            total_price = body.get("total_price")
            product_name = body.get("product_name")
            logger.info(
                f"SENDING EMAIL to {email}: Your order #{order_id} for '{product_name}' (Total: ${total_price}) has been created successfully")
        else:
            logger.info(f"Received unknown event: {body}")


async def main():
    while True:
        try:
            connection = await aio_pika.connect_robust(RABBITMQ_URL)
            break
        except Exception as e:
            logger.error(f"Waiting for RabbitMQ: {e}")
            await asyncio.sleep(2)

    channel = await connection.channel()
    await channel.set_qos(prefetch_count=1)

    queue = await channel.declare_queue("notifications", durable=True)

    await queue.consume(process_message)

    try:
        await asyncio.Future()
    finally:
        await connection.close()

if __name__ == "__main__":
    asyncio.run(main())
