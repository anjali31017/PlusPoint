import asyncio
from app.celery.worker import celery_app
from app.summary.summarization_model import end_summary


@celery_app.task(
    name="summerization_task",
    bind=True,
    autoretry_for=(Exception,),
    retry_backoff=5,
    retry_kwargs={"max_retries": 3},
)
def summerization_task(self, html_text, article_id=None):
    try:
        result = end_summary(self, html_text, article_id)
        return result
    except Exception as e:
        # print("Final summary error:", str(e))
        raise self.retry(exc=e)
    
    
