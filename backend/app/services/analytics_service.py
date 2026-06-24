from sqlalchemy.orm import Session
from sqlalchemy import func
from app.models import Target, Assessment, Finding, Analytics, RiskScore
from typing import Dict, Any, List
from datetime import datetime, timedelta

class AnalyticsService:
    @staticmethod
    def get_dashboard_stats(db: Session) -> Dict[str, Any]:
        """
        Calculates high-level metrics for the executive dashboards.
        """
        total_targets = db.query(Target).count()
        total_scans = db.query(Assessment).count()
        total_findings = db.query(Finding).filter(Finding.is_false_positive == False).count()
        
        # Calculate overall security score average
        recent_analytics = db.query(Analytics).order_by(Analytics.calculated_at.desc()).limit(10).all()
        avg_security = sum(a.security_score for a in recent_analytics) / len(recent_analytics) if recent_analytics else 100.0
        avg_compliance = sum(a.compliance_score for a in recent_analytics) / len(recent_analytics) if recent_analytics else 100.0
        
        # Severity Distribution
        severity_dist = {"Critical": 0, "High": 0, "Medium": 0, "Low": 0}
        findings_sev = db.query(Finding.severity, func.count(Finding.id)).filter(
            Finding.is_false_positive == False
        ).group_by(Finding.severity).all()
        
        for sev, count in findings_sev:
            if sev in severity_dist:
                severity_dist[sev] = count
                
        # OWASP Distribution
        owasp_dist = {}
        findings_owasp = db.query(Finding.owasp_category, func.count(Finding.id)).filter(
            Finding.is_false_positive == False
        ).group_by(Finding.owasp_category).all()
        
        for cat, count in findings_owasp:
            if cat:
                owasp_dist[cat] = count
                
        # Recent Scans
        recent_scans = db.query(Assessment).order_by(Assessment.started_at.desc()).limit(5).all()
        
        # Recent Findings
        recent_findings = db.query(Finding).filter(
            Finding.is_false_positive == False
        ).order_by(Finding.discovered_at.desc()).limit(5).all()
        
        return {
            "total_targets": total_targets,
            "total_scans": total_scans,
            "total_findings": total_findings,
            "overall_security_score": round(avg_security, 1),
            "overall_compliance_score": round(avg_compliance, 1),
            "severity_distribution": severity_dist,
            "owasp_distribution": owasp_dist,
            "recent_scans": recent_scans,
            "recent_findings": recent_findings
        }

    @staticmethod
    def get_target_trends(db: Session, target_id: int) -> List[Dict[str, Any]]:
        """
        Gets timeline data points of findings and security scores for a target.
        """
        history = db.query(Analytics).filter(Analytics.target_id == target_id).order_by(
            Analytics.calculated_at.asc()
        ).all()
        
        trends = []
        for h in history:
            trends.append({
                "date": h.calculated_at.strftime("%Y-%m-%d"),
                "security_score": h.security_score,
                "compliance_score": h.compliance_score,
                "total_vulns": h.total_vulns,
                "critical": h.critical_vulns,
                "high": h.high_vulns,
                "medium": h.medium_vulns,
                "low": h.low_vulns
            })
        return trends
