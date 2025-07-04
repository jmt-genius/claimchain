from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional
from fastapi import UploadFile

class QuickClaimRequest(BaseModel):
    sum_insured: float
    event_start: str
    event_end: str
    hospital_cost: float

    class Config:
        from_attributes = True

class QuickClaimResponse(BaseModel):
    claimable_amount: float
    quick_claim_amount: float
    reason: str
    timestamp: datetime = datetime.now()

class MedicalReportValidationResponse(BaseModel):
    is_valid_report: bool
    reason: str
    timestamp: datetime = datetime.now()

class FullClaimEvaluationResponse(BaseModel):
    claimable_amount: float
    reasoning: str
    timestamp: datetime = datetime.now()

class ClaimRequest(BaseModel):
    sum_insured: float
    event_start: str
    event_end: str
    hospital_cost: float

class ClaimResponse(BaseModel):
    claimable_amount: float
    quick_claim_amount: float
    reason: str

class CardiacEvent(BaseModel):
    customer_id: str = Field(..., alias="customerId")
    bpm: int
    timestamp: datetime
    summary: Optional[str] = None 