# # import os
# # from aiokafka import AIOKafkaProducer
# # import json

# # KAFKA_BOOTSTRAP_SERVERS = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "kafka_pluspoint:9092")

# # producer = AIOKafkaProducer(
# #     bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS,
# #     value_serializer=lambda v: json.dumps(v).encode("utf-8")
# # )


# import asyncio
# from aiokafka import AIOKafkaProducer
# import json
# from app.config import settings

# producer = None

# async def wait_for_kafka():
#     import socket
#     while True:
#         try:
#             s = socket.create_connection(("kafka_pluspoint", 9092), timeout=2)
#             s.close()
#             print("Kafka is ready!")
#             return
#         except:
#             print("Kafka not ready, retrying in 2s...")
#             await asyncio.sleep(2)
            
            
# async def start_producer():
#     global producer
#     producer = AIOKafkaProducer(
#         bootstrap_servers=settings.KAFKA_BOOTSTRAP_SERVERS,
#         value_serializer=lambda v: json.dumps(v).encode('utf-8')
#     )
#     for _ in range(10):
#         try:
#             await producer.start()
#             print("Kafka producer started")
#             return producer
#         except Exception as e:
#                 print(f"Kafka not ready, retrying in 2s... ({e})")
#                 await asyncio.sleep(2)
#     raise RuntimeError("Kafka producer could not start after retries")

# async def stop_producer():
#     await producer.stop()

# async def send_kafka_event(title, data):
#     await producer.send_and_wait(title, data)