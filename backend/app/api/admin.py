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
    """Get all KYC submissions with user details - one record per user"""
    try:
        # Get all users who have submitted KYC
        users_with_kyc = db.query(User).join(
            VerificationLog, User.id == VerificationLog.user_id
        ).distinct().all()
        
        submissions = []
        for user in users_with_kyc:
            # Get the latest (and only should be one) verification log for this user
            verification = db.query(VerificationLog).filter(
                VerificationLog.user_id == user.id
            ).order_by(VerificationLog.updated_at.desc()).first()
            if verification:
                # Decrypt user data
                full_name = encryption_service.decrypt(user.full_name_encrypted)
                dob = encryption_service.decrypt(user.dob_encrypted)
                phone = encryption_service.decrypt(user.phone_encrypted)
                
                # Parse detailed analysis
                import json
                document_analysis = None
                liveness_analysis = None
                compliance_analysis = None
                
                try:
                    if verification.document_analysis:
                        document_analysis = json.loads(verification.document_analysis)
                except:
                    pass
                
                try:
                    if verification.liveness_analysis:
                        liveness_analysis = json.loads(verification.liveness_analysis)
                except:
                    pass
                
                try:
                    if verification.compliance_analysis:
                        compliance_analysis = json.loads(verification.compliance_analysis)
                except:
                    pass
                
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
                    "document_analysis": document_analysis,
                    "liveness_analysis": liveness_analysis,
                    "compliance_analysis": compliance_analysis,
                    "explanation": verification.explanation,
                    "created_at": verification.created_at.isoformat() if verification.created_at else None,
                    "updated_at": verification.updated_at.isoformat() if verification.updated_at else None,
                    "_sort_timestamp": verification.updated_at  # For sorting
                })
        
        # Sort submissions by updated_at (newest first)
        submissions.sort(key=lambda x: x.get("_sort_timestamp") or x.get("created_at") or "", reverse=True)
        
        # Remove the temporary sort field
        for submission in submissions:
            submission.pop("_sort_timestamp", None)
        
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

