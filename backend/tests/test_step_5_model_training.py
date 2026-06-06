import json
from pathlib import Path

from app.services.model_training import MODEL_FEATURE_COLUMNS, train_and_evaluate_models


PROJECT_ROOT = Path(__file__).resolve().parents[2]
MIN_ACCURACY = 0.70
MIN_F1_MACRO = 0.65
EXPECTED_MODELS = {"decision_tree", "random_forest"}


def test_step_5_training_pipeline_produces_models_and_reports(tmp_path: Path) -> None:
    dataset_path = PROJECT_ROOT / "ml/data/processed/training_features.csv"
    models_dir = tmp_path / "models"
    reports_dir = tmp_path / "reports"

    metrics = train_and_evaluate_models(
        dataset_path=dataset_path,
        models_dir=models_dir,
        reports_dir=reports_dir,
    )

    assert set(metrics["models"]) == EXPECTED_MODELS
    assert metrics["dataset"]["rows"] >= 16
    assert metrics["dataset"]["feature_columns"] == MODEL_FEATURE_COLUMNS

    for model_name, result in metrics["models"].items():
        assert result["accuracy"] >= MIN_ACCURACY
        assert result["f1_macro"] >= MIN_F1_MACRO
        assert (models_dir / f"{model_name}.joblib").is_file()
        assert (reports_dir / f"{model_name}_feature_importance.csv").is_file()
        assert (reports_dir / f"{model_name}_confusion_matrix.json").is_file()

    assert (reports_dir / "model_metrics.json").is_file()


def test_step_5_repository_training_artifacts_exist_and_meet_thresholds() -> None:
    metrics_path = PROJECT_ROOT / "ml/reports/model_metrics.json"
    assert metrics_path.is_file(), "Training metrics report is missing"

    metrics = json.loads(metrics_path.read_text(encoding="utf-8"))
    assert set(metrics["models"]) == EXPECTED_MODELS

    for model_name, result in metrics["models"].items():
        assert result["accuracy"] >= MIN_ACCURACY
        assert result["f1_macro"] >= MIN_F1_MACRO
        assert (PROJECT_ROOT / "ml/models" / f"{model_name}.joblib").is_file()
        assert (PROJECT_ROOT / "ml/reports" / f"{model_name}_feature_importance.csv").is_file()
        assert (PROJECT_ROOT / "ml/reports" / f"{model_name}_confusion_matrix.json").is_file()
