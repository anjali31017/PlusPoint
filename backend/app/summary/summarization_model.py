import re
from transformers import BartTokenizer, BartForConditionalGeneration
import torch
from bs4 import BeautifulSoup
import os 

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

# BASE_DIR = os.path.dirname(os.path.abspath(__file__))
# model_path = os.path.join(BASE_DIR, "bart_lora")

tokenizer = BartTokenizer.from_pretrained('../bart_lora')
model = BartForConditionalGeneration.from_pretrained('../bart_lora').to(device)
# Load the fine-tuned model
# tokenizer = BartTokenizer.from_pretrained('./bart_lora')
# model = BartForConditionalGeneration.from_pretrained('./bart_lora').to(device)

def clean_html(html_text):
    try:
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
        str(e)
        return [text]

def summarize(text):
    try:
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
        str(e)
        


def multi_stage_summary(html_text):
    # Step 1: Clean
    cleaned = clean_html(html_text)

    # Step 2: Chunk
    chunks = chunk_text(cleaned, max_tokens=400)

    print(f"Total chunks: {len(chunks)}")

    # Step 3: Summaries of chunks
    chunk_summaries = []
    for i, chunk in enumerate(chunks, start=1):
        print(f"Summarizing chunk {i}/{len(chunks)}...")
        summary = summarize(chunk)
        chunk_summaries.append(summary)

    # Step 4: Combine partial summaries
    combined_summary_text = " ".join(chunk_summaries)

    # Step 5: Final summary pass
    print("Generating final summary...")
    final_summary = summarize(combined_summary_text)

    return {
        "cleaned_text": cleaned,
        "chunks": chunks,
        "chunk_summaries": chunk_summaries,
        "final_summary": final_summary
    }



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