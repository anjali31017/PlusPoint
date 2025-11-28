import datetime
import asyncio, json
from aiokafka import AIOKafkaConsumer
from bson import ObjectId
from app.models.subscription import SubscriptionModel
from app.config import settings
# from .celery_app import run_recommendation_task
from app.websocket.websocket_endpoints import article_notification_manager

from app.sse.sse_endpoint import sse_connection_manager

import asyncio
import json
from aiokafka import AIOKafkaConsumer
from app.config import settings
from datetime import datetime


class KafkaConsumerService:
    is_running = True
    consumer = None

    @classmethod
    async def consume_posts(cls):
        """Kafka Consumer with retry logic."""
        while cls.is_running:
            try:
                print("Attempting to connect Kafka Consumer...")

                cls.consumer = AIOKafkaConsumer(
                    'article_published',
                    bootstrap_servers=settings.KAFKA_BOOTSTRAP_SERVERS,
                    group_id="notification_service_group_test",
                    value_deserializer=lambda v: json.loads(v.decode('utf-8')),
                    auto_offset_reset="earliest",
                )

                await cls.consumer.start()
                print("Kafka Consumer connected successfully!")

                async for msg in cls.consumer:

                    try:
                        print("Message received from Kafka")
                        post = msg.value

                        if post.get("event_type") != "article_published":
                            continue

                        firm_id = post["firm_id"]
                        publisher_id = post["publisher_id"]
                        
                        firm_obj_id = ObjectId(firm_id)
                        publisher_obj_id = ObjectId(publisher_id)
                        article = {
                            "article_id": post["article_id"],
                            "article_title": post["article_title"],
                            "article_firm": post["firm_username"],
                            "article_publisher": post["publisher_username"],
                            "published_at": post["published_at"]
                        }
                        
                        firm_subscribers = await SubscriptionModel.find(SubscriptionModel.firm_id.id == firm_obj_id).to_list()
                        publisher_subscribers = await SubscriptionModel.find(SubscriptionModel.publisher_id.id == publisher_obj_id).to_list()
                        firm_subscribers_id = [str(sub.subscriber_id.ref.id) for sub in firm_subscribers]
                        publisher_subscribers_id = [str(sub.subscriber_id.ref.id) for sub in publisher_subscribers]
                        all_subscribers = []
                        if firm_subscribers is not None or publisher_subscribers is not None:
                            all_subscribers = firm_subscribers_id + publisher_subscribers_id
                            all_subscribers = list(set(all_subscribers))
                        
                        
                        # firm_subscriptions = await SubscriptionModel.find(SubscriptionModel.firm_id.id == firm_obj_id).to_list()
                        # print(f"Firm Subscriptions: {firm_subscriptions}")
                        # subscriber_ids = [sub.subscriber_id.id for sub in firm_subscriptions]
                        # firm_iddddd = 
                        # subscriber_ids = [sub.subscriber_id.link for sub in firm_subscriptions]
                        # print(f"Firm Subscriber IDs: {subscriber_ids}")
                        
                        # all_subscribers = None
                        # query = {"$or": []}

                        # if firm_id:
                        #     query["$or"].append({"firm_id.id": ObjectId(firm_id)})
                        # if publisher_id:
                        #     query["$or"].append({"publisher_id.id": ObjectId(publisher_id)})

                        # # If no conditions, return empty list
                        # if not query["$or"]:
                        #     return []

                        # subscriptions = await SubscriptionModel.find(query).to_list()
                        # subscriber_ids = [sub.subscriber_id.id for sub in subscriptions]
                        # print(f"Subscriber IDs: {subscriber_ids}")
                        # all_subscribers = list(set(subscriber_ids))
    
                        # firm_subscribers = await SubscriptionModel.find(
                        #     SubscriptionModel.firm_id.id == ObjectId(firm)
                        # ).to_list()

                        # publisher_subscribers = await SubscriptionModel.find(
                        #     SubscriptionModel.publisher_id.id == ObjectId(publisher)
                        # ).to_list()

                        # if firm_subscribers:
                        #     firm_ids = [str(sub.id) for sub in firm_subscribers]
                        # if publisher_subscribers:
                        #     publisher_ids = [str(sub.id) for sub in publisher_subscribers]
                            
                        # if firm_subscribers:
                        #     all_subscribers = set(firm_ids)
                        # if publisher_subscribers:
                        #     all_subscribers = set(publisher_ids)
                        # if firm_subscribers and publisher_subscribers:
                        #     all_subscribers = set(firm_ids).union(set(publisher_ids))
                            
                        # print(f"Firm Subscribers: {firm_subscribers}")
                        # print(f"Publisher Subscribers: {publisher_subscribers}")
                        # all_subscribers = {
                        #     str(sub.subscriber_id.get_link()) 
                        #     for sub in (firm_subscribers + publisher_subscribers)
                        # }
                        # all_subscribers = {str(sub.subscriber_id) for sub in (firm_subscribers.id + publisher_subscribers.id)}
                        # print(f"All Subscribers: {all_subscribers}")
                        # all_subscribers = {
                        #     str(sub.subscriber_id) if isinstance(sub.subscriber_id, ObjectId) else str(sub.subscriber_id.id)
                        #     for sub in (firm_subscribers + publisher_subscribers)
                        # }
                        
                        if not all_subscribers:
                            continue 
                        
                        message = {
                            "type": "new_article",
                            "data": article
                        }
                        # await sse_connection_manager.send_to_user("692052180cbaa9500904c230", message)
                        if all_subscribers:
                            # print(f"Sending notifications to subscribers: {all_subscribers}")
                            await asyncio.gather(*[
                                # article_notification_manager.send_personal_message(message, sid)
                                sse_connection_manager.send_to_user(sid, message)
                                for sid in all_subscribers
                            ])
                            print("Notifications sent to subscribers.")

                    except Exception as process_err:
                        print(f"Error processing message: {process_err}")

            except Exception as conn_err:
                print(f"Kafka connection failed: {conn_err}")
                print("Retrying in 5 seconds...")
                await asyncio.sleep(5)

            # finally:
            #     if cls.consumer:
            #         try:
            #             await asyncio.wait_for(cls.consumer.stop(), timeout=5)
            #         except asyncio.TimeoutError:
            #             print("Kafka consumer stop timed out")
            #         cls.consumer = None

