import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[2]
BACKEND_DIR = PROJECT_ROOT / "backend"
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from app.services.model_training import train_and_evaluate_models


def main() -> None:
    dataset_path = PROJECT_ROOT / "ml/data/processed/training_features.csv"
    models_dir = PROJECT_ROOT / "ml/models"
    reports_dir = PROJECT_ROOT / "ml/reports"

    metrics = train_and_evaluate_models(
        dataset_path=dataset_path,
        models_dir=models_dir,
        reports_dir=reports_dir,
    )

    print(f"Training rows: {metrics['dataset']['rows']}")
    for model_name, result in metrics["models"].items():
        print(
            f"{model_name}: accuracy={result['accuracy']}, "
            f"recall_macro={result['recall_macro']}, f1_macro={result['f1_macro']}"
        )


if __name__ == "__main__":
    main()
