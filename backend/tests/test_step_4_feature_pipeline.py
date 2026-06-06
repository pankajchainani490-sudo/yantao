import json
from pathlib import Path

import pandas as pd

from app.services.feature_pipeline import (
    FINAL_FEATURE_COLUMNS,
    build_processed_dataset_from_samples,
    load_label_map,
)


PROJECT_ROOT = Path(__file__).resolve().parents[2]


def test_step_4_feature_schema_exists_and_matches_pipeline() -> None:
    schema_path = PROJECT_ROOT / "ml/configs/feature_schema.json"
    assert schema_path.is_file(), "feature_schema.json is missing"

    schema = json.loads(schema_path.read_text(encoding="utf-8"))
    final_columns = schema["base_columns"] + schema["derived_columns"]
    assert final_columns == FINAL_FEATURE_COLUMNS


def test_step_4_processed_dataset_can_be_built_from_sample_inputs(tmp_path: Path) -> None:
    sample_dir = PROJECT_ROOT / "ml/data/sample"
    output_path = tmp_path / "training_features.csv"

    processed = build_processed_dataset_from_samples(sample_dir=sample_dir, output_path=output_path)

    assert output_path.is_file()
    assert not processed.empty
    assert list(processed.columns) == FINAL_FEATURE_COLUMNS
    assert set(processed["label"]) == {"benign", "arp_spoof", "ddos", "trojan"}
    assert set(processed["label_id"]) == {0, 1, 2, 3}
    assert processed["packet_len_range"].ge(0).all()
    assert processed["bytes_per_packet"].ge(0).all()
    assert processed["throughput_per_duration"].ge(0).all()


def test_step_4_repository_processed_dataset_exists_and_is_consistent() -> None:
    processed_path = PROJECT_ROOT / "ml/data/processed/training_features.csv"
    assert processed_path.is_file(), "Processed training feature dataset is missing"

    dataframe = pd.read_csv(processed_path)
    assert not dataframe.empty
    assert list(dataframe.columns) == FINAL_FEATURE_COLUMNS

    label_map = load_label_map()
    expected_ids = dataframe["label"].map(label_map)
    assert dataframe["label_id"].tolist() == expected_ids.tolist()
