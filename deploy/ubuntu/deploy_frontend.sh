#!/usr/bin/env bash
set -euo pipefail

PROJECT_ROOT=${PROJECT_ROOT:-/opt/malicious-traffic-ml}

echo "[1/5] Installing frontend dependencies"
cd "$PROJECT_ROOT/frontend"
npm install

echo "[2/5] Building frontend"
npm run build

echo "[3/5] Installing nginx config"
sudo cp "$PROJECT_ROOT/deploy/nginx/malicious-traffic.conf" /etc/nginx/sites-available/malicious-traffic.conf
sudo ln -sf /etc/nginx/sites-available/malicious-traffic.conf /etc/nginx/sites-enabled/malicious-traffic.conf

echo "[4/5] Validating nginx"
sudo nginx -t

echo "[5/5] Restarting nginx"
sudo systemctl restart nginx
sudo systemctl status nginx --no-pager
