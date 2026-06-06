#!/usr/bin/env bash
set -euo pipefail

PROJECT_ROOT=${PROJECT_ROOT:-/opt/malicious-traffic-ml}

echo "[1/7] Creating backend virtual environment"
python3 -m venv "$PROJECT_ROOT/backend/.venv"

echo "[2/7] Installing backend dependencies"
"$PROJECT_ROOT/backend/.venv/bin/pip" install -r "$PROJECT_ROOT/backend/requirements.txt"

echo "[3/7] Building processed dataset"
"$PROJECT_ROOT/backend/.venv/bin/python" "$PROJECT_ROOT/scripts/train/build_processed_dataset.py"

echo "[4/7] Training models"
"$PROJECT_ROOT/backend/.venv/bin/python" "$PROJECT_ROOT/scripts/train/train_models.py"

echo "[5/7] Running backend tests"
cd "$PROJECT_ROOT/backend"
"$PROJECT_ROOT/backend/.venv/bin/python" -m pytest -v

echo "[6/7] Installing systemd service"
sudo cp "$PROJECT_ROOT/deploy/systemd/malicious-traffic-backend.service" /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable malicious-traffic-backend.service

echo "[7/7] Starting backend service"
sudo systemctl restart malicious-traffic-backend.service
sudo systemctl status malicious-traffic-backend.service --no-pager
