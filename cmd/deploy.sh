#!/bin/bash

# ================= CONFIG =================
APP_DIR="/home/ubuntu/devops/d-manager"
LOG_FILE="/tmp/deploy.log"
PYTHON_BIN="python3"
TEST_FILE="backend/app/test/test.py"

# ================= START =================
set -e
set -o pipefail

echo "========================================" | tee $LOG_FILE
echo "[INFO] DEPLOY START $(date '+%Y-%m-%d %H:%M:%S')" | tee -a $LOG_FILE
echo "========================================" | tee -a $LOG_FILE

cd "$APP_DIR" || {
  echo "[ERROR] App directory not found: $APP_DIR" | tee -a $LOG_FILE
  exit 1
}

echo "[DEBUG] Current directory: $(pwd)" | tee -a $LOG_FILE

# ================= CHECK PYTHON =================
if ! command -v $PYTHON_BIN &> /dev/null; then
  echo "[ERROR] $PYTHON_BIN not found" | tee -a $LOG_FILE
  exit 1
fi

# ================= GIT PULL =================
echo "[STEP] Git pull origin main" | tee -a $LOG_FILE
if ! git pull origin main 2>&1 | tee -a $LOG_FILE; then
  echo "[ERROR] Git pull failed" | tee -a $LOG_FILE
  exit 1
fi

# ================= ENSURE CMD.SH =================
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
chmod -R 777 "$DATA_DIR" 2>/dev/null || true

touch "$DATA_DIR/data.txt"
touch "$DATA_DIR/deploy.txt"

chmod 666 "$DATA_DIR/data.txt" 2>/dev/null || true
chmod 666 "$DATA_DIR/deploy.txt" 2>/dev/null || true

echo "[CMD] Data directory ready"
EOF

  echo "[INFO] cmd.sh created" | tee -a $LOG_FILE
fi

chmod +x cmd/cmd.sh 2>/dev/null || true
echo "[INFO] cmd.sh is executable" | tee -a $LOG_FILE

echo "[STEP] Running cmd.sh..." | tee -a $LOG_FILE
if ! bash cmd/cmd.sh 2>&1 | tee -a $LOG_FILE; then
  echo "[ERROR] cmd.sh failed" | tee -a $LOG_FILE
  exit 1
fi

# ================= RUN TEST =================
echo "[STEP] Running $TEST_FILE ..." | tee -a $LOG_FILE

if [ -f "$TEST_FILE" ]; then
  if ! $PYTHON_BIN "$TEST_FILE" 2>&1 | tee -a $LOG_FILE; then
    echo "[ERROR] Test failed → stop deploy" | tee -a $LOG_FILE
    exit 1
  fi
  echo "[INFO] Test passed" | tee -a $LOG_FILE
else
  echo "[WARNING] $TEST_FILE not found → skip test" | tee -a $LOG_FILE
fi

# ================= DOCKER BUILD =================
echo "[STEP] Docker build" | tee -a $LOG_FILE
if ! docker compose build 2>&1 | tee -a $LOG_FILE; then
  echo "[ERROR] Docker build failed" | tee -a $LOG_FILE
  exit 1
fi

# ================= DOCKER UP =================
echo "[STEP] Docker up -d" | tee -a $LOG_FILE
if ! docker compose up -d --remove-orphans 2>&1 | tee -a $LOG_FILE; then
  echo "[ERROR] Docker run failed" | tee -a $LOG_FILE
  exit 1
fi

# ================= HEALTH CHECK =================
echo "[STEP] Waiting for containers..." | tee -a $LOG_FILE
sleep 5

if ! docker compose ps 2>&1 | tee -a $LOG_FILE; then
  echo "[ERROR] Containers not running properly" | tee -a $LOG_FILE
  exit 1
fi

# ================= SUCCESS =================
echo "========================================" | tee -a $LOG_FILE
echo "[SUCCESS] DEPLOY DONE $(date '+%Y-%m-%d %H:%M:%S')" | tee -a $LOG_FILE
echo "========================================" | tee -a $LOG_FILE

exit 0
