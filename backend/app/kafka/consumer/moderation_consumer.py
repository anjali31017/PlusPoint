# import asyncio
# import json
# from aiokafka import AIOKafkaConsumer
# from bson import ObjectId
# from datetime import datetime

# # from app.models.moderation_task import ModerationTaskModel, ModerationTrigger
# from app.config import settings


# class ModerationKafkaConsumer:
#     consumer = None
#     is_running = True

#     @classmethod
#     async def start(cls):
#         while cls.is_running:
#             try:
#                 print("🔵 Connecting Moderation Kafka Consumer...")

#                 cls.consumer = AIOKafkaConsumer(
#                     "moderation.requested",
#                     bootstrap_servers="kafka_pluspoint_1:9092",
#                     group_id="moderation_service_group",
#                     value_deserializer=lambda v: json.loads(v.decode("utf-8")),
#                     auto_offset_reset="earliest",
#                 )

#                 await cls.consumer.start()
#                 print("✅ Moderation Kafka Consumer connected")

#                 async for msg in cls.consumer:
#                     await cls.process_event(msg.value)

#             except Exception as e:
#                 print(f"❌ Moderation Kafka error: {e}")
#                 await asyncio.sleep(5)

#             finally:
#                 if cls.consumer:
#                     await cls.consumer.stop()

#     @classmethod
#     async def process_event(cls, event: dict):
#         try:
#             print("📥 Moderation event received:", event)

#             task = ModerationTaskModel(
#                 article_id=ObjectId(event["article_id"]),
#                 firm_id=ObjectId(event["firm_id"]),
#                 publisher_id=ObjectId(event["publisher_id"]),
#                 trigger=ModerationTrigger(event["trigger"]),
#                 trust_score_snapshot=event["trust_score"],
#                 created_at=datetime.now(),
#             )

#             await task.insert()

#             print(f"📝 Moderation task created for article {event['article_id']}")

#         except Exception as e:
#             print(f"⚠️ Failed to create moderation task: {e}")

#     @classmethod
#     async def shutdown(cls):
#         cls.is_running = False
#         if cls.consumer:
#             await cls.consumer.stop()
