from __future__ import annotations

import json
from pathlib import Path
from typing import Iterable, Optional

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[3]
LABEL_MAP_PATH = PROJECT_ROOT / "ml/configs/label_map.json"

BASE_FEATURE_COLUMNS = [
    "flow_id",
    "src_ip",
    "dst_ip",
    "src_port",
    "dst_port",
    "packet_len_mean",
    "packet_len_max",
    "packet_len_min",
    "packet_len_std",
    "packets_per_sec",
    "bytes_per_sec",
    "flow_duration",
    "label",
]

INFERENCE_BASE_COLUMNS = [
    "src_port",
    "dst_port",
    "packet_len_mean",
    "packet_len_max",
    "packet_len_min",
    "packet_len_std",
    "packets_per_sec",
    "bytes_per_sec",
    "flow_duration",
]

COMMON_DERIVED_FEATURE_COLUMNS = [
    "packet_len_range",
    "bytes_per_packet",
    "port_gap",
    "is_system_src_port",
    "is_system_dst_port",
    "throughput_per_duration",
]

DERIVED_FEATURE_COLUMNS = COMMON_DERIVED_FEATURE_COLUMNS + [
    "label_id",
]

MODEL_INPUT_COLUMNS = INFERENCE_BASE_COLUMNS + COMMON_DERIVED_FEATURE_COLUMNS
FINAL_FEATURE_COLUMNS = BASE_FEATURE_COLUMNS + DERIVED_FEATURE_COLUMNS


def load_label_map(label_map_path: Optional[Path] = None) -> dict[str, int]:
    path = label_map_path or LABEL_MAP_PATH
    return json.loads(path.read_text(encoding="utf-8"))


def load_sample_feature_frames(sample_dir: Path) -> list[pd.DataFrame]:
    csv_files = sorted(sample_dir.glob("sample_features_*.csv"))
    if not csv_files:
        raise FileNotFoundError(f"No sample feature files found in {sample_dir}")

    frames = [pd.read_csv(csv_file) for csv_file in csv_files]
    return frames


def validate_feature_columns(dataframe: pd.DataFrame, required_columns: Iterable[str]) -> None:
    missing = [column for column in required_columns if column not in dataframe.columns]
    if missing:
        raise ValueError(f"Missing required feature columns: {missing}")


def derive_common_features(dataframe: pd.DataFrame) -> pd.DataFrame:
    validate_feature_columns(dataframe, INFERENCE_BASE_COLUMNS)

    processed = dataframe.copy()
    numeric_columns = INFERENCE_BASE_COLUMNS
    processed[numeric_columns] = processed[numeric_columns].apply(pd.to_numeric)

    processed["packet_len_range"] = processed["packet_len_max"] - processed["packet_len_min"]
    processed["bytes_per_packet"] = processed["bytes_per_sec"] / processed["packets_per_sec"].replace(0, pd.NA)
    processed["bytes_per_packet"] = processed["bytes_per_packet"].fillna(0.0)
    processed["port_gap"] = (processed["src_port"] - processed["dst_port"]).abs()
    processed["is_system_src_port"] = (processed["src_port"] < 1024).astype(int)
    processed["is_system_dst_port"] = (processed["dst_port"] < 1024).astype(int)
    processed["throughput_per_duration"] = processed["bytes_per_sec"] / processed["flow_duration"].replace(0, pd.NA)
    processed["throughput_per_duration"] = processed["throughput_per_duration"].fillna(0.0)
    return processed


def build_processed_features(
    dataframe: pd.DataFrame,
    label_map: dict[str, int],
) -> pd.DataFrame:
    validate_feature_columns(dataframe, BASE_FEATURE_COLUMNS)

    processed = derive_common_features(dataframe)
    processed["label"] = processed["label"].astype(str)
    unknown_labels = sorted(set(processed["label"]) - set(label_map))
    if unknown_labels:
        raise ValueError(f"Unknown labels found: {unknown_labels}")

    processed["label_id"] = processed["label"].map(label_map)

    return processed[FINAL_FEATURE_COLUMNS]


def build_processed_dataset_from_samples(
    sample_dir: Path,
    output_path: Path,
    label_map_path: Optional[Path] = None,
) -> pd.DataFrame:
    label_map = load_label_map(label_map_path)
    frames = load_sample_feature_frames(sample_dir)
    combined = pd.concat(frames, ignore_index=True)
    processed = build_processed_features(combined, label_map)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    processed.to_csv(output_path, index=False)
    return processed
