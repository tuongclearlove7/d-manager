FROM python:3.11-slim

WORKDIR /app

COPY socket_server.py .

EXPOSE 9000

CMD ["python", "socket_server.py"]
