#!/bin/bash

# ================= CONFIG =================
APP_DIR="/home/ubuntu/devops/d-manager"
LOG_FILE="/tmp/deploy.log"

# ================= START =================
set -o pipefail
echo "[INFO] DEPLOY START $(date '+%Y-%m-%d %H:%M:%S')" | tee $LOG_FILE

cd $APP_DIR || {
  echo "[ERROR] App directory not found: $APP_DIR" | tee -a $LOG_FILE
  exit 1
}

# ================= GIT PULL FIRST =================
echo "[STEP] Git pull origin main" | tee -a $LOG_FILE
if ! git pull origin main 2>&1 | tee -a $LOG_FILE; then
  echo "[ERROR] Git pull failed" | tee -a $LOG_FILE
  exit 1
fi


# ================= ENSURE CMD.SH EXISTS =================
echo "[STEP] Checking cmd/cmd.sh..." | tee -a $LOG_FILE

mkdir -p cmd

if [ ! -f "cmd/cmd.sh" ]; then
  echo "[INFO] cmd.sh not found → creating..." | tee -a $LOG_FILE

  cat << 'EOF' > cmd/cmd.sh
#!/bin/bash

PROJECT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
DATA_DIR="$PROJECT_DIR/data"

echo "[CMD] Preparing data directory..."

mkdir -p "$DATA_DIR"

# Nếu không có quyền thì bỏ qua lỗi chmod
chmod -R 777 "$DATA_DIR" 2>/dev/null || true

touch "$DATA_DIR/data.txt"
touch "$DATA_DIR/deploy.txt"

chmod 666 "$DATA_DIR/data.txt" 2>/dev/null || true
chmod 666 "$DATA_DIR/deploy.txt" 2>/dev/null || true

echo "[CMD] Data directory ready"
EOF

  echo "[INFO] cmd.sh created" | tee -a $LOG_FILE
fi

# ================= SET EXEC PERMISSION =================
chmod +x cmd/cmd.sh 2>/dev/null || true
echo "[INFO] cmd.sh is executable" | tee -a $LOG_FILE

# ================= RUN CMD.SH =================
echo "[STEP] Running cmd.sh..." | tee -a $LOG_FILE
if ! bash cmd/cmd.sh 2>&1 | tee -a $LOG_FILE; then
  echo "[ERROR] cmd.sh failed" | tee -a $LOG_FILE
  exit 1
fi


# ================= CHECK requirements.txt =================
if [ ! -f "requirements.txt" ]; then
  echo "[STEP] requirements.txt not found → creating..." | tee -a $LOG_FILE
  touch requirements.txt
  echo "[INFO] requirements.txt created" | tee -a $LOG_FILE
else
  echo "[INFO] requirements.txt already exists" | tee -a $LOG_FILE
fi


# ================= DOCKER BUILD =================
echo "[STEP] Docker build" | tee -a $LOG_FILE
if ! docker compose build 2>&1 | tee -a $LOG_FILE; then
  echo "[ERROR] Build failed" | tee -a $LOG_FILE
  exit 1
fi

# ================= DOCKER UP =================
echo "[STEP] Docker up -d" | tee -a $LOG_FILE
if ! docker compose up -d --remove-orphans 2>&1 | tee -a $LOG_FILE; then
  echo "[ERROR] Run failed" | tee -a $LOG_FILE
  exit 1
fi


# ================= SUCCESS =================
echo "[SUCCESS] DEPLOY DONE $(date '+%Y-%m-%d %H:%M:%S')" | tee -a $LOG_FILE

exit 0