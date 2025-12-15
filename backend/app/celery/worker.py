from celery import Celery
import os
# from app.summary.summarization_model import load_model 

celery_app = Celery(
    "pluspoint",
    broker=os.getenv("CELERY_BROKER_URL", "redis://redis_pluspoint:6379/0"),
    backend=os.getenv("CELERY_RESULT_BACKEND", "redis://redis_pluspoint:6379/0"),
    include=["app.celery.summary_tasks"],
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
)


# @celery_app.on_after_configure.connect
# def init_worker(sender, **kwargs):
#     print("Worker starting, loading model...")
#     load_model()

# celery_app.autodiscover_tasks(["app"])

# from app.summary.summarization_model import final_summary