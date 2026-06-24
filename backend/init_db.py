import sys
import os
from datetime import datetime, timedelta
import json

# Adjust python path to import app correctly
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.database import Base, engine, SessionLocal
from app.models import Role, User, Target, Asset, Assessment, Finding, Analytics, RiskScore, AuditLog, Notification
from app.auth import get_password_hash
from app.ai.risk_model import RiskPrioritizationModel
from app.ai.anomaly_detection import AnomalyDetector
from app.assessment.compliance_engine import ComplianceEngine

def init_database():
    print("Initialising SQLite database...")
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    
    try:
        # 1. Create Roles
        print("Seeding RBAC Roles...")
        roles_data = [
            ("ADMIN", "Full access to administer users, targets, findings, and global system parameters."),
            ("SECURITY_ANALYST", "Standard security investigator. Can configure targets, launch discovery scans, and view reports."),
            ("DEVELOPER", "Read-only access. Can inspect security findings, view compliance scores, and access remediation guides.")
        ]
        
        role_map = {}
        for role_name, desc in roles_data:
            role = db.query(Role).filter(Role.name == role_name).first()
            if not role:
                role = Role(name=role_name, description=desc)
                db.add(role)
                db.flush()
            role_map[role_name] = role.id

        db.commit()
        
        # 2. Create Default Users
        print("Seeding default user accounts...")
        users_data = [
            ("admin", "admin@risklens.ai", "AdminPassword123!", "ADMIN"),
            ("analyst", "analyst@risklens.ai", "AnalystPassword123!", "SECURITY_ANALYST"),
            ("developer", "developer@risklens.ai", "DeveloperPassword123!", "DEVELOPER")
        ]
        
        user_ids = {}
        for username, email, pwd, role_name in users_data:
            user = db.query(User).filter(User.username == username).first()
            if not user:
                hashed = get_password_hash(pwd)
                user = User(
                    username=username,
                    email=email,
                    hashed_password=hashed,
                    role_id=role_map[role_name],
                    is_active=True
                )
                db.add(user)
                db.flush()
            user_ids[username] = user.id
            
        db.commit()
        
        # 3. Create Sample Targets
        print("Seeding sample target profiles...")
        targets_data = [
            {
                "name": "OWASP Juice Shop Sandbox",
                "url": "https://juice-shop.herokuapp.com",
                "description": "Intended vulnerable web application for security learning.",
                "environment": "Staging",
                "crawl_depth": 3,
                "auth_type": "None",
                "created_by": user_ids["analyst"]
            },
            {
                "name": "Corporate Portal Demo",
                "url": "http://corporate-portal-staging.local",
                "description": "Internal employee directory web interface.",
                "environment": "Development",
                "crawl_depth": 2,
                "auth_type": "Basic",
                "auth_config": json.dumps({"username": "guest", "password": "password"}),
                "created_by": user_ids["admin"]
            }
        ]
        
        target_ids = []
        for t_data in targets_data:
            target = db.query(Target).filter(Target.url == t_data["url"]).first()
            if not target:
                target = Target(**t_data)
                db.add(target)
                db.flush()
            target_ids.append(target.id)
            
        db.commit()
        
        # 4. Create Assets for Juice Shop Target
        print("Seeding discovered assets inventory...")
        target_id = target_ids[0]
        assets_data = [
            ("https://juice-shop.herokuapp.com/", "page", "GET", "[]"),
            ("https://juice-shop.herokuapp.com/#/login", "page", "GET", "[]"),
            ("https://juice-shop.herokuapp.com/#/register", "page", "GET", "[]"),
            ("https://juice-shop.herokuapp.com/api/Users/login", "form", "POST", json.dumps([{"name": "email", "type": "text"}, {"name": "password", "type": "password"}])),
            ("https://juice-shop.herokuapp.com/assets/public/main.js", "page", "GET", "[]"),
            ("https://juice-shop.herokuapp.com/api/Feedbacks/", "form", "POST", json.dumps([{"name": "comment", "type": "text"}, {"name": "rating", "type": "number"}])),
        ]
        
        for url, atype, method, params in assets_data:
            asset = db.query(Asset).filter(Asset.url == url, Asset.target_id == target_id).first()
            if not asset:
                db_asset = Asset(
                    target_id=target_id,
                    url=url,
                    asset_type=atype,
                    method=method,
                    parameters=params,
                    headers=json.dumps({"Server": "Express/4.17.1", "Content-Type": "text/html"}),
                    cookies=json.dumps({"session": "mock-session-cookie-12345"})
                )
                db.add(db_asset)
        db.commit()
        
        # 5. Seed Historical Assessments & Findings to populate ML datasets
        print("Creating historical assessments for AI anomaly models...")
        ai_risk_model = RiskPrioritizationModel()
        
        # Generate 9 historical completed runs (to create baseline trends)
        for i in range(1, 10):
            started_time = datetime.utcnow() - timedelta(days=10 - i, hours=i)
            completed_time = started_time + timedelta(minutes=15)
            
            assessment = Assessment(
                target_id=target_id,
                status="COMPLETED",
                progress=100,
                started_at=started_time,
                completed_at=completed_time,
                created_by=user_ids["analyst"],
                log_data=json.dumps(["Initialised crawl", "Mapped endpoints", "Scanned headers", "Crawl completed."])
            )
            db.add(assessment)
            db.flush()
            
            # Add 2-5 findings per historical assessment
            finding_keys = ["missing_csp", "missing_x_frame_options", "cookie_not_secure", "cookie_not_httponly", "missing_x_content_type_options"]
            selected_keys = finding_keys[:(i % 4) + 2]
            
            assess_findings = []
            for key in selected_keys:
                title = f"Vulnerability {key.replace('_', ' ').title()}"
                desc = f"Historical finding details for {key} security weakness."
                severity = "Medium" if "cookie" in key else "Low"
                cvss_score = 5.3 if severity == "Medium" else 3.7
                
                finding = Finding(
                    assessment_id=assessment.id,
                    title=title,
                    description=desc,
                    severity=severity,
                    cvss_score=cvss_score,
                    confidence_level="High",
                    owasp_category="A05:2021-Security Misconfiguration",
                    evidence="HTTP Response header check failed",
                    risk_explanation="Vulnerability could expose browser properties.",
                    remediation_guidance="Apply secure header configuration.",
                    discovered_at=completed_time
                )
                db.add(finding)
                db.flush()
                assess_findings.append({
                    "severity": severity,
                    "title": title,
                    "cvss_score": cvss_score,
                    "owasp_category": "A05:2021-Security Misconfiguration"
                })
                
                # Predict risk score
                pred = ai_risk_model.predict_risk(cvss_score, "A05:2021-Security Misconfiguration", 3, "Medium", i*2)
                risk_score = RiskScore(
                    finding_id=finding.id,
                    priority_score=pred["priority_score"],
                    recommended_action=pred["recommended_action"],
                    remediation_priority=pred["remediation_priority"]
                )
                db.add(risk_score)
            
            # Add Analytics summary for each run
            scores = ComplianceEngine.calculate_scores(assess_findings)
            analytics = Analytics(
                target_id=target_id,
                security_score=scores["security_score"],
                compliance_score=scores["compliance_score"],
                total_vulns=len(assess_findings),
                critical_vulns=0,
                high_vulns=0,
                medium_vulns=sum(1 for f in assess_findings if f["severity"] == "Medium"),
                low_vulns=sum(1 for f in assess_findings if f["severity"] == "Low"),
                calculated_at=completed_time
            )
            db.add(analytics)
            
        db.commit()
        
        # 6. Fit Anomaly Model on baseline
        print("Seeding Anomaly Detection baseline models...")
        anomaly_detector = AnomalyDetector()
        anomaly_detector.train() # establishes default pkl files

        # 7. Add notification logs
        notif = Notification(
            user_id=user_ids["analyst"],
            message="Welcome to RiskLens AI! Seeding complete. 9 historical assessments are preloaded.",
            is_read=False
        )
        db.add(notif)
        
        # 8. Add Audit Logs
        audit = AuditLog(
            user_id=user_ids["admin"],
            username="admin",
            action="SYSTEM_INIT",
            details="Completed database initialization and sample sandbox user seeding.",
            ip_address="127.0.0.1"
        )
        db.add(audit)
        
        db.commit()
        print("Database successfully initialized and seeded.")
        
    except Exception as e:
        db.rollback()
        print(f"Error seeding database: {e}")
        raise e
    finally:
        db.close()

if __name__ == "__main__":
    init_database()
