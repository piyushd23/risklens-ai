from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from app.database import get_db
from app.models import Finding, Assessment, User
from app.schemas import FindingResponse
from app.auth import RoleChecker, get_current_user
from app.services.audit_service import AuditService

router = APIRouter(prefix="/findings", tags=["Findings"])

@router.get("/assessment/{assessment_id}", response_model=List[FindingResponse])
def get_assessment_findings(assessment_id: int, db: Session = Depends(get_db),
                            current_user: User = Depends(RoleChecker(allowed_roles=["ADMIN", "SECURITY_ANALYST", "DEVELOPER"]))):
    # Verify assessment exists
    assess = db.query(Assessment).filter(Assessment.id == assessment_id).first()
    if not assess:
        raise HTTPException(status_code=404, detail="Scan not found")
        
    findings = db.query(Finding).filter(Finding.assessment_id == assessment_id).all()
    return findings

@router.get("/target/{target_id}", response_model=List[FindingResponse])
def get_target_findings(target_id: int, db: Session = Depends(get_db),
                        current_user: User = Depends(RoleChecker(allowed_roles=["ADMIN", "SECURITY_ANALYST", "DEVELOPER"]))):
    findings = db.query(Finding).join(Assessment).filter(
        Assessment.target_id == target_id,
        Finding.is_false_positive == False
    ).all()
    return findings

@router.post("/{finding_id}/false-positive", response_model=FindingResponse)
def toggle_false_positive(finding_id: int, is_false: bool, db: Session = Depends(get_db),
                          current_user: User = Depends(RoleChecker(allowed_roles=["ADMIN", "SECURITY_ANALYST"]))):
    finding = db.query(Finding).filter(Finding.id == finding_id).first()
    if not finding:
        raise HTTPException(status_code=404, detail="Finding not found")
        
    finding.is_false_positive = is_false
    db.commit()
    db.refresh(finding)
    
    # Audit log
    AuditService.log_event(
        db,
        action="UPDATE_FINDING",
        details=f"Marked finding '{finding.title}' as false-positive: {is_false}",
        user_id=current_user.id,
        username=current_user.username
    )
    
    return finding