#----------------------------
#  PENDING NOTIFICAITON
#----------------------------
# # Store notification
# await Notifications.create(user_id=subscriber_id, message=message)

# # When user connects
# pending_notifications = await Notifications.find(user_id=user.id, sent=False).to_list()
# for note in pending_notifications:
#     await article_notification_manager.send_personal_message(note.message, user.id)
#     note.sent = True
#     await note.save()


    @classmethod
    async def shutdown(cls):
        cls.is_running = False
        if cls.consumer:
            try:
                await asyncio.wait_for(cls.consumer.stop(), timeout=5)
            except asyncio.TimeoutError:
                print("Kafka consumer stop timed out")  

# class KafkaConsumerService:
#     async def consume_posts():
#         consumer = AIOKafkaConsumer(
#             'article_published',
#             bootstrap_servers=settings.KAFKA_BOOTSTRAP_SERVERS,
#             group_id="notification_service_group",
#             value_deserializer=lambda v: json.loads(v.decode('utf-8'))
#         )
#         await consumer.start()
#         try:
#             async for msg in consumer:
#                 post = msg.value
#                 if post.get("event_type") == "article_published":
#                     firm = post["firm_id"]
#                     publisher = post["publisher_id"]
#                 # content = post["content"]
#                     article = {
#                         "article_id": post["article_id"],
#                         "article_title": post["title"],
#                         "article_firm": post["firm_username"],
#                         "article_publisher": post["publisher_username"],
#                         "published_at": post["published_at"]
#                     }
#                 # for user, subs in subscriptions.items():
#                     firm_subscribers = await SubscriptionModel.find(SubscriptionModel.firm_id == firm).to_list()
#                     publisher_subscribers = await SubscriptionModel.find(SubscriptionModel.firm_id == publisher).to_list()
                    
#                     all_subscribers = {sub.subscriber_id for sub in firm_subscribers + publisher_subscribers}

#                     for subscriber_id in all_subscribers:
#                         # message = f"New article published: {article['article_title']} by {article['article_publisher']} (Firm: {article['article_firm']})"
#                         message = json.dumps({
#                             "type": "new_article",
#                             "data": article
#                         })
#                         for subscriber_id in all_subscribers:
#                             await article_notification_manager.send_personal_message(
#                                 message, subscriber_id
#                             )
                                
#                         # await NotificationModel.create(
#                         #     subscriber_id=subscriber_id,
#                         #     article_id=article["article_id"],
#                         #     message=message,
#                         #     created_at=datetime.now()
#                         # )
                        
                        
                        
#                     # # subscribers = await db.subscriptions.find({"publisher_id": author}).to_list(length=None)
#                     # for sub in subscribers:
#                     #     user = sub["subscriber_id"]
                        
#                     #     if author in subs:
#                     #         feeds.setdefault(user, []).append(f"{author}: {content}")
#                     #         if user in connected_ws:
#                     #             for ws in connected_ws[user]:
#                     #                 await ws.send_text(f"New post from {author}: {content}")
#         except Exception as e:
#             print(f"Error processing message: {e}")
#         finally:
#             await consumer.stop()
        


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
