from fastapi import APIRouter, UploadFile, File, Form, HTTPException, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.database_models import User, VerificationLog
from app.models.schemas import VerificationResponse, LivenessChallenge
from app.utils.encryption import encryption_service
from app.services.liveness_service import get_ai_liveness_service

# Get AI service instance
LivenessService = get_ai_liveness_service()
import uuid
import os
from datetime import datetime
import shutil

router = APIRouter()

UPLOAD_DIR = "./uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

@router.post("/ingest", response_model=VerificationResponse)
async def ingest_verification(
    token: str = Form(...),
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
    Requires authentication token
    """
    try:
        # Import here to avoid circular dependency
        from app.api.auth import get_current_user_id
        
        # Verify authentication
        user_id = get_current_user_id(token)
        
        # Get user
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        print(f"\n{'='*60}\nINGEST REQUEST: Received Name='{full_name}', DOB='{dob}', Email='{user.email}'\n{'='*60}")
        
        # Generate unique verification ID
        verification_id = str(uuid.uuid4())
        
        # Update user data
        user.full_name_encrypted = encryption_service.encrypt(full_name)
        user.dob_encrypted = encryption_service.encrypt(dob)
        user.phone_encrypted = encryption_service.encrypt(phone)
        user.kyc_status = "pending"
        
        db.commit()
        db.refresh(user)
        
        # Save uploaded files
        # Get file extension from uploaded file
        doc_ext = os.path.splitext(document_image.filename)[1] or '.jpg'
        video_ext = os.path.splitext(video.filename)[1] or '.webm'
        
        doc_path = os.path.join(UPLOAD_DIR, f"{verification_id}_document{doc_ext}")
        video_path = os.path.join(UPLOAD_DIR, f"{verification_id}_video{video_ext}")
        
        with open(doc_path, "wb") as buffer:
            shutil.copyfileobj(document_image.file, buffer)
        
        with open(video_path, "wb") as buffer:
            shutil.copyfileobj(video.file, buffer)
        
        # Check if verification log already exists for this user
        existing_verification = db.query(VerificationLog).filter(
            VerificationLog.user_id == user.id
        ).first()
        
        if existing_verification:
            # Update existing record for re-KYC
            print(f"RE-KYC: Updating existing verification record for user {user.email}")
            existing_verification.verification_id = verification_id
            existing_verification.status = "pending"
            existing_verification.risk_score = 0.0
            existing_verification.risk_level = "pending"
            existing_verification.document_status = "pending"
            existing_verification.liveness_status = "pending"
            existing_verification.compliance_status = "pending"
            existing_verification.admin_status = "pending_review"
            existing_verification.admin_notes = None  # Clear old notes
            existing_verification.rejection_reason = None  # Clear old rejection reason
            existing_verification.explanation = None
            existing_verification.document_analysis = None
            existing_verification.liveness_analysis = None
            existing_verification.compliance_analysis = None
            existing_verification.updated_at = datetime.utcnow()
            existing_verification.completed_at = None
            verification = existing_verification
        else:
            # Create new verification log for first-time KYC
            print(f"NEW KYC: Creating new verification record for user {user.email}")
            verification = VerificationLog(
                verification_id=verification_id,
                user_id=user.id,
                status="pending",
                risk_score=0.0,
                risk_level="pending",
                document_status="pending",
                liveness_status="pending",
                compliance_status="pending",
                admin_status="pending_review",
                admin_notes=None
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
