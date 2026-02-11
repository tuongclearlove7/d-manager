#!/bin/bash

PROJECT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
DATA_DIR="$PROJECT_DIR/data"

echo "[CMD] Setting permission for data directory..."

# Tạo thư mục nếu chưa tồn tại
mkdir -p "$DATA_DIR"

# Set quyền
chmod -R 777 "$DATA_DIR"

echo "[CMD] Permission set for $DATA_DIR"