def generate_rejection_suggestions(verification: VerificationLog) -> str:
    """Generate helpful suggestions based on what failed in verification"""
    import json
    
    suggestions = []
    
    # Parse detailed analysis
    document_analysis = None
    liveness_analysis = None
    
    try:
        if verification.document_analysis:
            document_analysis = json.loads(verification.document_analysis)
    except:
        pass
    
    try:
        if verification.liveness_analysis:
            liveness_analysis = json.loads(verification.liveness_analysis)
    except:
        pass
    
    # Document-specific suggestions
    if verification.document_status == "failed" and document_analysis:
        doc_suggestions = ["📄 DOCUMENT IMPROVEMENTS:"]
        
        if not document_analysis.get("name_match"):
            doc_suggestions.append("• Enter your full name exactly as shown on your ID document")
            doc_suggestions.append("• Ensure your name spelling matches your official ID")
        
        if not document_analysis.get("dob_match"):
            doc_suggestions.append("• Enter your date of birth exactly as shown on your ID")
            doc_suggestions.append("• Use the correct date format (YYYY-MM-DD)")
        
        if not document_analysis.get("ocr_available"):
            doc_suggestions.append("• Upload a clearer, higher quality image of your document")
            doc_suggestions.append("• Ensure all text on the document is readable and not blurred")
        
        if document_analysis.get("quality_analysis", {}).get("score", 1) < 0.7:
            doc_suggestions.append("• Use better lighting - avoid shadows and glare")
            doc_suggestions.append("• Take photo in a well-lit room with natural or bright light")
            doc_suggestions.append("• Keep the document flat and camera steady")
        
        if document_analysis.get("quality_analysis", {}).get("blur_score", 1) < 0.5:
            doc_suggestions.append("• Hold the camera steady to avoid blurry images")
            doc_suggestions.append("• Use a flat surface to place your document")
        
        if document_analysis.get("edge_analysis", {}).get("suspicious_edges"):
            doc_suggestions.append("• Ensure the document is not edited or modified")
            doc_suggestions.append("• Upload original photo, not a screenshot or photocopy")
        
        if document_analysis.get("pixel_analysis", {}).get("anomalies_found"):
            doc_suggestions.append("• Use the original document photo, not a scanned copy")
            doc_suggestions.append("• Avoid using photo editing apps")
        
        suggestions.append("\n".join(doc_suggestions))
    
    # Liveness-specific suggestions
    if verification.liveness_status == "failed" and liveness_analysis:
        liveness_suggestions = ["🎥 LIVENESS CHECK IMPROVEMENTS:"]
        
        if not liveness_analysis.get("audio_available") or not liveness_analysis.get("audio_match"):
            liveness_suggestions.append("• Speak clearly and loudly during recording")
            liveness_suggestions.append("• Say the EXACT phrase shown on screen")
            liveness_suggestions.append("• Move closer to the microphone")
            liveness_suggestions.append("• Reduce background noise - find a quiet room")
            liveness_suggestions.append("• Ensure your browser has microphone permissions")
        
        if not liveness_analysis.get("face_detected"):
            liveness_suggestions.append("• Position your face clearly in front of the camera")
            liveness_suggestions.append("• Ensure good lighting on your face")
            liveness_suggestions.append("• Remove any face coverings or obstructions")
        
        if not liveness_analysis.get("gesture_match"):
            liveness_suggestions.append("• Perform the EXACT gesture shown (e.g., hold up correct number of fingers)")
            liveness_suggestions.append("• Show the gesture clearly to the camera")
            liveness_suggestions.append("• Hold the gesture for 2-3 seconds")
        
        if liveness_analysis.get("spoof_score", 0) > 0.3:
            liveness_suggestions.append("• Record live video - do not use pre-recorded videos")
            liveness_suggestions.append("• Show natural movement and facial expressions")
            liveness_suggestions.append("• Do not hold up photos or use video screens")
        
        # Note: Removed technical 'issues' array to avoid showing technical details to users
        # Technical details like "Audio Match: 0.0%" should only be in admin panel
        
        suggestions.append("\n".join(liveness_suggestions))
    
    # Compliance suggestions
    if verification.compliance_status == "failed":
        compliance_suggestions = [
            "⚖️ COMPLIANCE REQUIREMENTS:",
            "• Ensure you meet the age requirements (18+ years)",
            "• Verify your personal information is correct",
            "• Contact support if you believe this is an error"
        ]
        suggestions.append("\n".join(compliance_suggestions))
    
    # General tips
    general_tips = [
        "💡 GENERAL TIPS:",
        "• Use a modern smartphone or webcam with good quality",
        "• Ensure stable internet connection during submission",
        "• Complete the process in one sitting without interruptions",
        "• Follow all on-screen instructions carefully",
        "• Contact support if you need assistance: support@deepverify.com"
    ]
    suggestions.append("\n".join(general_tips))
    
    return "\n\n".join(suggestions)

@router.post("/kyc-submissions/{verification_id}/reject")
async def reject_kyc(
    verification_id: str,
    notes: Optional[str] = None,
    db: Session = Depends(get_db),
    admin: str = Depends(verify_admin)
):
    """Reject a KYC submission with helpful suggestions"""
    try:
        verification = db.query(VerificationLog).filter(
            VerificationLog.verification_id == verification_id
        ).first()
        
        if not verification:
            raise HTTPException(status_code=404, detail="Verification not found")
        
        # Generate intelligent suggestions based on failures
        auto_suggestions = generate_rejection_suggestions(verification)
        
        # Store admin notes separately from user-facing suggestions
        verification.admin_status = "rejected"
        verification.admin_notes = notes or f"Rejected by {admin}"  # Short note for admin panel
        
        # Store detailed user-facing suggestions in rejection_reason
        if notes:
            # Include admin's custom message in user-facing suggestions
            verification.rejection_reason = f"ADMIN FEEDBACK:\n{notes}\n\n{auto_suggestions}"
        else:
            # Just show AI-generated suggestions
            verification.rejection_reason = auto_suggestions
        
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
            "suggestions": auto_suggestions,
            "message": "KYC submission rejected with helpful suggestions sent to user"
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
