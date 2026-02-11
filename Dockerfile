FROM python:3.11-slim

ENV PYTHONUNBUFFERED=1

WORKDIR /app

# 👇 CÀI GIT
RUN apt-get update && apt-get install -y git \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 9000

CMD ["python", "backend/app/main.py"]
