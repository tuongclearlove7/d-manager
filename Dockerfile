FROM python:3.11-slim

ENV PYTHONUNBUFFERED=1

WORKDIR /app

# cài lib cần thiết
RUN pip install --no-cache-dir websockets

# copy source
COPY socket_server.py .

EXPOSE 9000

CMD ["python", "socket_server.py"]
