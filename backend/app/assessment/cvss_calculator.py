from typing import Dict, Any

class CVSSCalculator:
    # Predefined finding vectors and qualitative mappings
    FINDING_MAPPING = {
        "missing_csp": {
            "score": 3.7,
            "severity": "Low",
            "vector": "CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:L/I:N/A:N",
            "confidence": "High"
        },
        "missing_hsts": {
            "score": 3.1,
            "severity": "Low",
            "vector": "CVSS:3.1/AV:N/AC:H/PR:N/UI:R/S:U/C:L/I:N/A:N",
            "confidence": "High"
        },
        "missing_x_frame_options": {
            "score": 4.7,
            "severity": "Medium",
            "vector": "CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:N/I:L/A:N",
            "confidence": "High"
        },
        "missing_x_content_type_options": {
            "score": 3.7,
            "severity": "Low",
            "vector": "CVSS:3.1/AV:N/AC:H/PR:N/UI:R/S:U/C:L/I:L/A:N",
            "confidence": "High"
        },
        "missing_referrer_policy": {
            "score": 3.1,
            "severity": "Low",
            "vector": "CVSS:3.1/AV:N/AC:H/PR:N/UI:R/S:U/C:L/I:N/A:N",
            "confidence": "High"
        },
        "cookie_not_secure": {
            "score": 5.3,
            "severity": "Medium",
            "vector": "CVSS:3.1/AV:N/AC:H/PR:N/UI:R/S:U/C:H/I:N/A:N",
            "confidence": "High"
        },
        "cookie_not_httponly": {
            "score": 5.3,
            "severity": "Medium",
            "vector": "CVSS:3.1/AV:N/AC:H/PR:N/UI:R/S:U/C:H/I:N/A:N",
            "confidence": "High"
        },
        "cookie_not_samesite": {
            "score": 3.1,
            "severity": "Low",
            "vector": "CVSS:3.1/AV:N/AC:H/PR:N/UI:R/S:U/C:L/I:N/A:N",
            "confidence": "High"
        },
        "missing_csrf_token": {
            "score": 6.5,
            "severity": "High",
            "vector": "CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:H/A:N",
            "confidence": "Medium"
        },
        "sensitive_key_exposure": {
            "score": 7.5,
            "severity": "High",
            "vector": "CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N",
            "confidence": "High"
        },
        "sensitive_path_exposure": {
            "score": 5.3,
            "severity": "Medium",
            "vector": "CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N",
            "confidence": "Medium"
        },
        "debug_info_exposure": {
            "score": 5.3,
            "severity": "Medium",
            "vector": "CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N",
            "confidence": "High"
        },
        "insecure_http_transport": {
            "score": 7.4,
            "severity": "High",
            "vector": "CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:N",
            "confidence": "High"
        },
        "server_banner_disclosure": {
            "score": 5.3,
            "severity": "Medium",
            "vector": "CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N",
            "confidence": "High"
        }
    }

    @classmethod
    def calculate(cls, finding_key: str) -> Dict[str, Any]:
        """
        Retrieves score, qualitative severity, vector string, and default confidence.
        """
        default = {
            "score": 4.0,
            "severity": "Medium",
            "vector": "CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N",
            "confidence": "Medium"
        }
        res = cls.FINDING_MAPPING.get(finding_key, default)
        return res

    @staticmethod
    def get_severity_from_score(score: float) -> str:
        if score == 0:
            return "None"
        elif 0.1 <= score <= 3.9:
            return "Low"
        elif 4.0 <= score <= 6.9:
            return "Medium"
        elif 7.0 <= score <= 8.9:
            return "High"
        else:
            return "Critical"
