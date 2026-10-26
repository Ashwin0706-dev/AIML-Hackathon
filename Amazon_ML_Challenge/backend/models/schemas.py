from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class DatasetSummary(BaseModel):
    name: str
    rows: int
    columns: List[str]
    missing: Dict[str, int]
    duplicate_entity_ids: int = 0
    sample_rows: List[Dict[str, Any]] = Field(default_factory=list)
    unique_country_counts: Dict[str, int] = Field(default_factory=dict)


class MatchRequest(BaseModel):
    source1_entity_id: str
    source2_entity_id: Optional[str] = None
    source3_entity_id: Optional[str] = None
    business_name: Optional[str] = None
    business_address: Optional[str] = None
    country: Optional[str] = None


class MatchRecord(BaseModel):
    source1_entity_id: str
    source2_entity_id: Optional[str] = None
    source3_entity_id: Optional[str] = None
    score: float = 0.0
    decision: str = 'No match'


class ValidationResult(BaseModel):
    valid: bool
    checks: Dict[str, Any]
