FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app:/app/wscraping

WORKDIR /app

# Gerekirse ek paketleri buraya ekle
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential curl libffi-dev && \
    rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000
CMD ["uvicorn", "wscraping.main:app", "--host", "0.0.0.0", "--port", "8000"]
