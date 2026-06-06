# Architecture

## Layered architecture

### 1. Data layer

- `ml/data/raw`: original public datasets and isolated lab captures
- `ml/data/interim`: parsed flow or window-level intermediate data
- `ml/data/processed`: model-ready feature tables
- `ml/data/sample`: lightweight demo assets used in repository-tracked tests

### 2. ML layer

- feature derivation in `backend/app/services/feature_pipeline.py`
- model training in `backend/app/services/model_training.py`
- model artifacts in `ml/models/`
- evaluation reports in `ml/reports/`

### 3. Service layer

- FastAPI routes under `backend/app/api/routes/`
- SQLite persistence via `backend/app/db/database.py`
- repository functions in `backend/app/repositories/security_repository.py`
- prediction service in `backend/app/services/prediction_service.py`

### 4. Presentation layer

- React pages in `frontend/src/pages/`
- API integration in `frontend/src/api/security.ts`
- dashboard, detection, replay, blacklist, metrics, and settings views

## Main runtime flow

1. Load sample/public data
2. Build processed feature table
3. Train decision tree and random forest
4. Save models and metrics reports
5. Serve predictions and demo state over FastAPI
6. Render visualization and interaction in React
