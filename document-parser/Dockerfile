FROM python:3.12-slim

RUN apt-get update && apt-get install -y --no-install-recommends \
    poppler-utils \
    libgl1 \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN mkdir -p /app/uploads /app/data

EXPOSE 8000

ENV UPLOAD_DIR=/app/uploads
ENV DB_PATH=/app/data/docling_studio.db

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
