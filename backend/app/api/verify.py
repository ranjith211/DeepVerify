from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.database_models import User, VerificationLog
from app.services.document_service import DocumentService
from app.services.liveness_service import LivenessService
from app.services.compliance_service import ComplianceService
from app.services.xai_service import XAIService
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
        
        # File paths
        doc_path = os.path.join(UPLOAD_DIR, f"{verification_id}_document.jpg")
        video_path = os.path.join(UPLOAD_DIR, f"{verification_id}_video.mp4")
        
        # 1. Document Analysis
        doc_valid, doc_confidence, doc_analysis = DocumentService.analyze_document(doc_path)
        verification.document_status = "passed" if doc_valid else "failed"
        
        # 2. Extract and verify data from document
        extracted_data = DocumentService.extract_data(doc_path, full_name)
        
        # Check if extracted name matches provided name (case-insensitive comparison)
        name_match = False
        name_match_confidence = 0.0
        
        if extracted_data.get("full_name") and full_name:
            extracted_name_clean = extracted_data["full_name"].lower().strip()
            provided_name_clean = full_name.lower().strip()
            
            # Simple name matching (in production, use fuzzy matching)
            if extracted_name_clean == provided_name_clean:
                name_match = True
                name_match_confidence = 0.95
            elif extracted_name_clean in provided_name_clean or provided_name_clean in extracted_name_clean:
                name_match = True
                name_match_confidence = 0.75
            else:
                name_match = False
                name_match_confidence = 0.20
                # If name doesn't match, mark document as failed
                doc_valid = False
                doc_analysis["name_verification"] = {
                    "matched": False,
                    "extracted_name": extracted_data["full_name"],
                    "provided_name": full_name,
                    "details": "Name on document does not match provided information"
                }
                verification.document_status = "failed"
        else:
            # No name extracted - document invalid
            name_match = False
            name_match_confidence = 0.0
            doc_valid = False
            verification.document_status = "failed"
            doc_analysis["name_verification"] = {
                "matched": False,
                "details": "Unable to extract name from document"
            }
        
        # 3. Liveness Check (mock challenge for now)
        mock_challenge = {"expected_phrase": "blue cat", "expected_gesture": "hold up three fingers"}
        liveness_valid, liveness_confidence, liveness_analysis = LivenessService.validate_liveness(
            video_path, mock_challenge
        )
        verification.liveness_status = "passed" if liveness_valid else "failed"
        
        # 4. Compliance Check
        compliance_result = ComplianceService.perform_compliance_check(full_name, dob)
        verification.compliance_status = "passed" if compliance_result["passed"] else "failed"
        
        # 5. Calculate Overall Risk Score (including name match)
        overall_risk = XAIService.calculate_risk_score(
            doc_valid,
            doc_confidence,
            liveness_valid,
            liveness_confidence,
            compliance_result["risk_score"]
        )
        
        # Increase risk if name doesn't match
        if not name_match:
            overall_risk = min(overall_risk + 0.30, 1.0)  # Add 30% risk for name mismatch
        
        verification.risk_score = overall_risk
        
        # Determine risk level
        if overall_risk < 0.3:
            verification.risk_level = "low"
            verification.status = "approved"
        elif overall_risk < 0.6:
            verification.risk_level = "medium"
            verification.status = "review_required"
            verification.requires_human_review = True
        else:
            verification.risk_level = "high"
            verification.status = "rejected"
        
        # 6. Generate Explanation
        explanation = XAIService.generate_explanation(
            doc_analysis,
            liveness_analysis,
            compliance_result,
            overall_risk
        )
        
        # Add name verification to explanation if it failed
        if not name_match:
            explanation = f"⚠ NAME MISMATCH DETECTED\n" + \
                         f"Document name does not match provided information (Confidence: {name_match_confidence:.1%})\n\n" + \
                         explanation
        verification.explanation = explanation
        verification.completed_at = datetime.utcnow()
        
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
