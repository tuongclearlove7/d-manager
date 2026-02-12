FROM python:3.11-slim

ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Cài git + docker CLI + curl (nếu cần healthcheck)
RUN apt-get update && \
    apt-get install -y git docker.io curl && \
    rm -rf /var/lib/apt/lists/*

# Fix git dubious ownership
RUN git config --global --add safe.directory /app

# Copy requirements trước để tận dụng cache
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy source
COPY . .

EXPOSE 9000

CMD ["python", "backend/app/main.py"]
