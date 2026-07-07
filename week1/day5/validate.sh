#!/bin/bash
# validate.sh — Project structure and config validator

# Timestamp for logs
TIMESTAMP=$(date '+%Y-%m-%d %H:%M:%S')
LOG_FILE="./week1/day5/logs/validate.log"

# Create logs directory if it doesn't exist
mkdir -p logs

echo "[$TIMESTAMP] Starting validation..." | tee -a $LOG_FILE

# ─── Check 1: src/ directory exists ───────────────────
if [ -d "./week1/day5/src" ]; then
  echo "[$TIMESTAMP] ✅ src/ directory exists" | tee -a $LOG_FILE
else
  echo "[$TIMESTAMP] ❌ src/ directory missing" | tee -a $LOG_FILE
  exit 1
fi

# ─── Check 2: config.json exists ──────────────────────
if [ -f "./week1/day5/config.json" ]; then
  echo "[$TIMESTAMP] ✅ config.json found" | tee -a $LOG_FILE
else
  echo "[$TIMESTAMP] ❌ config.json missing" | tee -a $LOG_FILE
  exit 1
fi

# ─── Check 3: config.json is valid JSON ───────────────
if python3 -m json.tool ./week1/day5/config.json > /dev/null 2>&1; then
  echo "[$TIMESTAMP] ✅ config.json is valid JSON" | tee -a $LOG_FILE
else
  echo "[$TIMESTAMP] ❌ config.json is invalid JSON" | tee -a $LOG_FILE
  exit 1
fi

echo "[$TIMESTAMP] ✅ All checks passed" | tee -a $LOG_FILE
exit 0
