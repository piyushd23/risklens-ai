import urllib.parse
from typing import List, Dict, Any

class EndpointMapper:
    @staticmethod
    def map_endpoints(urls: List[str]) -> Dict[str, Any]:
        """
        Groups URLs by directory structure and file extension to present a sitemap.
        """
        sitemap = {}
        for url in urls:
            parsed = urllib.parse.urlparse(url)
            path = parsed.path if parsed.path else "/"
            
            # Group by path depth
            parts = [p for p in path.split("/") if p]
            current = sitemap
            
            for part in parts:
                if part not in current:
                    current[part] = {}
                current = current[part]
                
            # Store full URL metadata in leaf if empty
            if not current:
                current["_url"] = url
                
        return sitemap

    @staticmethod
    def categorize_assets(assets: List[Dict[str, Any]]) -> Dict[str, List[Dict[str, Any]]]:
        categories = {
            "pages": [],
            "forms": [],
            "scripts": [],
            "styles": [],
            "apis": []
        }
        
        for asset in assets:
            url = asset.get("url", "")
            method = asset.get("method", "GET")
            asset_type = asset.get("asset_type", "page")
            
            if asset_type == "form":
                categories["forms"].append(asset)
            elif url.endswith(".js"):
                categories["scripts"].append(asset)
            elif url.endswith(".css"):
                categories["styles"].append(asset)
            elif "/api/" in url or method in ["POST", "PUT", "DELETE"]:
                categories["apis"].append(asset)
            else:
                categories["pages"].append(asset)
                
        return categories
