from pydantic import BaseModel, Field, EmailStr
from datetime import datetime
from typing import Optional
from fastapi import UploadFile
from enum import Enum

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
    claim_id: str

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
    user_id: str = Field(..., alias="userId")
    bpm: int
    timestamp: datetime
    summary: Optional[str] = None

class UserSignup(BaseModel):
    email: EmailStr
    password: str
    name: Optional[str] = None

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserOut(BaseModel):
    user_id: str
    email: EmailStr
    name: Optional[str] = None

class FullClaimStatus(str, Enum):
    waiting = "waiting"
    approved = "approved"

class FullClaimDB(BaseModel):
    user_id: str
    discharge_hash: str
    bill_hash: str
    status: FullClaimStatus
    created_at: datetime = Field(default_factory=datetime.utcnow) 