from sqlalchemy.orm import Session
from app.models import Finding, Target, Analytics, RiskScore, Assessment
from typing import List, Dict, Any

class PowerBIConnector:
    @staticmethod
    def get_findings_table(db: Session) -> List[Dict[str, Any]]:
        """
        Denormalized flat table of security findings for Power BI.
        """
        findings = db.query(Finding).all()
        data = []
        for f in findings:
            target_name = "Unknown Target"
            if f.assessment and f.assessment.target:
                target_name = f.assessment.target.name
                
            priority_score = 0.0
            remediation_priority = "Low"
            recommended_action = "N/A"
            if f.risk_score:
                priority_score = f.risk_score.priority_score
                remediation_priority = f.risk_score.remediation_priority
                recommended_action = f.risk_score.recommended_action
                
            data.append({
                "FindingID": f.id,
                "TargetName": target_name,
                "AssessmentID": f.assessment_id,
                "Title": f.title,
                "Severity": f.severity,
                "CVSSScore": f.cvss_score,
                "ConfidenceLevel": f.confidence_level,
                "OWASPCategory": f.owasp_category,
                "IsFalsePositive": f.is_false_positive,
                "DiscoveredDate": f.discovered_at.strftime("%Y-%m-%d %H:%M:%S"),
                "AIPriorityScore": priority_score,
                "AIRemediationPriority": remediation_priority,
                "AIRecommendedAction": recommended_action
            })
        return data

    @staticmethod
    def get_trends_table(db: Session) -> List[Dict[str, Any]]:
        """
        Historical compliance and security metrics trend table for Power BI.
        """
        history = db.query(Analytics).all()
        data = []
        for h in history:
            target_name = "Unknown Target"
            if h.target:
                target_name = h.target.name
                
            data.append({
                "AnalyticsID": h.id,
                "TargetName": target_name,
                "SecurityScore": h.security_score,
                "ComplianceScore": h.compliance_score,
                "TotalVulnerabilities": h.total_vulns,
                "CriticalVulnerabilities": h.critical_vulns,
                "HighVulnerabilities": h.high_vulns,
                "MediumVulnerabilities": h.medium_vulns,
                "LowVulnerabilities": h.low_vulns,
                "CalculatedDate": h.calculated_at.strftime("%Y-%m-%d %H:%M:%S")
            })
        return data

    @staticmethod
    def get_powerbi_m_query(api_base_url: str) -> str:
        """
        Generates Power Query M Language script for copying directly into Power BI Advanced Editor.
        """
        return f"""
// Copy this script into Power BI Advanced Editor to load findings
let
    Source = Json.Document(Web.Contents("{api_base_url}/api/v1/analytics/powerbi/findings")),
    #"Converted to Table" = Table.FromList(Source, Splitter.SplitByNothing(), null, null, ExtraValues.Error),
    #"Expanded Column1" = Table.ExpandRecordColumn(#"Converted to Table", "Column1", 
        {{"FindingID", "TargetName", "AssessmentID", "Title", "Severity", "CVSSScore", "ConfidenceLevel", "OWASPCategory", "IsFalsePositive", "DiscoveredDate", "AIPriorityScore", "AIRemediationPriority", "AIRecommendedAction"}}, 
        {{"FindingID", "TargetName", "AssessmentID", "Title", "Severity", "CVSSScore", "ConfidenceLevel", "OWASPCategory", "IsFalsePositive", "DiscoveredDate", "AIPriorityScore", "AIRemediationPriority", "AIRecommendedAction"}}
    )
in
    #"Expanded Column1"
"""
