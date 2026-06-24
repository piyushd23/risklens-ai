from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks, status
from sqlalchemy.orm import Session
from typing import List
import json
from datetime import datetime
import asyncio

from app.database import get_db, SessionLocal
from app.models import Assessment, Target, User, Finding, Asset, Analytics, RiskScore, Notification
from app.schemas import AssessmentResponse, AssessmentCreate
from app.auth import RoleChecker, get_current_user
from app.crawler.crawler_engine import CrawlerEngine
from app.crawler.asset_inventory import AssetInventory
from app.assessment.assessment_engine import AssessmentEngine
from app.assessment.compliance_engine import ComplianceEngine
from app.ai.risk_model import RiskPrioritizationModel
from app.ai.anomaly_detection import AnomalyDetector
from app.services.audit_service import AuditService

router = APIRouter(prefix="/assessments", tags=["Assessments"])

async def run_assessment_task(assessment_id: int):
    """
    Background worker performing crawl -> assess -> AI priority -> anomaly checks.
    """
    db = SessionLocal()
    try:
        # Load assessment and target
        assess = db.query(Assessment).filter(Assessment.id == assessment_id).first()
        if not assess:
            return
            
        target = db.query(Target).filter(Target.id == assess.target_id).first()
        if not target:
            assess.status = "FAILED"
            assess.log_data = json.dumps(["Scan failed: Target configuration profile not found."])
            db.commit()
            return

        logs = ["Initializing scan session...", f"Target: {target.url}"]
        assess.status = "CRAWLING"
        assess.progress = 20
        assess.log_data = json.dumps(logs)
        db.commit()

        # 1. RUN CRAWLER
        logs.append("Launching discovery crawler...")
        assess.log_data = json.dumps(logs)
        db.commit()

        crawler = CrawlerEngine(
            target_id=target.id,
            base_url=target.url,
            crawl_depth=target.crawl_depth,
            include_paths=target.include_paths,
            exclude_paths=target.exclude_paths,
            auth_type=target.auth_type,
            auth_config=target.auth_config
        )
        
        assets, crawl_logs = await crawler.crawl()
        logs.extend(crawl_logs)
        logs.append(f"Crawler finished. Identified {len(assets)} web assets.")
        assess.progress = 50
        assess.log_data = json.dumps(logs)
        db.commit()

        # Save to assets inventory
        AssetInventory.save_discovered_assets(db, target.id, assets)

        # 2. RUN SECURITY POSTURE ASSESSMENT
        logs.append("Commencing vulnerability and header audits...")
        assess.status = "ASSESSING"
        assess.progress = 60
        assess.log_data = json.dumps(logs)
        db.commit()

        scanner = AssessmentEngine(target.url)
        findings = scanner.run_assessment(assets, logs)
        
        logs.append(f"Assessment audits completed. Discovered {len(findings)} issues.")
        assess.progress = 80
        assess.log_data = json.dumps(logs)
        db.commit()

        # Write Findings & AI Risk Scores
        ai_model = RiskPrioritizationModel()
        findings_to_score = []
        
        # Pull asset history count
        past_findings_count = db.query(Finding).join(Assessment).filter(
            Assessment.target_id == target.id, 
            Finding.is_false_positive == False
        ).count()

        for idx, f_data in enumerate(findings):
            db_finding = Finding(
                assessment_id=assess.id,
                title=f_data["title"],
                description=f_data["description"],
                severity=f_data["severity"],
                cvss_score=f_data["cvss_score"],
                confidence_level=f_data["confidence_level"],
                owasp_category=f_data["owasp_category"],
                evidence=f_data["evidence"],
                risk_explanation=f_data["risk_explanation"],
                remediation_guidance=f_data["remediation_guidance"],
                is_false_positive=False
            )
            db.add(db_finding)
            db.flush() # loads ID
            
            # Predict AI Risk
            ai_pred = ai_model.predict_risk(
                cvss_score=f_data["cvss_score"],
                owasp_category=f_data["owasp_category"],
                finding_frequency=idx + 1,
                asset_criticality="High" if target.environment == "Production" else "Medium",
                historical_findings=past_findings_count
            )
            
            db_risk = RiskScore(
                finding_id=db_finding.id,
                priority_score=ai_pred["priority_score"],
                recommended_action=ai_pred["recommended_action"],
                remediation_priority=ai_pred["remediation_priority"]
            )
            db.add(db_risk)
            findings_to_score.append(f_data)

        # 3. RUN ANOMALY DETECTION
        logs.append("Running machine learning anomaly engines...")
        assess.log_data = json.dumps(logs)
        db.commit()
        
        # Load historical scans for this target
        past_assessments = db.query(Assessment).filter(
            Assessment.target_id == target.id,
            Assessment.status == "COMPLETED"
        ).all()
        
        past_findings_list = []
        for past in past_assessments:
            past_f = db.query(Finding).filter(Finding.assessment_id == past.id).all()
            past_findings_list.append([{"severity": pf.severity, "cvss_score": pf.cvss_score, "owasp_category": pf.owasp_category} for pf in past_f])

        anomaly_detector = AnomalyDetector()
        anomaly_report = anomaly_detector.check_anomaly(findings_to_score, past_findings_list)
        
        if anomaly_report["is_anomaly"]:
            logs.append(f"[ALERT] AI Anomaly Engine flagged scan: {anomaly_report['explanation']} (Confidence: {anomaly_report['confidence']}%)")
        else:
            logs.append(f"AI Anomaly Engine passed: Scan matches baseline trends.")
            
        assess.progress = 90
        assess.log_data = json.dumps(logs)
        db.commit()

        # 4. COMPILING SCORES AND FINISHING
        scores = ComplianceEngine.calculate_scores(findings_to_score)
        
        analytics = Analytics(
            target_id=target.id,
            security_score=scores["security_score"],
            compliance_score=scores["compliance_score"],
            total_vulns=len(findings_to_score),
            critical_vulns=sum(1 for f in findings_to_score if f["severity"] == "Critical"),
            high_vulns=sum(1 for f in findings_to_score if f["severity"] == "High"),
            medium_vulns=sum(1 for f in findings_to_score if f["severity"] == "Medium"),
            low_vulns=sum(1 for f in findings_to_score if f["severity"] == "Low"),
            calculated_at=datetime.utcnow()
        )
        db.add(analytics)

        # Send alert notification if Critical/High findings discovered
        if any(f["severity"] in ["Critical", "High"] for f in findings_to_score):
            notif = Notification(
                user_id=assess.created_by,
                message=f"Scan Alert: Target '{target.name}' completed with critical/high severities detected."
            )
            db.add(notif)
        else:
            notif = Notification(
                user_id=assess.created_by,
                message=f"Scan Success: Target '{target.name}' assessment completed."
            )
            db.add(notif)

        logs.append("Scan completed successfully. Analytics and compliance trends mapped.")
        assess.status = "COMPLETED"
        assess.progress = 100
        assess.completed_at = datetime.utcnow()
        assess.log_data = json.dumps(logs)
        
        # Log Audit event
        AuditService.log_event(
            db,
            action="RUN_SCAN_COMPLETE",
            details=f"Completed security scan on target '{target.name}'. Findings: {len(findings_to_score)}",
            user_id=assess.created_by
        )
        
        db.commit()

    except Exception as e:
        db.rollback()
        # Fallback logging
        logger_err = f"Scan aborted due to critical error: {e}"
        print(logger_err)
        try:
            assess = db.query(Assessment).filter(Assessment.id == assessment_id).first()
            if assess:
                assess.status = "FAILED"
                logs_data = json.loads(assess.log_data) if assess.log_data else []
                logs_data.append(logger_err)
                assess.log_data = json.dumps(logs_data)
                db.commit()
        except Exception:
            pass
    finally:
        db.close()

