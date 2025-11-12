# import os
# from aiokafka import AIOKafkaProducer
# import json

# KAFKA_BOOTSTRAP_SERVERS = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "kafka_pluspoint:9092")

# producer = AIOKafkaProducer(
#     bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS,
#     value_serializer=lambda v: json.dumps(v).encode("utf-8")
# )


import asyncio
from aiokafka import AIOKafkaProducer
import json
from config import settings
producer = None

async def start_producer():
    global producer
    producer = AIOKafkaProducer(
        bootstrap_servers=settings.KAFKA_BOOTSTRAP_SERVERS,
        value_serializer=lambda v: json.dumps(v).encode('utf-8')
    )
    await producer.start()

async def stop_producer():
    await producer.stop()

async def send_kafka_event(title, data):
    await producer.send_and_wait(title, data)