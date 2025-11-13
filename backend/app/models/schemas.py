from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime

class UserCreate(BaseModel):
    email: EmailStr
    full_name: str
    dob: str
    phone: str

class VerificationRequest(BaseModel):
    email: EmailStr
    full_name: str
    dob: str
    phone: str

class VerificationResponse(BaseModel):
    verification_id: str
    status: str
    message: str

class VerificationStatus(BaseModel):
    verification_id: str
    status: str
    risk_score: Optional[float]
    risk_level: Optional[str]
    document_status: Optional[str]
    liveness_status: Optional[str]
    compliance_status: Optional[str]
    requires_human_review: bool
    created_at: datetime
    completed_at: Optional[datetime]

class RiskExplanation(BaseModel):
    verification_id: str
    risk_score: float
    risk_level: str
    explanation: str
    document_analysis: dict
    liveness_analysis: dict
    compliance_analysis: dict
    recommendation: str

class LivenessChallenge(BaseModel):
    challenge_text: str
    challenge_language: str
    expected_gesture: str
    expected_phrase: str
