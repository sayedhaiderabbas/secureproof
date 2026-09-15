import json
from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator


class AnalysisResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    incident_category: str
    risk_level: Literal["LOW", "MEDIUM", "HIGH", "CRITICAL"]
    confidence: int = Field(ge=0, le=100)
    summary: str
    indicators: list[str]
    recommendations: list[str]

    @field_validator("indicators", "recommendations", mode="before")
    @classmethod
    def decode_json_list(cls, value: object) -> object:
        if isinstance(value, str):
            return json.loads(value)
        return value


class EvidenceResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str
    original_filename: str
    evidence_type: str
    file_size: int
    sha256_hash: str
    storage_reference: str
    created_at: datetime
    status: str
    analysis: AnalysisResponse | None = None


class VerificationResponse(BaseModel):
    result: Literal["VERIFIED", "INTEGRITY MISMATCH"]
    message: str
    original_hash: str
    current_hash: str
    verified_at: datetime


class ProofResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    evidence_hash: str
    network: str
    contract_address: str
    transaction_hash: str
    block_number: int
    timestamp: datetime
    status: str


class DashboardResponse(BaseModel):
    total_evidence: int
    verified_evidence: int
    integrity_mismatches: int
    high_critical_risk: int
    recent_evidence: list[EvidenceResponse]


class EventResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    event_type: str
    description: str
    transaction_reference: str | None
    timestamp: datetime
