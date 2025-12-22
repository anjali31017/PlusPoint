from celery import Celery
import os
import asyncio
from celery.signals import worker_process_init
from app.summary.summarization_model import load_summerization_model 
from app.database.connection import connect_to_mongo


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




@worker_process_init.connect
def init_worker_process(**kwargs):
    try:
        # global db, loop
        
        load_summerization_model()
        # loop = asyncio.new_event_loop()
        # asyncio.set_event_loop(loop)
        # db = loop.run_until_complete(connect_to_mongo())
        
        
        print("Child worker process started")
    except Exception as e:
        print("Error initializing worker process:", e)




# @worker_process_shutdown.connect
# def close_db(**kwargs):
#     global db
#     db.close()

# @celery_app.on_after_configure.connect
# def init_worker(sender, **kwargs):
#     print("Worker starting, loading model...")
#     load_model()

# celery_app.autodiscover_tasks(["app"])

# from app.summary.summarization_model import final_summary