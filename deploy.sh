#!/bin/bash

# ===== CONFIG =====
APP_DIR="/home/ubuntu/devops/d-manager"
SERVICE_NAME="d-manager"
PYTHON="/usr/bin/python3"
NOTIFIER="deploy_notifier.py"
LOG_FILE="/tmp/deploy.log"

# ===== START =====
set -o pipefail
echo "[INFO] DEPLOY START $(date '+%Y-%m-%d %H:%M:%S')" | tee $LOG_FILE

cd $APP_DIR || {
  echo "[ERROR] App directory not found" | tee -a $LOG_FILE
  exit 1
}

# ===== GIT PULL =====
echo "[STEP] Git pull origin main" | tee -a $LOG_FILE
if ! git pull origin main 2>&1 | tee -a $LOG_FILE; then
  echo "[ERROR] Git pull failed" | tee -a $LOG_FILE
  $PYTHON $NOTIFIER FAIL "git pull failed"
  exit 1
fi

# ===== BUILD =====
echo "[STEP] Docker build" | tee -a $LOG_FILE
if ! docker compose build 2>&1 | tee -a $LOG_FILE; then
  echo "[ERROR] Build failed" | tee -a $LOG_FILE
  $PYTHON $NOTIFIER FAIL "docker build failed"
  exit 1
fi

# ===== RUN =====
echo "[STEP] Docker up -d" | tee -a $LOG_FILE
if ! docker compose up -d 2>&1 | tee -a $LOG_FILE; then
  echo "[ERROR] Run failed" | tee -a $LOG_FILE
  $PYTHON $NOTIFIER FAIL "docker up failed"
  exit 1
fi

# ===== SUCCESS =====
echo "[SUCCESS] DEPLOY DONE" | tee -a $LOG_FILE
$PYTHON $NOTIFIER SUCCESS "deploy success"

exit 0
