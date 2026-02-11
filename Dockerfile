FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY socket_server.py .
COPY deploy_notifier.py .

CMD ["python", "socket_server.py"]
