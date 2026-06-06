from pydantic import BaseModel, Field


class BlacklistCreateRequest(BaseModel):
    source_ip: str
    source_port: int = Field(ge=0)
    attack_type: str
    risk_level: str = "medium"
    reason: str
    created_by: str = "manual"


class ReplayStartRequest(BaseModel):
    stage_order: int = Field(default=1, ge=1)
