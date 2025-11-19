from fastapi import APIRouter, HTTPException, Depends, status
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.database_models import User, VerificationLog
from app.utils.encryption import encryption_service
from datetime import datetime
from typing import List, Optional
import secrets

router = APIRouter()
security = HTTPBasic()

# Simple admin credentials (in production, use proper authentication)
ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "admin"

def verify_admin(credentials: HTTPBasicCredentials = Depends(security)):
    """Verify admin credentials"""
    correct_username = secrets.compare_digest(credentials.username, ADMIN_USERNAME)
    correct_password = secrets.compare_digest(credentials.password, ADMIN_PASSWORD)
    
    if not (correct_username and correct_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Basic"},
        )
    return credentials.username

@router.get("/kyc-submissions")
async def get_all_kyc_submissions(
    db: Session = Depends(get_db),
    admin: str = Depends(verify_admin)
):
    """Get all KYC submissions with user details"""
    try:
        # Get all verification logs with user data
        verifications = db.query(VerificationLog).order_by(
            VerificationLog.created_at.desc()
        ).all()
        
        submissions = []
        for verification in verifications:
            user = db.query(User).filter(User.id == verification.user_id).first()
            if user:
                # Decrypt user data
                full_name = encryption_service.decrypt(user.full_name_encrypted)
                dob = encryption_service.decrypt(user.dob_encrypted)
                phone = encryption_service.decrypt(user.phone_encrypted)
                
                submissions.append({
                    "verification_id": verification.verification_id,
                    "user_id": user.id,
                    "email": user.email,
                    "full_name": full_name,
                    "dob": dob,
                    "phone": phone,
                    "status": verification.status,
                    "risk_level": verification.risk_level,
                    "risk_score": verification.risk_score,
                    "document_status": verification.document_status,
                    "liveness_status": verification.liveness_status,
                    "compliance_status": verification.compliance_status,
                    "admin_status": verification.admin_status,
                    "admin_notes": verification.admin_notes,
                    "created_at": verification.created_at.isoformat() if verification.created_at else None,
                    "updated_at": verification.updated_at.isoformat() if verification.updated_at else None
                })
        
        return {
            "total": len(submissions),
            "submissions": submissions
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching submissions: {str(e)}")

@router.post("/kyc-submissions/{verification_id}/approve")
async def approve_kyc(
    verification_id: str,
    notes: Optional[str] = None,
    db: Session = Depends(get_db),
    admin: str = Depends(verify_admin)
):
    """Approve a KYC submission"""
    try:
        verification = db.query(VerificationLog).filter(
            VerificationLog.verification_id == verification_id
        ).first()
        
        if not verification:
            raise HTTPException(status_code=404, detail="Verification not found")
        
        verification.admin_status = "approved"
        verification.admin_notes = notes or f"Approved by {admin}"
        verification.status = "approved"
        verification.updated_at = datetime.utcnow()
        
        # Update user KYC status
        user = db.query(User).filter(User.id == verification.user_id).first()
        if user:
            user.kyc_status = "approved"
        
        db.commit()
        
        return {
            "verification_id": verification_id,
            "admin_status": "approved",
            "message": "KYC submission approved successfully"
        }
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error approving submission: {str(e)}")

@router.post("/kyc-submissions/{verification_id}/reject")
async def reject_kyc(
    verification_id: str,
    notes: Optional[str] = None,
    db: Session = Depends(get_db),
    admin: str = Depends(verify_admin)
):
    """Reject a KYC submission"""
    try:
        verification = db.query(VerificationLog).filter(
            VerificationLog.verification_id == verification_id
        ).first()
        
        if not verification:
            raise HTTPException(status_code=404, detail="Verification not found")
        
        verification.admin_status = "rejected"
        verification.admin_notes = notes or f"Rejected by {admin}"
        verification.status = "rejected"
        verification.updated_at = datetime.utcnow()
        
        # Update user KYC status
        user = db.query(User).filter(User.id == verification.user_id).first()
        if user:
            user.kyc_status = "rejected"
        
        db.commit()
        
        return {
            "verification_id": verification_id,
            "admin_status": "rejected",
            "message": "KYC submission rejected successfully"
        }
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error rejecting submission: {str(e)}")

@router.get("/kyc-submissions/{verification_id}")
async def get_kyc_details(
    verification_id: str,
    db: Session = Depends(get_db),
    admin: str = Depends(verify_admin)
):
    """Get detailed information about a specific KYC submission"""
    try:
        verification = db.query(VerificationLog).filter(
            VerificationLog.verification_id == verification_id
        ).first()
        
        if not verification:
            raise HTTPException(status_code=404, detail="Verification not found")
        
        user = db.query(User).filter(User.id == verification.user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Decrypt user data
        full_name = encryption_service.decrypt(user.full_name_encrypted)
        dob = encryption_service.decrypt(user.dob_encrypted)
        phone = encryption_service.decrypt(user.phone_encrypted)
        
        return {
            "verification_id": verification.verification_id,
            "user": {
                "id": user.id,
                "email": user.email,
                "full_name": full_name,
                "dob": dob,
                "phone": phone,
                "created_at": user.created_at.isoformat() if user.created_at else None
            },
            "verification": {
                "status": verification.status,
                "risk_level": verification.risk_level,
                "risk_score": verification.risk_score,
                "document_status": verification.document_status,
                "liveness_status": verification.liveness_status,
                "compliance_status": verification.compliance_status,
                "admin_status": verification.admin_status,
                "admin_notes": verification.admin_notes,
                "created_at": verification.created_at.isoformat() if verification.created_at else None,
                "updated_at": verification.updated_at.isoformat() if verification.updated_at else None
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching details: {str(e)}")
