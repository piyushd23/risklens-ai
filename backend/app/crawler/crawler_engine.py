import asyncio
import urllib.parse
from bs4 import BeautifulSoup
import requests
import json
import logging
from typing import Set, Dict, List, Any, Optional


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("CrawlerEngine")

class CrawlerEngine:
    def __init__(self, target_id: int, base_url: str, crawl_depth: int = 3,
                 include_paths: str = None, exclude_paths: str = None,
                 auth_type: str = "None", auth_config: str = None):
        self.target_id = target_id
        self.base_url = base_url
        self.parsed_base = urllib.parse.urlparse(base_url)
        self.max_depth = crawl_depth
        self.auth_type = auth_type
        
        # Parse configurations
        self.include_paths = [p.strip() for p in include_paths.split(",")] if include_paths else []
        self.exclude_paths = [p.strip() for p in exclude_paths.split(",")] if exclude_paths else []
        
        self.auth_data = {}
        if auth_config:
            try:
                self.auth_data = json.loads(auth_config)
            except Exception as e:
                logger.error(f"Error parsing auth config: {e}")

        self.session = requests.Session()
        self.visited_urls: Set[str] = set()
        self.discovered_assets: List[Dict[str, Any]] = []
        self.logs: List[str] = []

        self._setup_authentication()

    def log(self, message: str):
        msg = f"[{self.base_url}] {message}"
        logger.info(msg)
        self.logs.append(msg)

    def _setup_authentication(self):
        # Default Headers
        self.session.headers.update({
            "User-Agent": "RiskLensAI-DefensiveCrawler/1.0",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8"
        })
        
        if self.auth_type == "Basic":
            username = self.auth_data.get("username", "")
            password = self.auth_data.get("password", "")
            self.session.auth = (username, password)
            self.log("Authenticated using HTTP Basic Authentication")
            
        elif self.auth_type == "Bearer":
            token = self.auth_data.get("token", "")
            if token:
                self.session.headers.update({"Authorization": f"Bearer {token}"})
                self.log("Authenticated using Bearer token")
                
        elif self.auth_type == "Form":
            login_url = self.auth_data.get("login_url", "")
            username_field = self.auth_data.get("username_field", "username")
            password_field = self.auth_data.get("password_field", "password")
            username_val = self.auth_data.get("username", "")
            password_val = self.auth_data.get("password", "")
            
            if login_url and username_val:
                try:
                    payload = {username_field: username_val, password_field: password_val}
                    # Add additional form fields if specified
                    extra = self.auth_data.get("extra_fields", {})
                    payload.update(extra)
                    
                    res = self.session.post(login_url, data=payload, timeout=10)
                    self.log(f"Form Login completed with status: {res.status_code}")
                except Exception as e:
                    self.log(f"Failed form authentication: {e}")

    def is_in_scope(self, url: str) -> bool:
        parsed = urllib.parse.urlparse(url)
        # Check domain match
        if parsed.netloc and parsed.netloc != self.parsed_base.netloc:
            return False
            
        # Check path exclusion
        path = parsed.path
        for exp in self.exclude_paths:
            if exp and exp in path:
                return False
                
        # Check path inclusion
        if self.include_paths:
            in_scope = False
            for inp in self.include_paths:
                if inp and inp in path:
                    in_scope = True
                    break
            if not in_scope:
                return False
                
        return True

    def clean_url(self, url: str) -> str:
        # Strip anchors/fragments
        parsed = urllib.parse.urlparse(url)
        cleaned = parsed._replace(fragment="").geturl()
        return cleaned

    def fetch_url(self, url: str) -> Optional[requests.Response]:
        try:
            res = self.session.get(url, timeout=10, allow_redirects=True)
            return res
        except Exception as e:
            self.log(f"Error requesting {url}: {e}")
            return None

    def crawl_sync(self):
        self.log(f"Starting discovery crawl for root {self.base_url}")
        queue = [(self.base_url, 0)] # (url, depth)
        
        while queue:
            current_url, depth = queue.pop(0)
            cleaned = self.clean_url(current_url)
            
            if cleaned in self.visited_urls:
                continue
                
            self.visited_urls.add(cleaned)
            self.log(f"Crawling (Depth {depth}): {cleaned}")
            
            res = self.fetch_url(cleaned)
            if not res:
                continue

            # Record page as asset
            headers_dict = dict(res.headers)
            cookies_dict = dict(res.cookies)
            self.discovered_assets.append({
                "url": cleaned,
                "asset_type": "page",
                "method": "GET",
                "parameters": json.dumps(list(urllib.parse.parse_qs(urllib.parse.urlparse(cleaned).query).keys())),
                "headers": json.dumps(headers_dict),
                "cookies": json.dumps(cookies_dict)
            })

            # Check content type - only crawl HTML
            content_type = res.headers.get("Content-Type", "")
            if "text/html" not in content_type:
                continue
                
            soup = BeautifulSoup(res.text, "html.parser")
            
            # Find Forms
            for form in soup.find_all("form"):
                action = form.get("action", "")
                method = form.get("method", "GET").upper()
                form_url = urllib.parse.urljoin(cleaned, action)
                
                inputs = []
                for inp in form.find_all(["input", "textarea", "select"]):
                    name = inp.get("name")
                    inp_type = inp.get("type", "text")
                    if name:
                        inputs.append({"name": name, "type": inp_type})
                        
                if self.is_in_scope(form_url):
                    self.discovered_assets.append({
                        "url": self.clean_url(form_url),
                        "asset_type": "form",
                        "method": method,
                        "parameters": json.dumps(inputs),
                        "headers": json.dumps({}),
                        "cookies": json.dumps({})
                    })

            # Find Links (only crawl up to max depth)
            if depth < self.max_depth:
                for link in soup.find_all("a", href=True):
                    href = link.get("href")
                    joined_url = urllib.parse.urljoin(cleaned, href)
                    if self.is_in_scope(joined_url):
                        queue.append((joined_url, depth + 1))

        self.log(f"Crawl completed. Visited {len(self.visited_urls)} page URLs.")

    async def crawl(self):
        # Wrap the sync crawler in asyncio thread executor to avoid blocking FastAPI
        await asyncio.to_thread(self.crawl_sync)
        return self.discovered_assets, self.logs
