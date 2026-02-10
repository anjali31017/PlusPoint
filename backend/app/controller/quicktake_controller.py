import asyncio
from datetime import datetime, timezone
from bson import ObjectId
from app.kafka.producer import send_kafka_event
from app.models.article import ArticleModel
import time

async def wait_for_article_summary(article_id, timeout=250, interval=30):
    start = time.monotonic()

    while True:
        article = await ArticleModel.find_one(
            ArticleModel.id == ObjectId(article_id),
            ArticleModel.is_deleted == False
        )

        if article and article.summary is not None:
            firm = await article.firm_id.fetch()
            data = {
                "article": article,
                "firm": firm,
            }
            print("@@@@@######", data)
            return data

        if time.monotonic() - start >= timeout:
            return None  # timeout reached

        await asyncio.sleep(interval)

async def push_quicktake(article_id:str, current_user:dict):
    try:
        data = await wait_for_article_summary(article_id)
        if not data:
            print(f"Summary not ready after timeout for article {article_id}")
            return True
        
        article = data["article"]
        firm = data["firm"]
    
        kafka_quick_take_event = {
            "event_type": "quick.take",
            "user_id": str(current_user["user_id"]),
            "firm_id": str(firm.id),
            "article_id": str(article.id),
            "title": article.title,
            "firm_username": firm.firm_username,
            "summary": article.summary,
            "likes": article.like_count,
            "endorse": article.endorse_count,
            "category":article.category,
            "tags":article.tags,
            "trust_score_snapshot":article.trust_score_snapshot,
            "hot_topic": article.hot_topic,
            "published_at": (
                article.published_at.isoformat()
                if article.published_at
                else datetime.now(timezone.utc).isoformat()
            ),
            }
        
        print("##########",kafka_quick_take_event)
        await send_kafka_event("quick.take", kafka_quick_take_event)

        # background_tasks.add_task(
        #     send_kafka_event,
        #     "quick.take", 
        #     kafka_quick_take_event
        #     )
        return True
    
    except Exception as e:
        print(str(e))
        return False