from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from typing import List
import os

from app.database import get_db
from app.models import Report, Assessment, Finding, User, Analytics
from app.schemas import ReportResponse
from app.auth import RoleChecker, get_current_user
from app.services.report_service import ReportService
from app.services.audit_service import AuditService

router = APIRouter(prefix="/reports", tags=["Reports"])

@router.get("/", response_model=List[ReportResponse])
def get_reports(db: Session = Depends(get_db),
                current_user: User = Depends(RoleChecker(allowed_roles=["ADMIN", "SECURITY_ANALYST", "DEVELOPER"]))):
    return db.query(Report).order_by(Report.created_at.desc()).all()

@router.post("/generate/{assessment_id}", response_model=List[ReportResponse])
def generate_reports(assessment_id: int, db: Session = Depends(get_db),
                     current_user: User = Depends(RoleChecker(allowed_roles=["ADMIN", "SECURITY_ANALYST"]))):
    # Verify assessment exists and is completed
    assess = db.query(Assessment).filter(Assessment.id == assessment_id).first()
    if not assess:
        raise HTTPException(status_code=404, detail="Scan session not found")
    if assess.status != "COMPLETED":
        raise HTTPException(status_code=400, detail="Cannot generate report for an incomplete assessment")
        
    findings = db.query(Finding).filter(Finding.assessment_id == assessment_id).all()
    target = assess.target
    
    # Calculate scores from findings
    recent_analytics = db.query(Analytics).filter(Analytics.target_id == target.id).order_by(
        Analytics.calculated_at.desc()
    ).first()
    
    sec_score = recent_analytics.security_score if recent_analytics else 100.0
    comp_score = recent_analytics.compliance_score if recent_analytics else 100.0
    
    findings_list = []
    for f in findings:
        findings_list.append({
            "title": f.title,
            "description": f.description,
            "severity": f.severity,
            "cvss_score": f.cvss_score,
            "confidence_level": f.confidence_level,
            "owasp_category": f.owasp_category,
            "evidence": f.evidence,
            "risk_explanation": f.risk_explanation,
            "remediation_guidance": f.remediation_guidance,
        })
        
    # Generate files (JSON, HTML, PDF)
    pdf_path = ReportService.generate_pdf(target.name, target.url, assess.started_at, sec_score, comp_score, findings_list)
    html_path = ReportService.generate_html(target.name, target.url, assess.started_at, sec_score, comp_score, findings_list)
    json_path = ReportService.generate_json(target.name, target.url, assess.started_at, sec_score, comp_score, findings_list)
    
    generated_reports = []
    formats = [("pdf", pdf_path), ("html", html_path), ("json", json_path)]
    
    for r_type, path in formats:
        # Check if already recorded
        existing = db.query(Report).filter(
            Report.assessment_id == assessment_id, 
            Report.report_type == r_type
        ).first()
        
        if existing:
            existing.file_path = path
            existing.created_at = os.path.getmtime(path)
            db_report = existing
        else:
            db_report = Report(
                assessment_id=assessment_id,
                name=f"Security Assessment Report ({r_type.upper()})",
                report_type=r_type,
                file_path=path,
                created_by=current_user.id
            )
            db.add(db_report)
        
        db.flush()
        generated_reports.append(db_report)
        
    db.commit()
    
    # Audit log
    AuditService.log_event(
        db,
        action="EXPORT_REPORT",
        details=f"Generated PDF, HTML, and JSON reports for target '{target.name}' assessment ID {assessment_id}",
        user_id=current_user.id,
        username=current_user.username
    )
    
    return generated_reports

@router.get("/download/{report_id}")
def download_report(report_id: int, db: Session = Depends(get_db)):
    """
    Directly download a report by ID, streaming the file back to the browser.
    """
    report = db.query(Report).filter(Report.id == report_id).first()
    if not report:
        raise HTTPException(status_code=404, detail="Report file record not found")
        
    if not os.path.exists(report.file_path):
        raise HTTPException(status_code=404, detail="File no longer exists on system disk")
        
    filename = os.path.basename(report.file_path)
    
    media_types = {
        "pdf": "application/pdf",
        "html": "text/html",
        "json": "application/json"
    }
    mtype = media_types.get(report.report_type.lower(), "application/octet-stream")
    
    return FileResponse(
        path=report.file_path,
        filename=filename,
        media_type=mtype,
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )
