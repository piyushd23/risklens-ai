import numpy as np
from typing import List, Dict, Any

class FeatureEngineering:
    @staticmethod
    def extract_assessment_features(findings: List[Dict[str, Any]]) -> np.ndarray:
        """
        Extracts feature vectors from a list of findings for a single assessment run.
        Features:
        1. Total finding count
        2. Average CVSS score
        3. High/Critical finding ratio
        4. Medium finding ratio
        5. Low finding ratio
        6. Unique OWASP categories count
        """
        total = len(findings)
        if total == 0:
            return np.array([0.0, 0.0, 0.0, 0.0, 0.0, 0.0])
            
        scores = [f.get("cvss_score", 0.0) for f in findings]
        avg_cvss = sum(scores) / total
        
        critical_count = sum(1 for f in findings if f.get("severity") == "Critical")
        high_count = sum(1 for f in findings if f.get("severity") == "High")
        medium_count = sum(1 for f in findings if f.get("severity") == "Medium")
        low_count = sum(1 for f in findings if f.get("severity") == "Low")
        
        ratio_critical_high = (critical_count + high_count) / total
        ratio_medium = medium_count / total
        ratio_low = low_count / total
        
        unique_owasp = len(set(f.get("owasp_category", "") for f in findings if f.get("owasp_category")))
        
        return np.array([
            float(total),
            float(avg_cvss),
            float(ratio_critical_high),
            float(ratio_medium),
            float(ratio_low),
            float(unique_owasp)
        ])

    @staticmethod
    def extract_multiple_assessments(assessments_findings: List[List[Dict[str, Any]]]) -> np.ndarray:
        matrix = []
        for findings in assessments_findings:
            matrix.append(FeatureEngineering.extract_assessment_features(findings))
        return np.array(matrix)