@router.get("/", response_model=List[AssessmentResponse])
def get_assessments(db: Session = Depends(get_db),
                    current_user: User = Depends(RoleChecker(allowed_roles=["ADMIN", "SECURITY_ANALYST", "DEVELOPER"]))):
    return db.query(Assessment).order_by(Assessment.started_at.desc()).all()

@router.get("/{assessment_id}", response_model=AssessmentResponse)
def get_assessment(assessment_id: int, db: Session = Depends(get_db),
                   current_user: User = Depends(RoleChecker(allowed_roles=["ADMIN", "SECURITY_ANALYST", "DEVELOPER"]))):
    assess = db.query(Assessment).filter(Assessment.id == assessment_id).first()
    if not assess:
        raise HTTPException(status_code=404, detail="Scan not found")
    return assess

@router.post("/", response_model=AssessmentResponse)
def create_assessment(assessment_in: AssessmentCreate, background_tasks: BackgroundTasks,
                      db: Session = Depends(get_db),
                      current_user: User = Depends(RoleChecker(allowed_roles=["ADMIN", "SECURITY_ANALYST"]))):
    # Verify target exists
    target = db.query(Target).filter(Target.id == assessment_in.target_id).first()
    if not target:
        raise HTTPException(status_code=404, detail="Target not found")
        
    assess = Assessment(
        target_id=target.id,
        status="PENDING",
        progress=0,
        log_data=json.dumps(["Scan queued in scheduler."]),
        started_at=datetime.utcnow(),
        created_by=current_user.id
    )
    
    db.add(assess)
    db.commit()
    db.refresh(assess)
    
    AuditService.log_event(
        db,
        action="RUN_SCAN_START",
        details=f"Queued security scan on target '{target.name}'",
        user_id=current_user.id,
        username=current_user.username
    )
    
    background_tasks.add_task(run_assessment_task, assess.id)
    return assess
