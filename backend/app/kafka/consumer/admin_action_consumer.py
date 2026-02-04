import asyncio, json
from aiokafka import AIOKafkaConsumer
from app.sse.sse_endpoint import sse_connection_manager
from app.models.notification import NotificationStatus


class KafkaAdminService:
    is_running = True
    consumer = None

    @classmethod
    async def consume_admin_action(cls):
        """Kafka Consumer with retry logic."""
        while cls.is_running:
            try:
                print("Attempting to connect Kafka Consumer...")

                cls.consumer = AIOKafkaConsumer(
                    "admin.action",
                    # bootstrap_servers="kafka_pluspoint_1:9092",
                    bootstrap_servers=[
                        "kafka_pluspoint_1:9092",
                        "kafka_pluspoint_2:9094",
                    ],
                    group_id="notification_service_group_test",
                    value_deserializer=lambda v: json.loads(v.decode("utf-8")),
                    auto_offset_reset="earliest",
                    request_timeout_ms=30000,
                    session_timeout_ms=10000,
                    heartbeat_interval_ms=3000,
                )

                await cls.consumer.start()
                print("Kafka Consumer connected successfully!")

                async for msg in cls.consumer:

                    try:
                        print("Message received from Kafka")
                        post = msg.value

                        user_id = post["user_id"]

                        message = {
                            "status": post["status"],
                            "detail": post["detail"],
                            "article_id": post["article_id"],
                            "firm_id": post["firm_id"],
                        }

                        await asyncio.gather(
                            *[
                                sse_connection_manager.send_to_user(
                                    user_id, message, NotificationStatus.ADMIN
                                )
                            ]
                        )
                        print("Notifications sent to user.")

                    except Exception as process_err:
                        print(f"Error processing message: {process_err}")

            except Exception as conn_err:
                print(f"Kafka connection failed: {conn_err}")
                print("Retrying in 5 seconds...")
                await asyncio.sleep(5)
            except Exception as e:
                print(f"Kafka consumer error: {e}")
                if cls.consumer:
                    await cls.consumer.stop()
                await asyncio.sleep(3)

    @classmethod
    async def shutdown(cls):
        cls.is_running = False
        if cls.consumer:
            try:
                await asyncio.wait_for(cls.consumer.stop(), timeout=5)
            except asyncio.TimeoutError:
                print("Kafka consumer stop timed out")
