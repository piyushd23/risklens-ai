from typing import Dict, Any

class OWASPMapper:
    OWASP_CATEGORIES = {
        "A01:2021-Broken Access Control": "Broken Access Control involves security issues where users can access resources or execute actions outside of their intended permissions.",
        "A02:2021-Cryptographic Failures": "Cryptographic Failures occur when sensitive data is transmitted in clear text, or when weak cryptographic algorithms/keys are utilized.",
        "A03:2021-Injection": "Injection vulnerabilities arise when untrusted data is sent to an interpreter as part of a command or query.",
        "A04:2021-Insecure Design": "Insecure Design represents flaws in architectural design and lack of threat modeling, including lack of CSRF tokens or token-based defenses.",
        "A05:2021-Security Misconfiguration": "Security Misconfiguration happens when security settings are not defined, implemented, or maintained properly. (e.g. missing HTTP response headers).",
        "A06:2021-Vulnerable and Outdated Components": "This refers to risk associated with using third-party components, frameworks, or dependencies that have known security flaws.",
        "A07:2021-Identification and Authentication Failures": "This covers vulnerabilities in user verification, session management (like session hijacking via missing HttpOnly cookies), and weak passwords.",
        "A08:2021-Software and Data Integrity Failures": "This category focuses on software updates, data validation, and CI/CD pipelines without integrity verification.",
        "A09:2021-Security Logging and Monitoring Failures": "This occurs when insufficient logging, reporting, or active monitoring fails to detect ongoing attacks.",
        "A10:2021-Server-Side Request Forgery": "SSRF occurs when a web application fetches a remote resource without validating the user-supplied destination URL."
    }

    FINDING_OWASP_MAP = {
        "missing_csp": "A05:2021-Security Misconfiguration",
        "missing_hsts": "A02:2021-Cryptographic Failures",
        "missing_x_frame_options": "A05:2021-Security Misconfiguration",
        "missing_x_content_type_options": "A05:2021-Security Misconfiguration",
        "missing_referrer_policy": "A05:2021-Security Misconfiguration",
        "cookie_not_secure": "A02:2021-Cryptographic Failures",
        "cookie_not_httponly": "A07:2021-Identification and Authentication Failures",
        "cookie_not_samesite": "A01:2021-Broken Access Control",
        "missing_csrf_token": "A04:2021-Insecure Design",
        "sensitive_key_exposure": "A02:2021-Cryptographic Failures",
        "sensitive_path_exposure": "A01:2021-Broken Access Control",
        "debug_info_exposure": "A05:2021-Security Misconfiguration",
        "insecure_http_transport": "A02:2021-Cryptographic Failures",
        "server_banner_disclosure": "A05:2021-Security Misconfiguration"
    }

    @classmethod
    def get_category(cls, finding_key: str) -> str:
        return cls.FINDING_OWASP_MAP.get(finding_key, "A05:2021-Security Misconfiguration")

    @classmethod
    def get_description(cls, category: str) -> str:
        return cls.OWASP_CATEGORIES.get(category, "General Security Vulnerability")
