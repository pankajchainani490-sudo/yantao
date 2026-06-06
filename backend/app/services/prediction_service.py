from __future__ import annotations

from functools import lru_cache
from pathlib import Path
from typing import Any, Optional

import joblib
import pandas as pd

from app.core.config import settings
from app.repositories import security_repository
from app.schemas.prediction import PredictionRequest
from app.services.feature_pipeline import MODEL_INPUT_COLUMNS, derive_common_features, load_label_map


RISK_BY_LABEL = {
    "benign": "low",
    "arp_spoof": "high",
    "ddos": "high",
    "trojan": "medium",
}


@lru_cache(maxsize=4)
def load_model_artifact(model_name: str) -> dict[str, Any]:
    artifact_path = settings.models_dir / f"{model_name}.joblib"
    if not artifact_path.is_file():
        raise FileNotFoundError(f"Model artifact not found: {artifact_path}")
    return joblib.load(artifact_path)


def get_supported_models() -> list[str]:
    return ["decision_tree", "random_forest"]


def _prepare_inference_frame(request: PredictionRequest) -> pd.DataFrame:
    raw = pd.DataFrame(
        [
            {
                "src_port": request.source_port,
                "dst_port": request.destination_port,
                "packet_len_mean": request.packet_len_mean,
                "packet_len_max": request.packet_len_max,
                "packet_len_min": request.packet_len_min,
                "packet_len_std": request.packet_len_std,
                "packets_per_sec": request.packets_per_sec,
                "bytes_per_sec": request.bytes_per_sec,
                "flow_duration": request.flow_duration,
            }
        ]
    )
    features = derive_common_features(raw)
    return features[MODEL_INPUT_COLUMNS]


def _top_feature_details(model_name: str, artifact: dict[str, Any], limit: int = 3) -> list[dict[str, float]]:
    model = artifact["model"]
    feature_columns = artifact["feature_columns"]
    ranked = sorted(
        zip(feature_columns, model.feature_importances_),
        key=lambda item: item[1],
        reverse=True,
    )
    return [{"feature": name, "importance": round(float(score), 4)} for name, score in ranked[:limit]]


def run_prediction(request: PredictionRequest, db_path: Optional[Path] = None) -> dict[str, Any]:
    model_name = request.model_name or settings.default_model_name
    if model_name not in get_supported_models():
        raise ValueError(f"Unsupported model name: {model_name}")

    artifact = load_model_artifact(model_name)
    label_map = load_label_map()
    inverse_label_map = {value: key for key, value in label_map.items()}

    feature_frame = _prepare_inference_frame(request)
    model = artifact["model"]
    predicted_label_id = int(model.predict(feature_frame)[0])
    probabilities = model.predict_proba(feature_frame)[0]
    confidence = round(float(max(probabilities)), 4)
    predicted_label = inverse_label_map[predicted_label_id]
    risk_level = RISK_BY_LABEL[predicted_label]

    prediction_id = security_repository.create_prediction_event(
        {
            "source_ip": request.source_ip,
            "destination_ip": request.destination_ip,
            "source_port": request.source_port,
            "destination_port": request.destination_port,
            "predicted_label": predicted_label,
            "predicted_label_id": predicted_label_id,
            "risk_level": risk_level,
            "confidence": confidence,
            "model_name": model_name,
        },
        db_path=db_path,
    )

    alert_created = False
    blacklist_action = "none"
    if predicted_label != "benign":
        alert_created = True
        security_repository.create_alert(
            {
                "prediction_id": prediction_id,
                "source_ip": request.source_ip,
                "source_port": request.source_port,
                "destination_ip": request.destination_ip,
                "destination_port": request.destination_port,
                "attack_type": predicted_label,
                "risk_level": risk_level,
                "confidence": confidence,
            },
            db_path=db_path,
        )

        hit_count = security_repository.count_alert_hits(request.source_ip, predicted_label, db_path=db_path)
        if hit_count >= settings.auto_blacklist_threshold:
            security_repository.upsert_blacklist_entry(
                {
                    "source_ip": request.source_ip,
                    "source_port": request.source_port,
                    "attack_type": predicted_label,
                    "risk_level": risk_level,
                    "hit_count": hit_count,
                    "reason": f"Auto-blacklisted after {hit_count} {predicted_label} alerts.",
                    "created_by": "system",
                },
                db_path=db_path,
            )
            blacklist_action = "upserted"
        else:
            blacklist_action = "candidate"

    return {
        "predicted_label": predicted_label,
        "predicted_label_id": predicted_label_id,
        "confidence": confidence,
        "risk_level": risk_level,
        "model_name": model_name,
        "top_features": _top_feature_details(model_name, artifact),
        "prediction_id": prediction_id,
        "alert_created": alert_created,
        "blacklist_action": blacklist_action,
    }
