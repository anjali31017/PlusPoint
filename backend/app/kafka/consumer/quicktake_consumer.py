import asyncio, json
from aiokafka import AIOKafkaConsumer
from bson import ObjectId
from app.models.subscription import SubscriptionModel
from app.config import settings
from app.sse.sse_endpoint import add_to_recent_articles, sse_connection_manager
from app.models.notification import NotificationStatus
from app.models.article import ArticleLikeModel, ArticleModel
from app.models.endorse import EndorsementModel
from app.models.report import ReportModel


import asyncio
import time
from bson import ObjectId

async def wait_for_article_summary(article_id, timeout=30, interval=2):
    start = time.monotonic()

    while True:
        article = await ArticleModel.find_one(
            ArticleModel.id == ObjectId(article_id),
            ArticleModel.is_deleted == False
        )

        if article and article.summary is not None:
            return article

        if time.monotonic() - start >= timeout:
            return None  # timeout reached

        await asyncio.sleep(interval)



class KafkaQuickTakeService:
    is_running = True
    consumer = None

    @classmethod
    async def consume_quicktake(cls):
        """Kafka Consumer with retry logic."""
        while cls.is_running:
            # await asyncio.sleep(0.1)
            try:
                print("Attempting to connect Kafka Consumer...")

                cls.consumer = AIOKafkaConsumer(
                    "quick.take",
                    bootstrap_servers="kafka_pluspoint_1:9092",
                    group_id="quick_take_service_group_test",
                    value_deserializer=lambda v: json.loads(v.decode('utf-8')),
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
                        
                        article_id = post["article_id"]
                        # liked = await ArticleLikeModel.find_one(ArticleLikeModel.article_id == ObjectId(article_id), ArticleLikeModel.user_id == ObjectId(user_id))
                        # endorsed = await EndorsementModel.find_one(EndorsementModel.article_id == ObjectId(article_id), EndorsementModel.user_id == ObjectId(user_id))
                        # reported = await ReportModel.find_one(ReportModel.article_id == ObjectId(article_id), ReportModel.user_id == ObjectId(user_id), ReportModel.is_deleted == False)
                        
                        await asyncio.sleep(30)
                        
                        # article = await ArticleModel.find_one(ArticleModel.id == ObjectId(article_id), ArticleModel.is_deleted == False)
                        article = await wait_for_article_summary(article_id)
                        
                        if not article:
                            print(f"Summary not ready after timeout for article {article_id}")
                            return  # or handle fallback logic
    
                        article_data = {
                            "firm_id": post["firm_id"],
                            "article_id": post["article_id"],
                            "title": post["title"],
                            "firm_username": post["firm_username"],
                            "summary": article.summary,
                            "likes": post["likes"],
                            "endorse": post["endorse"],
                            "category": post["category"],
                            "tags": post["tags"],
                            "trust_score_snapshot": post["trust_score_snapshot"],
                            "hot_topic": post["hot_topic"],
                            # "liked": bool(liked),
                            # "endorsed": bool(endorsed),
                            # "reported": bool(reported),
                            "published_at": post["published_at"]
                        }

                        await add_to_recent_articles(article_data)
                        await sse_connection_manager.broadcast(article_data)

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
            
       