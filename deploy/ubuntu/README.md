# Ubuntu Deployment

This directory contains the first deployable Ubuntu templates for the project.

## Files

- `backend.env.example`: backend environment example
- `deploy_backend.sh`: backend install, training, test, and service startup script
- `deploy_frontend.sh`: frontend build and nginx deployment script

## Recommended host

- Ubuntu 22.04 LTS
- 4 CPU cores or more
- 8 GB RAM or more
- 40 GB disk or more

## Suggested directory

```text
/opt/malicious-traffic-ml
```

## Current deployment mode

- backend served by `uvicorn` under `systemd`
- frontend static assets served by `nginx`
- database stored in local `SQLite`
- replay-based demonstration preferred for classroom/demo stability
