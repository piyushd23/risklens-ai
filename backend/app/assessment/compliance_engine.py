from typing import List, Dict, Any

class ComplianceEngine:
    @staticmethod
    def calculate_scores(findings: List[Dict[str, Any]]) -> Dict[str, float]:
        """
        Calculates Security Score (out of 100) and Compliance Score (out of 100).
        """
        # Deduct based on severity
        security_score = 100.0
        
        # Track domains for compliance
        domains = {
            "HTTP Headers": True,
            "Cookie Security": True,
            "CSRF Protection": True,
            "Information Leakage": True,
            "Transport Security": True
        }
        
        for finding in findings:
            severity = finding.get("severity", "Low")
            title = finding.get("title", "").lower()
            
            # Severity-based deductions
            if severity == "Critical":
                security_score -= 15.0
            elif severity == "High":
                security_score -= 10.0
            elif severity == "Medium":
                security_score -= 5.0
            else: # Low
                security_score -= 2.0
                
            # Domain tracking
            if "header" in title or "csp" in title or "hsts" in title or "referrer" in title:
                domains["HTTP Headers"] = False
            if "cookie" in title or "session" in title:
                domains["Cookie Security"] = False
            if "csrf" in title or "cross-site request forgery" in title:
                domains["CSRF Protection"] = False
            if "leak" in title or "key" in title or "trace" in title or "disclosure" in title:
                domains["Information Leakage"] = False
            if "http" in title or "ssl" in title:
                domains["Transport Security"] = False
                
        # Bound security score to [0.0, 100.0]
        security_score = max(0.0, min(100.0, security_score))
        
        # Compliance score: % of domains fully compliant
        compliant_domains = sum(1 for val in domains.values() if val)
        compliance_score = (compliant_domains / len(domains)) * 100.0
        
        return {
            "security_score": security_score,
            "compliance_score": compliance_score
        }
