from typing import Optional

from pydantic import BaseModel, Field


class FeatureImportanceItem(BaseModel):
    feature: str
    importance: float


class PredictionRequest(BaseModel):
    source_ip: str
    destination_ip: str
    source_port: int = Field(ge=0)
    destination_port: int = Field(ge=0)
    packet_len_mean: float = Field(ge=0)
    packet_len_max: float = Field(ge=0)
    packet_len_min: float = Field(ge=0)
    packet_len_std: float = Field(ge=0)
    packets_per_sec: float = Field(ge=0)
    bytes_per_sec: float = Field(ge=0)
    flow_duration: float = Field(gt=0)
    model_name: Optional[str] = None


class PredictionResponse(BaseModel):
    predicted_label: str
    predicted_label_id: int
    confidence: float
    risk_level: str
    model_name: str
    top_features: list[FeatureImportanceItem]
    prediction_id: int
    alert_created: bool
    blacklist_action: str
