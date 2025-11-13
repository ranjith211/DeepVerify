from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.database_models import VerificationLog
from app.models.schemas import RiskExplanation
from app.mongodb import get_ai_logs

router = APIRouter()

@router.get("/explain/{verification_id}", response_model=RiskExplanation)
async def get_explanation(
    verification_id: str,
    db: Session = Depends(get_db)
):
    """
    Get detailed risk explanation for a verification
    """
    try:
        # Get verification from SQL
        verification = db.query(VerificationLog).filter(
            VerificationLog.verification_id == verification_id
        ).first()
        
        if not verification:
            raise HTTPException(status_code=404, detail="Verification not found")
        
        # Get detailed analysis from MongoDB
        ai_logs = get_ai_logs()
        ai_log = ai_logs.find_one({"verification_id": verification_id})
        
        if not ai_log:
            # Return basic explanation if detailed logs not found
            return RiskExplanation(
                verification_id=verification_id,
                risk_score=verification.risk_score or 0.0,
                risk_level=verification.risk_level or "unknown",
                explanation=verification.explanation or "Analysis in progress",
                document_analysis={},
                liveness_analysis={},
                compliance_analysis={},
                recommendation="Pending analysis"
            )
        
        # Determine recommendation
        if verification.status == "approved":
            recommendation = "APPROVE: Low risk - verification passed"
        elif verification.status == "rejected":
            recommendation = "REJECT: High risk - verification failed"
        else:
            recommendation = "HUMAN REVIEW REQUIRED: Medium risk"
        
        return RiskExplanation(
            verification_id=verification_id,
            risk_score=verification.risk_score,
            risk_level=verification.risk_level,
            explanation=verification.explanation,
            document_analysis=ai_log.get("document_analysis", {}),
            liveness_analysis=ai_log.get("liveness_analysis", {}),
            compliance_analysis=ai_log.get("compliance_analysis", {}),
            recommendation=recommendation
        )
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving explanation: {str(e)}")
