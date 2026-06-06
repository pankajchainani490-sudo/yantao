# Backend

FastAPI backend for the malicious traffic detection system.

## Responsibilities

- Provide health, prediction, dashboard, replay, and blacklist APIs.
- Load trained decision tree and random forest models.
- Persist alerts and blacklist records in SQLite during the first phase.
- Expose metrics and settings data for the frontend dashboard.

## Local development

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
python ..\scripts\train\build_processed_dataset.py
python ..\scripts\train\train_models.py
uvicorn app.main:app --reload
```

## Test

```bash
.venv\Scripts\python -m pytest -v
```

## Main API groups

- `/api/v1/health`
- `/api/v1/predict`
- `/api/v1/dashboard/*`
- `/api/v1/alerts`
- `/api/v1/blacklist`
- `/api/v1/replay/*`
- `/api/v1/metrics/summary`
- `/api/v1/settings`
