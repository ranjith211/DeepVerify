from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.database_models import User, VerificationLog
from app.services.document_service import get_ai_document_service
from app.services.liveness_service import get_ai_liveness_service
from app.services.compliance_service import ComplianceService
from app.services.xai_service import XAIService

# Get AI service instances
DocumentService = get_ai_document_service()
LivenessService = get_ai_liveness_service()
from app.utils.encryption import encryption_service
from app.mongodb import get_ai_logs, get_audit_logs
import os
from datetime import datetime

router = APIRouter()

UPLOAD_DIR = "./uploads"

@router.post("/verify/{verification_id}")
async def verify(
    verification_id: str,
    db: Session = Depends(get_db)
):
    """
    Perform complete verification process for a given verification ID
    Runs document, liveness, and compliance checks
    """
    try:
        # Get verification record
        verification = db.query(VerificationLog).filter(
            VerificationLog.verification_id == verification_id
        ).first()
        
        if not verification:
            raise HTTPException(status_code=404, detail="Verification not found")
        
        # Get user data
        user = db.query(User).filter(User.id == verification.user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Decrypt user data
        full_name = encryption_service.decrypt(user.full_name_encrypted)
        dob = encryption_service.decrypt(user.dob_encrypted)
        print(f"\n{'='*60}\nVERIFICATION REQUEST: User entered Name='{full_name}', DOB='{dob}'\n{'='*60}")
        
        # File paths - try multiple extensions
        doc_path = None
        video_path = None
        
        # Find document file
        for ext in ['.jpg', '.jpeg', '.png']:
            path = os.path.join(UPLOAD_DIR, f"{verification_id}_document{ext}")
            if os.path.exists(path):
                doc_path = path
                break
        
        # Find video file
        for ext in ['.webm', '.mp4', '.mov']:
            path = os.path.join(UPLOAD_DIR, f"{verification_id}_video{ext}")
            if os.path.exists(path):
                video_path = path
                break
        
        if not doc_path or not os.path.exists(doc_path):
            raise HTTPException(status_code=404, detail="Document file not found")
        
        if not video_path or not os.path.exists(video_path):
            raise HTTPException(status_code=404, detail="Video file not found")
        
        # 1. Document Analysis with name/DOB verification
        doc_valid, doc_confidence, doc_analysis = DocumentService.analyze_document(
            doc_path, 
            expected_name=full_name,
            expected_dob=dob
        )
        verification.document_status = "passed" if doc_valid else "failed"
        
        # 2. Liveness Check (mock challenge for now)
        mock_challenge = {"expected_phrase": "blue cat", "expected_gesture": "hold up three fingers"}
        liveness_valid, liveness_confidence, liveness_analysis = LivenessService.validate_liveness(
            video_path, mock_challenge
        )
        verification.liveness_status = "passed" if liveness_valid else "failed"
        
        # 3. Compliance Check
        compliance_result = ComplianceService.perform_compliance_check(full_name, dob)
        verification.compliance_status = "passed" if compliance_result["passed"] else "failed"
        
        # 4. Calculate Overall Risk Score
        overall_risk = XAIService.calculate_risk_score(
            doc_valid,
            doc_confidence,
            liveness_valid,
            liveness_confidence,
            compliance_result["risk_score"]
        )
        
        verification.risk_score = overall_risk
        
        # Determine risk level and admin status
        if overall_risk < 0.3:
            verification.risk_level = "low"
            verification.status = "approved"
            # Low risk but still needs admin review
            if not verification.admin_status or verification.admin_status == "pending_review":
                verification.admin_status = "pending_review"
        elif overall_risk < 0.6:
            verification.risk_level = "medium"
            verification.status = "review_required"
            verification.requires_human_review = True
            # Medium risk requires admin review
            if not verification.admin_status or verification.admin_status == "pending_review":
                verification.admin_status = "pending_review"
        else:
            verification.risk_level = "high"
            verification.status = "rejected"
            # High risk requires admin review
            if not verification.admin_status or verification.admin_status == "pending_review":
                verification.admin_status = "pending_review"
        
        # 5. Generate Explanation
        explanation = XAIService.generate_explanation(
            doc_analysis,
            liveness_analysis,
            compliance_result,
            overall_risk
        )
        verification.explanation = explanation
        verification.completed_at = datetime.utcnow()
        
        # Store detailed analysis as JSON strings
        import json
        verification.document_analysis = json.dumps(doc_analysis)
        verification.liveness_analysis = json.dumps(liveness_analysis)
        verification.compliance_analysis = json.dumps(compliance_result)
        
        # Update user KYC status based on verification result
        # Keep as pending until admin reviews (except for very low risk auto-approve)
        if verification.status == "approved" and overall_risk < 0.2:
            user.kyc_status = "approved"
        elif verification.status == "rejected" and overall_risk > 0.8:
            user.kyc_status = "rejected"
        else:
            # All other cases need admin review
            user.kyc_status = "pending"
        
        # Save to database
        db.commit()
        
        # Log to MongoDB
        ai_logs = get_ai_logs()
        ai_logs.insert_one({
            "verification_id": verification_id,
            "timestamp": datetime.utcnow(),
            "document_analysis": doc_analysis,
            "liveness_analysis": liveness_analysis,
            "compliance_analysis": compliance_result,
            "risk_score": overall_risk,
            "risk_level": verification.risk_level
        })
        
        audit_logs = get_audit_logs()
        audit_logs.insert_one({
            "verification_id": verification_id,
            "user_id": user.id,
            "action": "verification_completed",
            "status": verification.status,
            "timestamp": datetime.utcnow()
        })
        
        return {
            "verification_id": verification_id,
            "status": verification.status,
            "risk_score": overall_risk,
            "risk_level": verification.risk_level,
            "requires_human_review": verification.requires_human_review,
            "message": "Verification completed successfully"
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error during verification: {str(e)}")
