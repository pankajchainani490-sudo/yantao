from typing import Optional

from pydantic import BaseModel, Field


class SiteTargetRequest(BaseModel):
    target: str = Field(min_length=1, max_length=255)
    scheme: str = Field(default="https")
    port: int = Field(default=443, ge=1, le=65535)


class LocalPortTargetRequest(BaseModel):
    port: int = Field(ge=1, le=65535)
    scheme: str = Field(default="http")
    display_name: Optional[str] = Field(default=None, max_length=80)


class TrafficObservationRequest(BaseModel):
    target_id: Optional[int] = None
    source_ip: str = "198.51.100.10"
    source_port: int = Field(default=49152, ge=0, le=65535)
    scenario: str = "manual"
    request_count: int = Field(default=1, ge=1, le=5000)
    packet_len_mean: float = Field(ge=0)
    packet_len_max: float = Field(ge=0)
    packet_len_min: float = Field(ge=0)
    packet_len_std: float = Field(ge=0)
    packets_per_sec: float = Field(ge=0)
    bytes_per_sec: float = Field(ge=0)
    flow_duration: float = Field(gt=0)
    model_name: Optional[str] = None


class SimulationRunRequest(BaseModel):
    scenario: str = Field(default="http_flood")
    count: int = Field(default=5, ge=1, le=50)
    target_id: Optional[int] = None
    source_ip: Optional[str] = None
    target: Optional[str] = None
    scheme: str = Field(default="https")
    port: int = Field(default=443, ge=1, le=65535)
    model_name: Optional[str] = None
