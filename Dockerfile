FROM python:3.11-slim

WORKDIR /app

# Copy requirements trước để cache layer
COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

# Copy toàn bộ backend
COPY backend ./backend

# Copy data file nếu chưa có (optional)
RUN touch data.txt

EXPOSE 9000

CMD ["python", "backend/app/main.py"]
