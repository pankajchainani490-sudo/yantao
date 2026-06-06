# Deployment

This document describes the current deployment direction and local-to-Ubuntu transition notes.

## Current state

- Windows local development is available now
- Backend runs with FastAPI and SQLite
- Frontend builds to static assets with Vite
- Ubuntu deployment templates are now included in `deploy/`

## Target Ubuntu structure

- Backend: `uvicorn` under `systemd`
- Frontend: static files served by `nginx`
- Database: local `SQLite` in phase 1

## Recommended deployment flow

1. Build or retrain models on the development machine
2. Copy repository to Ubuntu host
3. Create Python virtual environment in `backend/`
4. Install backend dependencies
5. Generate processed dataset and model artifacts if needed
6. Build frontend with `npm run build`
7. Serve frontend `dist/` through nginx
8. Reverse proxy `/api` to FastAPI

## Included deployment templates

- `deploy/nginx/malicious-traffic.conf`
- `deploy/systemd/malicious-traffic-backend.service`
- `deploy/docker/docker-compose.yml`
- `deploy/ubuntu/backend.env.example`
- `deploy/ubuntu/deploy_backend.sh`
- `deploy/ubuntu/deploy_frontend.sh`

## Example Ubuntu setup commands

```bash
sudo apt update
sudo apt install -y python3 python3-venv python3-pip nodejs npm nginx
sudo mkdir -p /opt/malicious-traffic-ml
sudo chown -R $USER:$USER /opt/malicious-traffic-ml
```

Then copy the project into `/opt/malicious-traffic-ml` and run:

```bash
cd /opt/malicious-traffic-ml
bash deploy/ubuntu/deploy_backend.sh
bash deploy/ubuntu/deploy_frontend.sh
```

## Service verification

```bash
systemctl status malicious-traffic-backend.service
curl http://127.0.0.1:8000/api/v1/health
nginx -t
```

## Important note

For defense/demo environments, replay mode is more reliable than live packet capture because:

- cloud hosts may not expose local ARP traffic
- live capture often requires root/capability changes
- replay produces stable and repeatable demonstrations

## Phase-1 deployment conclusion

The current project is deployment-ready for:

- frontend static page hosting
- backend prediction and dashboard APIs
- local SQLite state persistence
- repeatable replay-based classroom or defense demonstration
