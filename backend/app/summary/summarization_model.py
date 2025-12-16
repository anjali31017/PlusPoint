import asyncio
import re
from bson import ObjectId
from transformers import BartTokenizer, BartForConditionalGeneration
import torch 
from app.controller.article_controller import ArticleController
from app.database.connection import connect_to_mongo, close_mongo_connection

# device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

# BASE_DIR = os.path.dirname(os.path.abspath(__file__))
# model_path = os.path.join(BASE_DIR, "bart_lora")

# tokenizer = BartTokenizer.from_pretrained('/app/app/summary/bart_lora')
# model = BartForConditionalGeneration.from_pretrained('/app/app/summary/bart_lora').to(device)
# Load the fine-tuned model
# tokenizer = BartTokenizer.from_pretrained('./bart_lora')
# model = BartForConditionalGeneration.from_pretrained('./bart_lora').to(device)

article_controller = ArticleController()



model = None
tokenizer = None
device = None


def load_model():
    try:
        print("LOADINGGG MODEL")
        global model, tokenizer, device
        if model is None or tokenizer is None:
            device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
            tokenizer = BartTokenizer.from_pretrained('/app/app/summary/bart_lora')
            model = BartForConditionalGeneration.from_pretrained('/app/app/summary/bart_lora').to(device)
    except Exception as e:
        str(e)
    
    
def clean_html(html_text):
    try:
        print("CLEANINGGG")
        # Remove media elements explicitly
        html_text = re.sub(r'<img[^>]*>', '', html_text, flags=re.IGNORECASE)
        html_text = re.sub(r'<video[^>]*>.*?</video>', '', html_text, flags=re.DOTALL | re.IGNORECASE)
        html_text = re.sub(r'<audio[^>]*>.*?</audio>', '', html_text, flags=re.DOTALL | re.IGNORECASE)
        html_text = re.sub(r'<iframe[^>]*>.*?</iframe>', '', html_text, flags=re.DOTALL | re.IGNORECASE)
        html_text = re.sub(r'<embed[^>]*>', '', html_text, flags=re.IGNORECASE)
        html_text = re.sub(r'<object[^>]*>.*?</object>', '', html_text, flags=re.DOTALL | re.IGNORECASE)
        html_text = re.sub(r'<source[^>]*>', '', html_text, flags=re.IGNORECASE)
        html_text = re.sub(r'<track[^>]*>', '', html_text, flags=re.IGNORECASE)
        html_text = re.sub(r'<picture[^>]*>.*?</picture>', '', html_text, flags=re.DOTALL | re.IGNORECASE)

        # Remove script/style tags and content
        html_text = re.sub(r'<(script|style).*?>.*?</\1>', '', html_text, flags=re.DOTALL | re.IGNORECASE)

        # Remove ALL remaining HTML tags
        html_text = re.sub(r'<[^>]+>', '', html_text)

        # Normalize whitespace
        html_text = re.sub(r'\s+', ' ', html_text).strip()

        return html_text

    except Exception as e:
        print("clean_html error:", e)
        return html_text
    # try:
    #     # Remove script/style
    #     html_text = re.sub(r'<(script|style).*?>.*?</\1>', '', html_text, flags=re.DOTALL)
    #     # Remove tags
    #     html_text = re.sub(r'<[^>]+>', '', html_text)
    #     # Replace multiple spaces/newlines
    #     html_text = re.sub(r'\s+', ' ', html_text).strip()
    #     return html_text
    # except Exception as e:
    #     str(e)
    #     return html_text


def chunk_text(text, max_tokens=400):
    try:
        print("CHUNKINGGG")
        words = text.split()
        chunks = []
        current = []

        for w in words:
            current.append(w)
            token_len = len(tokenizer(" ".join(current))["input_ids"])
            if token_len > max_tokens:
                current.pop()
                chunks.append(" ".join(current))
                current = [w]

        if current:
            chunks.append(" ".join(current))

        return chunks
    except Exception as e:
        print("Chunk text error:", e)
        return [text]

