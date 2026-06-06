from pathlib import Path


class Settings:
    project_name = "Malicious Traffic ML Detection System"
    version = "0.1.0"
    api_prefix = "/api/v1"
    base_dir = Path(__file__).resolve().parents[3]
    data_dir = base_dir / "backend" / "data"
    db_path = data_dir / "app.sqlite3"
    models_dir = base_dir / "ml" / "models"
    reports_dir = base_dir / "ml" / "reports"
    replay_manifest_path = base_dir / "ml" / "data" / "sample" / "replay_manifest.json"
    default_model_name = "random_forest"
    auto_blacklist_threshold = 2


settings = Settings()
