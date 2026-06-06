from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import joblib
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, confusion_matrix, f1_score, precision_score, recall_score
from sklearn.model_selection import train_test_split
from sklearn.tree import DecisionTreeClassifier

from app.services.feature_pipeline import FINAL_FEATURE_COLUMNS, MODEL_INPUT_COLUMNS, load_label_map


PROJECT_ROOT = Path(__file__).resolve().parents[3]
DEFAULT_DATASET_PATH = PROJECT_ROOT / "ml/data/processed/training_features.csv"
DEFAULT_MODELS_DIR = PROJECT_ROOT / "ml/models"
DEFAULT_REPORTS_DIR = PROJECT_ROOT / "ml/reports"

METADATA_COLUMNS = ["flow_id", "src_ip", "dst_ip", "label", "label_id"]
MODEL_FEATURE_COLUMNS = MODEL_INPUT_COLUMNS


def load_training_dataset(dataset_path: Path = DEFAULT_DATASET_PATH) -> pd.DataFrame:
    return pd.read_csv(dataset_path)


def _build_models() -> dict[str, Any]:
    return {
        "decision_tree": DecisionTreeClassifier(max_depth=6, min_samples_split=2, random_state=42),
        "random_forest": RandomForestClassifier(
            n_estimators=250,
            max_depth=8,
            min_samples_split=2,
            random_state=42,
        ),
    }


def _evaluate_model(model: Any, x_test: pd.DataFrame, y_test: pd.Series, label_order: list[int]) -> dict[str, Any]:
    predictions = model.predict(x_test)
    return {
        "accuracy": round(float(accuracy_score(y_test, predictions)), 4),
        "precision_macro": round(float(precision_score(y_test, predictions, average="macro", zero_division=0)), 4),
        "recall_macro": round(float(recall_score(y_test, predictions, average="macro", zero_division=0)), 4),
        "f1_macro": round(float(f1_score(y_test, predictions, average="macro", zero_division=0)), 4),
        "confusion_matrix": confusion_matrix(y_test, predictions, labels=label_order).tolist(),
    }


def train_and_evaluate_models(
    dataset_path: Path = DEFAULT_DATASET_PATH,
    models_dir: Path = DEFAULT_MODELS_DIR,
    reports_dir: Path = DEFAULT_REPORTS_DIR,
) -> dict[str, Any]:
    dataframe = load_training_dataset(dataset_path)
    label_map = load_label_map()
    label_order = [label_map[name] for name in label_map]

    x = dataframe[MODEL_FEATURE_COLUMNS]
    y = dataframe["label_id"]

    x_train, x_test, y_train, y_test = train_test_split(
        x,
        y,
        test_size=0.25,
        random_state=42,
        stratify=y,
    )

    models_dir.mkdir(parents=True, exist_ok=True)
    reports_dir.mkdir(parents=True, exist_ok=True)

    metrics: dict[str, Any] = {
        "dataset": {
            "rows": int(len(dataframe)),
            "feature_columns": MODEL_FEATURE_COLUMNS,
            "train_rows": int(len(x_train)),
            "test_rows": int(len(x_test)),
        },
        "models": {},
    }

    for model_name, model in _build_models().items():
        model.fit(x_train, y_train)
        model_metrics = _evaluate_model(model, x_test, y_test, label_order)
        model_artifact = {
            "model": model,
            "feature_columns": MODEL_FEATURE_COLUMNS,
            "label_map": label_map,
        }

        joblib.dump(model_artifact, models_dir / f"{model_name}.joblib")

        feature_importance = pd.DataFrame(
            {
                "feature": MODEL_FEATURE_COLUMNS,
                "importance": model.feature_importances_,
            }
        ).sort_values(by="importance", ascending=False)
        feature_importance.to_csv(reports_dir / f"{model_name}_feature_importance.csv", index=False)

        with (reports_dir / f"{model_name}_confusion_matrix.json").open("w", encoding="utf-8") as file:
            json.dump(
                {
                    "labels": list(label_map.keys()),
                    "label_ids": label_order,
                    "matrix": model_metrics["confusion_matrix"],
                },
                file,
                indent=2,
            )

        metrics["models"][model_name] = model_metrics

    metrics_path = reports_dir / "model_metrics.json"
    metrics_path.write_text(json.dumps(metrics, indent=2), encoding="utf-8")
    return metrics
