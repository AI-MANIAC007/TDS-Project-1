# Dockerfile
FROM python:3.10-slim

WORKDIR /app

COPY main.py .

RUN apt-get update && apt-get install -y sqlite3 && \
    pip install fastapi uvicorn requests

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
