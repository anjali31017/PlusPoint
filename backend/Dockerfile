# Use Python slim image
FROM python:3.11-slim

# Set working directory inside container
WORKDIR /code

# Install system dependencies (needed for psycopg2 / SQLAlchemy + Postgres)
RUN apt-get update && apt-get install -y gcc libpq-dev

# Copy dependency list and install
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy app source code
COPY ./app /code/app
COPY ./config.py /code/app/config.py  # but in your structure config.py is already inside app, so this line can be skipped

# Run FastAPI app with Uvicorn
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
