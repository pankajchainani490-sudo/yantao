# Test Plan

This project uses `pytest` as the milestone verification mechanism.

## Current automated coverage

- `test_step_2_scaffold.py`: directory and file scaffold verification
- `test_step_3_dataset_layout.py`: label map, manifests, and sample dataset verification
- `test_step_4_feature_pipeline.py`: processed feature pipeline verification
- `test_step_5_model_training.py`: model training and artifact verification
- `test_step_6_api_predict.py`: prediction, dashboard, replay, metrics, settings, and blacklist API verification
- `test_health_api.py`: basic service availability verification

## How to run

```bash
cd backend
.venv\Scripts\python -m pytest -v
```

## Expected current result

- All backend tests should pass
- Frontend should compile successfully with `npm run build`
