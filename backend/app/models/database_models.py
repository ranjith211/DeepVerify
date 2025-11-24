from sqlalchemy import Column, Integer, String, DateTime, Float, Boolean, Text, LargeBinary
from app.database import Base
from datetime import datetime

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    password_hash = Column(String)  # Hashed password
    full_name_encrypted = Column(LargeBinary, nullable=True)  # Encrypted PII
    dob_encrypted = Column(LargeBinary, nullable=True)  # Encrypted PII
    phone_encrypted = Column(LargeBinary, nullable=True)  # Encrypted PII
    kyc_status = Column(String, default="not_started")  # not_started, pending, approved, rejected
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
    requires_human_review = Column(Boolean, default=False)
    explanation = Column(Text)
    admin_status = Column(String, nullable=True)  # approved, rejected, pending_review
    admin_notes = Column(Text, nullable=True)  # Admin's personal notes (short, visible to admin only)
    rejection_reason = Column(Text, nullable=True)  # User-facing rejection suggestions (detailed, visible to user)
    # Detailed analysis JSON stored as text
    document_analysis = Column(Text, nullable=True)  # JSON string with full document analysis
    liveness_analysis = Column(Text, nullable=True)  # JSON string with full liveness analysis
    compliance_analysis = Column(Text, nullable=True)  # JSON string with compliance checks
    liveness_challenge = Column(Text, nullable=True)  # JSON string with the challenge given to user
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)
