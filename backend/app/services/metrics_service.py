from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any

from app.core.config import settings


def _read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _read_feature_importance(path: Path) -> list[dict[str, Any]]:
    with path.open("r", encoding="utf-8", newline="") as file:
        reader = csv.DictReader(file)
        return [
            {
                "feature": row["feature"],
                "importance": round(float(row["importance"]), 4),
            }
            for row in reader
        ]


def get_metrics_summary() -> dict[str, Any]:
    reports_dir = settings.reports_dir
    metrics = _read_json(reports_dir / "model_metrics.json")

    return {
        "dataset": metrics["dataset"],
        "models": metrics["models"],
        "feature_importance": {
            "decision_tree": _read_feature_importance(reports_dir / "decision_tree_feature_importance.csv"),
            "random_forest": _read_feature_importance(reports_dir / "random_forest_feature_importance.csv"),
        },
        "confusion_matrices": {
            "decision_tree": _read_json(reports_dir / "decision_tree_confusion_matrix.json"),
            "random_forest": _read_json(reports_dir / "random_forest_confusion_matrix.json"),
        },
    }
