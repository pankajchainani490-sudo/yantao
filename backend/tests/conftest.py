from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from app.core.config import settings
from app.db.database import initialize_database
from app.main import app
from app.services.prediction_service import load_model_artifact

PROJECT_ROOT = Path(__file__).resolve().parents[2]


@pytest.fixture
def api_client(tmp_path: Path):
    db_path = tmp_path / "test_app.sqlite3"
    original_db_path = settings.db_path
    settings.db_path = db_path
    load_model_artifact.cache_clear()
    initialize_database(db_path)

    with TestClient(app) as client:
        yield client

    settings.db_path = original_db_path
    load_model_artifact.cache_clear()
