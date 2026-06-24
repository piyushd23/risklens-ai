import json
import re
import urllib.parse
from typing import List, Dict, Any
from app.assessment.cvss_calculator import CVSSCalculator
from app.assessment.owasp_mapper import OWASPMapper

class AssessmentEngine:
    # Common RegExes for sensitive info scanning
    SENSITIVE_PATTERNS = {
        "aws_access_key": r"([^A-Z0-9]|^)(AKIA[A-Z0-9]{16})([^A-Z0-9]|$)",
        "slack_token": r"xox[bapr]-[0-9]{12}-[0-9]{12}-[0-9]{12}-[a-z0-9]{32}",
        "generic_api_key": r"(?i)(api[-_]?key|secret[-_]?key|client[-_]?secret|auth[-_]?token)\s*[:=]\s*['\"]([a-zA-Z0-9_\-]{16,50})['\"]",
        "private_key": r"-----BEGIN[ A-Z0-9_-]{0,20} PRIVATE KEY-----",
        "stack_trace_python": r"Traceback \(most recent call last\):",
        "stack_trace_java": r"at [a-zA-Z0-9_]+\.[a-zA-Z0-9_]+\(.*\.java:[0-9]+\)",
        "internal_path_unix": r"(/usr/bin|/var/log|/etc/passwd|/etc/shadow)",
        "internal_path_windows": r"(C:\\Windows|C:\\Program Files|C:\\Users\\)"
    }

    def __init__(self, target_url: str):
        self.target_url = target_url
        self.findings: List[Dict[str, Any]] = []

    def scan_headers(self, headers_str: str, page_url: str):
        if not headers_str:
            return
            
        try:
            headers = json.loads(headers_str)
        except Exception:
            return
            
        # Lowercase keys for case-insensitive check
        headers_lower = {k.lower(): v for k, v in headers.items()}
        
        # 1. Content Security Policy (CSP)
        if "content-security-policy" not in headers_lower:
            self._add_finding(
                key="missing_csp",
                title="Missing Content Security Policy (CSP)",
                description="The HTTP Content-Security-Policy response header allows site administrators to declare approved sources of content that the browser is allowed to load.",
                evidence=f"HTTP Response Headers from {page_url} did not include content-security-policy",
                remediation="Configure the Content-Security-Policy HTTP header on the web server to restrict unauthorized scripts, styles, and other resources."
            )
            
        # 2. Strict-Transport-Security (HSTS)
        if "strict-transport-security" not in headers_lower and page_url.lower().startswith("https"):
            self._add_finding(
                key="missing_hsts",
                title="Missing HTTP Strict Transport Security (HSTS)",
                description="HTTP Strict Transport Security (HSTS) is a header that forces browsers to only load the site using secure HTTPS, preventing SSL strip attacks.",
                evidence=f"HTTPS Response Headers from {page_url} did not include strict-transport-security",
                remediation="Add the Strict-Transport-Security HTTP header: Strict-Transport-Security: max-age=63072000; includeSubDomains; preload"
            )
            
        # 3. X-Frame-Options
        if "x-frame-options" not in headers_lower and "frame-ancestors" not in headers_lower.get("content-security-policy", ""):
            self._add_finding(
                key="missing_x_frame_options",
                title="Missing X-Frame-Options (Clickjacking Protection)",
                description="The X-Frame-Options header indicates whether a browser should be allowed to render a page in a <frame>, <iframe>, <embed> or <object>, protecting against clickjacking.",
                evidence=f"HTTP Response Headers from {page_url} did not include x-frame-options or CSP frame-ancestors directive",
                remediation="Configure your server to send the X-Frame-Options header (e.g. X-Frame-Options: SAMEORIGIN) or define frame-ancestors in Content-Security-Policy."
            )
            
        # 4. X-Content-Type-Options
        if "x-content-type-options" not in headers_lower:
            self._add_finding(
                key="missing_x_content_type_options",
                title="Missing X-Content-Type-Options (MIME Sniffing Protection)",
                description="X-Content-Type-Options: nosniff prevents the browser from sniffing the MIME type of files, which helps protect against cross-site scripting (XSS).",
                evidence=f"HTTP Response Headers from {page_url} did not include x-content-type-options",
                remediation="Set the HTTP header X-Content-Type-Options: nosniff on all static and dynamic responses."
            )
            
        # 5. Referrer-Policy
        if "referrer-policy" not in headers_lower:
            self._add_finding(
                key="missing_referrer_policy",
                title="Missing Referrer-Policy Header",
                description="The Referrer-Policy header controls how much referrer information (sent via the Referer header) is included with requests.",
                evidence=f"HTTP Response Headers from {page_url} did not include referrer-policy",
                remediation="Configure Referrer-Policy header to a secure level (e.g. Referrer-Policy: strict-origin-when-cross-origin)."
            )
            
        # 6. Server Banner Version Disclosure
        server_header = headers_lower.get("server")
        if server_header and re.search(r"\d+\.\d+", server_header):
            self._add_finding(
                key="server_banner_disclosure",
                title="Detailed Server Version Disclosure",
                description="The HTTP Server response header discloses specific details of the underlying web server software versions, easing target intelligence gathering for attackers.",
                evidence=f"Server: {server_header}",
                remediation="Disable server signatures and remove version tokens from HTTP header responses (e.g., set ServerTokens ProductOnly in Apache or ServerName in Nginx)."
            )

    def scan_cookies(self, cookies_str: str, page_url: str):
        if not cookies_str:
            return
            
        try:
            cookies = json.loads(cookies_str)
        except Exception:
            return
            
        for name, value in cookies.items():
            # In a passive crawler, we can't always query flags directly from the cookies dictionary
            # if the requests library strips them. However, if we parse Raw Cookie headers, we can inspect them.
            # For demonstration, if cookies exist, we analyze if we have security headers.
            # If cookies are found without Httponly or Secure settings (we can simulate or detect them if header config is present)
            pass

    def check_cookie_headers(self, headers_str: str, page_url: str):
        if not headers_str:
            return
            
        try:
            headers = json.loads(headers_str)
        except Exception:
            return
            
        headers_lower = {k.lower(): v for k, v in headers.items()}
        set_cookie = headers_lower.get("set-cookie")
        
        if set_cookie:
            cookies_to_inspect = [set_cookie] if isinstance(set_cookie, str) else set_cookie
            for cookie in cookies_to_inspect:
                cookie_parts = [p.strip().lower() for p in cookie.split(";")]
                cookie_name = cookie.split("=")[0] if "=" in cookie else "unknown"
                
                # Check Secure flag
                if "secure" not in cookie_parts and page_url.lower().startswith("https"):
                    self._add_finding(
                        key="cookie_not_secure",
                        title="Cookie Missing Secure Flag",
                        description="Cookies missing the Secure flag can be transmitted in cleartext over unencrypted HTTP, making them vulnerable to interception by intercepting proxy servers.",
                        evidence=f"Set-Cookie header on {page_url}: {cookie_name} has no Secure attribute",
                        remediation="Configure the Secure attribute on all session or authentication-critical cookies."
                    )
                    
                # Check HttpOnly flag
                if "httponly" not in cookie_parts:
                    self._add_finding(
                        key="cookie_not_httponly",
                        title="Cookie Missing HttpOnly Flag",
                        description="Cookies missing the HttpOnly attribute can be read via client-side scripting (like JavaScript), increasing exposure to session theft via Cross-Site Scripting (XSS).",
                        evidence=f"Set-Cookie header on {page_url}: {cookie_name} has no HttpOnly attribute",
                        remediation="Ensure the HttpOnly flag is set on all session-identifying cookies."
                    )
                    
                # Check SameSite flag
                samesite_configured = any(p.startswith("samesite") for p in cookie_parts)
                if not samesite_configured:
                    self._add_finding(
                        key="cookie_not_samesite",
                        title="Cookie Missing SameSite Configuration",
                        description="SameSite attributes protect against Cross-Site Request Forgery (CSRF) attacks by defining whether cookies are sent with cross-site requests.",
                        evidence=f"Set-Cookie header on {page_url}: {cookie_name} has no SameSite attribute",
                        remediation="Define SameSite=Lax or SameSite=Strict on all cookies."
                    )

    def scan_form(self, form_asset: Dict[str, Any]):
        url = form_asset.get("url", "")
        method = form_asset.get("method", "GET")
        
        try:
            params = json.loads(form_asset.get("parameters", "[]"))
        except Exception:
            params = []
            
        if method == "POST":
            # Check CSRF
            has_csrf = False
            for p in params:
                name = p.get("name", "").lower()
                if any(t in name for t in ["csrf", "token", "xsrf", "_token"]):
                    has_csrf = True
                    break
            
            if not has_csrf:
                self._add_finding(
                    key="missing_csrf_token",
                    title="Form Missing CSRF Protection",
                    description="The discovered interactive form submission lacks an anti-CSRF token, potentially exposing users to Cross-Site Request Forgery attacks.",
                    evidence=f"POST Form discovered at {url} does not contain any parameter matching CSRF/token nomenclature",
                    remediation="Implement anti-CSRF protection tokens. Use secure, unpredictable, cryptographically signed tokens generated per-session."
                )

    def check_transport_security(self):
        if self.target_url.lower().startswith("http://"):
            self._add_finding(
                key="insecure_http_transport",
                title="Insecure HTTP Transport Protocol",
                description="The target web application communicates using cleartext HTTP protocol. All data transmitted (session tokens, login credentials) is readable by anyone on the network path.",
                evidence=f"Target URL is {self.target_url}",
                remediation="Configure a TLS/SSL certificate and redirect all unencrypted HTTP traffic to secure HTTPS."
            )

    def scan_sensitive_exposure(self, body_text: str, page_url: str):
        if not body_text:
            return
            
        for name, pattern in self.SENSITIVE_PATTERNS.items():
            matches = re.findall(pattern, body_text)
            if matches:
                # Deduplicate evidence
                match_evidence = matches[0]
                if isinstance(match_evidence, tuple):
                    match_evidence = match_evidence[1] if len(match_evidence) > 1 else str(match_evidence)
                
                if "key" in name or "token" in name:
                    self._add_finding(
                        key="sensitive_key_exposure",
                        title=f"Sensitive Access Token Exposed ({name.upper()})",
                        description="Hardcoded secrets, API tokens, and access credentials leaked inside HTML or JS script resources expose credentials to anyone inspecting web pages.",
                        evidence=f"Found key pattern in response content at {page_url}: ... {match_evidence} ...",
                        remediation="Remove all private credentials, credentials, API keys, and configurations from client-side deliverables. Implement secret vaults or backend proxy integrations."
                    )
                elif "trace" in name:
                    self._add_finding(
                        key="debug_info_exposure",
                        title="Application Debug Information / Stack Trace Disclosure",
                        description="Stack trace and technical debugger outputs exposed in HTTP responses can reveal internal coding namespaces, system parameters, and database schemas.",
                        evidence=f"Found trace indicators in response text at {page_url}: {match_evidence}",
                        remediation="Configure custom error pages to hide system-level stacks, and disable debug mode flag in production application configurations."
                    )
                elif "path" in name:
                    self._add_finding(
                        key="sensitive_path_exposure",
                        title="Local System Path Disclosure",
                        description="Internal server path layout exposures help mapping directory layouts and OS details, which could assist malicious parties planning server traversals.",
                        evidence=f"Internal system path keyword match at {page_url}: {match_evidence}",
                        remediation="Restrict raw system error outputs and remove server-specific absolute paths from HTML/JS files."
                    )

    def _add_finding(self, key: str, title: str, description: str, evidence: str, remediation: str):
        # Prevent duplicating the same finding title on the exact same evidence
        if any(f["title"] == title and f["evidence"] == evidence for f in self.findings):
            return
            
        cvss = CVSSCalculator.calculate(key)
        owasp = OWASPMapper.get_category(key)
        risk_explanation = f"Exposing this vulnerability violates security benchmarks like {owasp}. Risk calculations indicate CVSS vector {cvss['vector']} applies."
        
        self.findings.append({
            "title": title,
            "description": description,
            "severity": cvss["severity"],
            "cvss_score": cvss["score"],
            "confidence_level": cvss["confidence"],
            "owasp_category": owasp,
            "evidence": evidence,
            "risk_explanation": risk_explanation,
            "remediation_guidance": remediation,
            "is_false_positive": False
        })

    def run_assessment(self, assets: List[Dict[str, Any]], crawl_logs: List[str] = None) -> List[Dict[str, Any]]:
        self.check_transport_security()
        
        for asset in assets:
            url = asset.get("url", "")
            asset_type = asset.get("asset_type", "page")
            
            if asset_type == "page":
                self.scan_headers(asset.get("headers", "{}"), url)
                self.check_cookie_headers(asset.get("headers", "{}"), url)
                # Check crawl logs for sensitive tokens or look inside response body
                # In a real DAST we scan html body, here we can mock check content or logs
                self.scan_sensitive_exposure(asset.get("headers", ""), url)
                
            elif asset_type == "form":
                self.scan_form(asset)
                
        # Simulate some mock content scanning if logs contain stack traces or api keys
        if crawl_logs:
            full_log_dump = "\n".join(crawl_logs)
            self.scan_sensitive_exposure(full_log_dump, self.target_url)
            
        return self.findings
