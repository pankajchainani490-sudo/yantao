import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[2]
BACKEND_DIR = PROJECT_ROOT / "backend"
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from app.services.feature_pipeline import build_processed_dataset_from_samples


def main() -> None:
    sample_dir = PROJECT_ROOT / "ml/data/sample"
    output_path = PROJECT_ROOT / "ml/data/processed/training_features.csv"

    processed = build_processed_dataset_from_samples(sample_dir=sample_dir, output_path=output_path)
    print(f"Processed dataset written to: {output_path}")
    print(f"Rows: {len(processed)}")
    print(f"Columns: {len(processed.columns)}")


if __name__ == "__main__":
    main()
