from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.database_models import VerificationLog
from app.models.schemas import VerificationStatus

router = APIRouter()

@router.get("/status/{verification_id}", response_model=VerificationStatus)
async def get_status(
    verification_id: str,
    db: Session = Depends(get_db)
):
    """
    Get the current status of a verification request
    """
    try:
        verification = db.query(VerificationLog).filter(
            VerificationLog.verification_id == verification_id
        ).first()
        
        if not verification:
            raise HTTPException(status_code=404, detail="Verification not found")
        
        return VerificationStatus(
            verification_id=verification.verification_id,
            status=verification.status,
            risk_score=verification.risk_score,
            risk_level=verification.risk_level,
            document_status=verification.document_status,
            liveness_status=verification.liveness_status,
            compliance_status=verification.compliance_status,
            requires_human_review=verification.requires_human_review,
            created_at=verification.created_at,
            completed_at=verification.completed_at
        )
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving status: {str(e)}")
