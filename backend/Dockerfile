FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app/ /app/app/
COPY .env /app/.env

EXPOSE 5500

CMD ["uvicorn", "app.main:app", "--reload", "--host", "0.0.0.0", "--port", "5500"]
