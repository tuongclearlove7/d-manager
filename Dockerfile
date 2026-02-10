FROM python:3.11-slim

ENV PYTHONUNBUFFERED=1

WORKDIR /app
COPY socket_server.py .

EXPOSE 9000
CMD ["python", "socket_server.py"]
