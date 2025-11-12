import datetime
import asyncio, json
from aiokafka import AIOKafkaConsumer
from app.models.subscription import SubscriptionModel
from config import settings
# from .celery_app import run_recommendation_task
from app.websocket.websocket_endpoints import article_notification_manager

class KafkaConsumerService:
    async def consume_posts():
        consumer = AIOKafkaConsumer(
            'article_published',
            bootstrap_servers=settings.KAFKA_BOOTSTRAP_SERVERS,
            group_id="notification_service_group",
            value_deserializer=lambda v: json.loads(v.decode('utf-8'))
        )
        await consumer.start()
        try:
            async for msg in consumer:
                post = msg.value
                if post.get("event_type") == "article_published":
                    firm = post["firm_id"]
                    publisher = post["publisher_id"]
                # content = post["content"]
                    article = {
                        "article_id": post["article_id"],
                        "article_title": post["title"],
                        "article_firm": post["firm_username"],
                        "article_publisher": post["publisher_username"],
                        "published_at": post["published_at"]
                    }
                # for user, subs in subscriptions.items():
                    firm_subscribers = await SubscriptionModel.find(SubscriptionModel.firm_id == firm).to_list()
                    publisher_subscribers = await SubscriptionModel.find(SubscriptionModel.firm_id == publisher).to_list()
                    
                    all_subscribers = {sub.subscriber_id for sub in firm_subscribers + publisher_subscribers}

                    for subscriber_id in all_subscribers:
                        # message = f"New article published: {article['article_title']} by {article['article_publisher']} (Firm: {article['article_firm']})"
                        message = json.dumps({
                            "type": "new_article",
                            "data": article
                        })
                        for subscriber_id in all_subscribers:
                            await article_notification_manager.send_personal_message(
                                message, subscriber_id
                            )
                                
                        # await NotificationModel.create(
                        #     subscriber_id=subscriber_id,
                        #     article_id=article["article_id"],
                        #     message=message,
                        #     created_at=datetime.now()
                        # )
                        
                        
                        
                    # # subscribers = await db.subscriptions.find({"publisher_id": author}).to_list(length=None)
                    # for sub in subscribers:
                    #     user = sub["subscriber_id"]
                        
                    #     if author in subs:
                    #         feeds.setdefault(user, []).append(f"{author}: {content}")
                    #         if user in connected_ws:
                    #             for ws in connected_ws[user]:
                    #                 await ws.send_text(f"New post from {author}: {content}")
        except Exception as e:
            print(f"Error processing message: {e}")
        finally:
            await consumer.stop()
        


    # async def consume_user_activity():
    #     consumer = AIOKafkaConsumer(
    #         'user-activity',
    #         bootstrap_servers=settings.KAFKA_BOOTSTRAP_SERVERS,
    #         value_deserializer=lambda v: json.loads(v.decode('utf-8'))
    #     )
    #     await consumer.start()
    #     try:
    #         async for msg in consumer:
    #             event = msg.value
    #             event_type = event["event"]
    #             user = event["user_id"]

    #             print(f"[Kafka] User activity: {event}")

    #             # Trigger notifications or tasks based on event
    #             if event_type == "liked":
    #                 # Notify the author of the liked post
    #                 post_id = event["target"]
    #                 print(f"User {user} liked {post_id}")
    #                 # run_recommendation_task.delay(user)

    #             elif event_type == "commented":
    #                 post_id = event["target"]
    #                 comment = event["comment"]
    #                 print(f"User {user} commented on {post_id}: {comment}")
    #                 # could trigger analytics or author notifications

    #             elif event_type == "subscribed":
    #                 print(f"User {user} subscribed to {event['target']}")
    #                 # optional: update analytics or relationships DB
    #     finally:
    #         await consumer.stop()
