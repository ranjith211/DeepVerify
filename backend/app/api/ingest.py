from fastapi import APIRouter, UploadFile, File, Form, HTTPException, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.database_models import User, VerificationLog
from app.models.schemas import VerificationResponse, LivenessChallenge
from app.utils.encryption import encryption_service
from app.services.liveness_service import LivenessService
import uuid
import os
from datetime import datetime
import shutil

router = APIRouter()

UPLOAD_DIR = "./uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

@router.post("/ingest", response_model=VerificationResponse)
async def ingest_verification(
    email: str = Form(...),
    full_name: str = Form(...),
    dob: str = Form(...),
    phone: str = Form(...),
    document_image: UploadFile = File(...),
    video: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """
    Ingest verification request with document and video
    Creates initial verification record and stores files
    """
    try:
        # Generate unique verification ID
        verification_id = str(uuid.uuid4())
        
        # Create user or get existing
        user = db.query(User).filter(User.email == email).first()
        if not user:
            user = User(
                email=email,
                full_name_encrypted=encryption_service.encrypt(full_name),
                dob_encrypted=encryption_service.encrypt(dob),
                phone_encrypted=encryption_service.encrypt(phone)
            )
            db.add(user)
            db.commit()
            db.refresh(user)
        
        # Save uploaded files
        doc_path = os.path.join(UPLOAD_DIR, f"{verification_id}_document.jpg")
        video_path = os.path.join(UPLOAD_DIR, f"{verification_id}_video.mp4")
        
        with open(doc_path, "wb") as buffer:
            shutil.copyfileobj(document_image.file, buffer)
        
        with open(video_path, "wb") as buffer:
            shutil.copyfileobj(video.file, buffer)
        
        # Create verification log
        verification = VerificationLog(
            verification_id=verification_id,
            user_id=user.id,
            status="pending",
            risk_score=0.0,
            risk_level="pending",
            document_status="pending",
            liveness_status="pending",
            compliance_status="pending"
        )
        db.add(verification)
        db.commit()
        
        return VerificationResponse(
            verification_id=verification_id,
            status="pending",
            message="Verification request received. Processing initiated."
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing request: {str(e)}")

@router.get("/challenge/{language}")
async def get_liveness_challenge(language: str = "english"):
    """
    Get a random liveness challenge in specified language
    Supports: english, hindi, tamil
    """
    try:
        challenge = LivenessService.generate_challenge(language)
        return challenge
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating challenge: {str(e)}")
