FROM python:3.12
# Install poppler for PDF processing
RUN apt-get update && apt-get install -y poppler-utils && rm -rf /var/lib/apt/lists/*
WORKDIR /app
COPY backend/requirements.txt ./backend/requirements.txt
RUN pip install --no-cache-dir -r backend/requirements.txt
COPY . .
RUN chmod +x run_app.sh
ENTRYPOINT ["./run_app.sh"]