def summarize(text):
    try:
        print("SUMMERIZEEE")
        inputs = tokenizer(text, return_tensors="pt", max_length=512, truncation=True)
        inputs = {k: v.to(device) for k, v in inputs.items()}

        summary_ids = model.generate(
            inputs['input_ids'],
            # max_length=50,
            # min_length=60,
            length_penalty=2.0,
            num_beams=4,
            early_stopping=True
        )

        summary = tokenizer.decode(summary_ids[0], skip_special_tokens=True)
        return summary
    except Exception as e:
        print("Summarize error:", e)
        

        
async def update_summary(article_id, final_summary):
    try:
        print("DBBBBBB")
        article_id = ObjectId(article_id)
        await connect_to_mongo()
        await article_controller.update_article(article_id, {"summary": final_summary})
        await close_mongo_connection()
    except Exception as e:
        print("Update summary error:", e)

def end_summary(self, html_text, article_id=None):
    
    try:
        load_model()
        cleaned = clean_html(html_text)
        chunks = chunk_text(cleaned, max_tokens=400)
        chunk_summaries = [summarize(c) for c in chunks]
        combined_summary_text = " ".join(chunk_summaries)
        final_summary = summarize(combined_summary_text)
        
        print(final_summary)
        # article_id = ObjectId(article_id)
        # asyncio.run(article_controller.update_article(article_id, {"summary": final_summary}))
        
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
    
    
# import asyncio

# def run_async_task(coro):
#     """Run an async coroutine safely inside Celery."""
#     try:
#         loop = asyncio.get_event_loop()
#     except RuntimeError:  # no event loop in this thread
#         loop = asyncio.new_event_loop()
#         asyncio.set_event_loop(loop)

#     if loop.is_closed():  # sometimes the loop exists but is closed
#         loop = asyncio.new_event_loop()
#         asyncio.set_event_loop(loop)

#     return loop.run_until_complete(coro)

# def run_async(coro):
#     """Run an async function safely in a synchronous context."""
#     loop = asyncio.new_event_loop()  # always create a fresh loop
#     asyncio.set_event_loop(loop)
#     try:
#         return loop.run_until_complete(coro)
#     finally:
#         loop.close()
        
        


# @celery_app.on_after_configure.connect
# def init_worker(sender, **kwargs):
#     print("Worker starting, loading model...")
#     load_model()


# @celery_app.task(
#     name="final_summary",
#     bind=True,
#     autoretry_for=(Exception,),
#     retry_backoff=5,
#     retry_kwargs={"max_retries": 3},
# )
# def end_summary(self, html_text, article_id=None):
    
#     # load_model()
#     # Step 1: Clean
#     cleaned = clean_html(html_text)

#     # Step 2: Chunk
#     chunks = chunk_text(cleaned, max_tokens=400)

#     print(f"Total chunks: {len(chunks)}")

#     # Step 3: Summaries of chunks
#     chunk_summaries = []
#     for i, chunk in enumerate(chunks, start=1):
#         print(f"Summarizing chunk {i}/{len(chunks)}...")
#         summary = summarize(chunk)
#         chunk_summaries.append(summary)

#     # Step 4: Combine partial summaries
#     combined_summary_text = " ".join(chunk_summaries)

#     # Step 5: Final summary pass
#     print("Generating final summary...")
#     final_summary = summarize(combined_summary_text)
    
#     # #db connection
#     # asyncio.run(connect_to_mongo())
    
#     # db entry
#     asyncio.run(update_summary(article_id, final_summary))
    
#     # asyncio.run(article_controller.update_article(ObjectId(article_id), {"summary": final_summary}))
    
#     print("db updated")
    
    
#     return {
#         "cleaned_text": cleaned,
#         "chunks": chunks,
#         "chunk_summaries": chunk_summaries,
#         "final_summary": final_summary
#     }



# def summarize(text):
#     """Run a single summary step using the user-provided model."""
#     try:
#         inputs = tokenizer(text, return_tensors="pt", max_length=512, truncation=True)
#         inputs = {k: v.to(device) for k, v in inputs.items()}

#         summary_ids = model.generate(
#             inputs["input_ids"],
#             length_penalty=2.0,
#             num_beams=4,
#             early_stopping=True
#         )

#         return tokenizer.decode(summary_ids[0], skip_special_tokens=True)
#     except Exception as e:
#         return str(e)