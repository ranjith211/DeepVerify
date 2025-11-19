from fastapi import APIRouter, HTTPException, Depends, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.database_models import User, VerificationLog
from app.utils.encryption import encryption_service
from pydantic import BaseModel, EmailStr
from datetime import datetime, timedelta
import hashlib
import secrets

router = APIRouter()

# Simple session storage (in production, use Redis or JWT)
active_sessions = {}

class SignupRequest(BaseModel):
    email: EmailStr
    password: str

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class LoginResponse(BaseModel):
    token: str
    email: str
    kyc_status: str

def hash_password(password: str) -> str:
    """Hash password with salt"""
    return hashlib.sha256(password.encode()).hexdigest()

def verify_password(password: str, password_hash: str) -> bool:
    """Verify password against hash"""
    return hash_password(password) == password_hash

def create_session_token() -> str:
    """Generate a secure session token"""
    return secrets.token_urlsafe(32)

@router.post("/signup")
async def signup(request: SignupRequest, db: Session = Depends(get_db)):
    """Register a new customer account"""
    try:
        # Check if user already exists
        existing_user = db.query(User).filter(User.email == request.email).first()
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
        
        # Create new user
        password_hash = hash_password(request.password)
        user = User(
            email=request.email,
            password_hash=password_hash,
            kyc_status="not_started"
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        
        # Create session
        token = create_session_token()
        active_sessions[token] = {
            "user_id": user.id,
            "email": user.email,
            "expires_at": datetime.utcnow() + timedelta(hours=24)
        }
        
        return LoginResponse(
            token=token,
            email=user.email,
            kyc_status=user.kyc_status
        )
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating account: {str(e)}"
        )

@router.post("/login")
async def login(request: LoginRequest, db: Session = Depends(get_db)):
    """Login to customer account"""
    try:
        # Find user
        user = db.query(User).filter(User.email == request.email).first()
        if not user or not user.password_hash:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password"
            )
        
        # Verify password
        if not verify_password(request.password, user.password_hash):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password"
            )
        
        # Create session
        token = create_session_token()
        active_sessions[token] = {
            "user_id": user.id,
            "email": user.email,
            "expires_at": datetime.utcnow() + timedelta(hours=24)
        }
        
        return LoginResponse(
            token=token,
            email=user.email,
            kyc_status=user.kyc_status or "not_started"
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error logging in: {str(e)}"
        )

@router.post("/logout")
async def logout(token: str):
    """Logout from customer account"""
    if token in active_sessions:
        del active_sessions[token]
    return {"message": "Logged out successfully"}

@router.get("/me")
async def get_current_user(token: str, db: Session = Depends(get_db)):
    """Get current user information and KYC status"""
    # Verify token
    if token not in active_sessions:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired session"
        )
    
    session = active_sessions[token]
    
    # Check expiration
    if datetime.utcnow() > session["expires_at"]:
        del active_sessions[token]
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Session expired"
        )
    
    # Get user
    user = db.query(User).filter(User.id == session["user_id"]).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Get latest verification
    latest_verification = db.query(VerificationLog).filter(
        VerificationLog.user_id == user.id
    ).order_by(VerificationLog.created_at.desc()).first()
    
    verification_data = None
    if latest_verification:
        verification_data = {
            "verification_id": latest_verification.verification_id,
            "status": latest_verification.status,
            "admin_status": latest_verification.admin_status,
            "document_status": latest_verification.document_status,
            "liveness_status": latest_verification.liveness_status,
            "compliance_status": latest_verification.compliance_status,
            "risk_level": latest_verification.risk_level,
            "admin_notes": latest_verification.admin_notes,
            "created_at": latest_verification.created_at.isoformat() if latest_verification.created_at else None
        }
    
    # Decrypt user data if available
    full_name = None
    dob = None
    phone = None
    
    if user.full_name_encrypted:
        full_name = encryption_service.decrypt(user.full_name_encrypted)
    if user.dob_encrypted:
        dob = encryption_service.decrypt(user.dob_encrypted)
    if user.phone_encrypted:
        phone = encryption_service.decrypt(user.phone_encrypted)
    
    return {
        "email": user.email,
        "full_name": full_name,
        "dob": dob,
        "phone": phone,
        "kyc_status": user.kyc_status,
        "latest_verification": verification_data,
        "created_at": user.created_at.isoformat() if user.created_at else None
    }

def get_current_user_id(token: str) -> int:
    """Helper function to get current user ID from token"""
    if token not in active_sessions:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired session"
        )
    
    session = active_sessions[token]
    
    # Check expiration
    if datetime.utcnow() > session["expires_at"]:
        del active_sessions[token]
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Session expired"
        )
    
    return session["user_id"]
