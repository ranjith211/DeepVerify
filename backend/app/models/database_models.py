from sqlalchemy import Column, Integer, String, DateTime, Float, Boolean, Text, LargeBinary
from app.database import Base
from datetime import datetime

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    full_name_encrypted = Column(LargeBinary)  # Encrypted PII
    dob_encrypted = Column(LargeBinary)  # Encrypted PII
    phone_encrypted = Column(LargeBinary)  # Encrypted PII
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class VerificationLog(Base):
    __tablename__ = "verification_logs"

    id = Column(Integer, primary_key=True, index=True)
    verification_id = Column(String, unique=True, index=True)
    user_id = Column(Integer, index=True)
    status = Column(String)  # pending, approved, rejected, review_required
    risk_score = Column(Float)
    risk_level = Column(String)  # low, medium, high
    document_status = Column(String)
    liveness_status = Column(String)
    compliance_status = Column(String)
    face_count = Column(Integer, nullable=True)  # Number of faces in liveness video (must be 1)
    requires_human_review = Column(Boolean, default=False)
    explanation = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)
