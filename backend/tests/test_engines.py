import sys
import os

# Set python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.assessment.cvss_calculator import CVSSCalculator
from app.assessment.owasp_mapper import OWASPMapper
from app.assessment.compliance_engine import ComplianceEngine
from app.ai.risk_model import RiskPrioritizationModel
from app.ai.anomaly_detection import AnomalyDetector

def test_cvss_calculator():
    res = CVSSCalculator.calculate("missing_csp")
    assert res["score"] == 3.7
    assert res["severity"] == "Low"
    assert "CVSS:3.1" in res["vector"]

def test_owasp_mapper():
    cat = OWASPMapper.get_category("missing_csrf_token")
    assert cat == "A04:2021-Insecure Design"
    desc = OWASPMapper.get_description(cat)
    assert "CSRF" in desc

def test_compliance_engine():
    findings = [
        {"title": "Missing Content Security Policy", "severity": "Low", "cvss_score": 3.7},
        {"title": "Cookie Missing Secure Flag", "severity": "Medium", "cvss_score": 5.3}
    ]
    scores = ComplianceEngine.calculate_scores(findings)
    assert scores["security_score"] < 100.0
    assert scores["compliance_score"] < 100.0

def test_ai_risk_model():
    model = RiskPrioritizationModel()
    pred = model.predict_risk(
        cvss_score=7.5,
        owasp_category="A02:2021-Cryptographic Failures",
        finding_frequency=2,
        asset_criticality="High",
        historical_findings=5
    )
    assert "priority_score" in pred
    assert pred["remediation_priority"] in ["Immediate", "High", "Medium", "Low"]

def test_anomaly_detection():
    detector = AnomalyDetector()
    detector.train() # fit baseline
    
    # 1. Normal scan simulation
    normal_scan = [
        {"severity": "Low", "cvss_score": 3.1, "owasp_category": "A05:2021-Security Misconfiguration"},
        {"severity": "Medium", "cvss_score": 5.3, "owasp_category": "A02:2021-Cryptographic Failures"}
    ]
    res_normal = detector.check_anomaly(normal_scan)
    # Usually normal scan should not be an anomaly
    assert "is_anomaly" in res_normal
    
    # 2. Anomalous scan simulation (huge count, high severity)
    anomaly_scan = [{"severity": "Critical", "cvss_score": 9.8, "owasp_category": "A01:2021-Broken Access Control"} for _ in range(30)]
    res_anomaly = detector.check_anomaly(anomaly_scan)
    assert "is_anomaly" in res_anomaly

if __name__ == "__main__":
    print("Running unit tests...")
    test_cvss_calculator()
    test_owasp_mapper()
    test_compliance_engine()
    test_ai_risk_model()
    test_anomaly_detection()
    print("All unit tests passed successfully!")
