import asyncio, json
from aiokafka import AIOKafkaConsumer
from app.models import subscriptions, feeds
# from .celery_app import run_recommendation_task

connected_ws = {}  # user -> WebSocket connections

async def consume_posts():
    consumer = AIOKafkaConsumer(
        'posts',
        bootstrap_servers='localhost:9092',
        value_deserializer=lambda v: json.loads(v.decode('utf-8'))
    )
    await consumer.start()
    try:
        async for msg in consumer:
            post = msg.value
            author = post["user"]
            content = post["content"]

            for user, subs in subscriptions.items():
                if author in subs:
                    feeds.setdefault(user, []).append(f"{author}: {content}")
                    if user in connected_ws:
                        for ws in connected_ws[user]:
                            await ws.send_text(f"New post from {author}: {content}")
    finally:
        await consumer.stop()


async def consume_user_activity():
    consumer = AIOKafkaConsumer(
        'user-activity',
        bootstrap_servers='localhost:9092',
        value_deserializer=lambda v: json.loads(v.decode('utf-8'))
    )
    await consumer.start()
    try:
        async for msg in consumer:
            event = msg.value
            event_type = event["event"]
            user = event["user_id"]

            print(f"[Kafka] User activity: {event}")

            # Trigger notifications or tasks based on event
            if event_type == "liked":
                # Notify the author of the liked post
                post_id = event["target"]
                print(f"User {user} liked {post_id}")
                run_recommendation_task.delay(user)

            elif event_type == "commented":
                post_id = event["target"]
                comment = event["comment"]
                print(f"User {user} commented on {post_id}: {comment}")
                # could trigger analytics or author notifications

            elif event_type == "subscribed":
                print(f"User {user} subscribed to {event['target']}")
                # optional: update analytics or relationships DB
    finally:
        await consumer.stop()
