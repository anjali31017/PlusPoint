import asyncio
from app.celery.worker import celery_app
from app.summary.summarization_model import clean_html, chunk_text, summarize, load_model, update_summary


# @celery_app.on_after_configure.connect
# def init_worker(sender, **kwargs):
#     print("Worker starting, loading model...")
#     load_model()


@celery_app.task(
    name="final_summary",
    bind=True,
    autoretry_for=(Exception,),
    retry_backoff=5,
    retry_kwargs={"max_retries": 3},
)
def final_summary(self, html_text, article_id=None):
    
    try:
        load_model()
        cleaned = clean_html(html_text)
        chunks = chunk_text(cleaned, max_tokens=400)
        chunk_summaries = [summarize(c) for c in chunks]
        combined_summary_text = " ".join(chunk_summaries)
        final_summary = summarize(combined_summary_text)
        asyncio.run(update_summary(article_id, final_summary))
        return {
            "cleaned_text": cleaned,
            "chunks": chunks,
            "chunk_summaries": chunk_summaries,
            "final_summary": final_summary
        }
    except Exception as e:
        print("Final summary error:", str(e))
        raise self.retry(exc=e)
    
    # # load_model()
    # # Step 1: Clean
    # cleaned = clean_html(html_text)

    # # Step 2: Chunk
    # chunks = chunk_text(cleaned, max_tokens=400)

    # print(f"Total chunks: {len(chunks)}")

    # # Step 3: Summaries of chunks
    # chunk_summaries = []
    # for i, chunk in enumerate(chunks, start=1):
    #     print(f"Summarizing chunk {i}/{len(chunks)}...")
    #     summary = summarize(chunk)
    #     chunk_summaries.append(summary)

    # # Step 4: Combine partial summaries
    # combined_summary_text = " ".join(chunk_summaries)

    # # Step 5: Final summary pass
    # print("Generating final summary...")
    # final_summary = summarize(combined_summary_text)
    
    # # #db connection
    # # asyncio.run(connect_to_mongo())
    
    # # db entry
    # asyncio.run(update_summary(article_id, final_summary))
    
    # # asyncio.run(article_controller.update_article(ObjectId(article_id), {"summary": final_summary}))
    
    # print("db updated")
    
    
    # return {
    #     "cleaned_text": cleaned,
    #     "chunks": chunks,
    #     "chunk_summaries": chunk_summaries,
    #     "final_summary": final_summary
    # }


