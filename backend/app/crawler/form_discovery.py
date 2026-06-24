from bs4 import BeautifulSoup
from typing import List, Dict, Any

class FormDiscovery:
    @staticmethod
    def extract_forms(html_content: str, page_url: str) -> List[Dict[str, Any]]:
        soup = BeautifulSoup(html_content, "html.parser")
        forms = []
        
        for idx, form_tag in enumerate(soup.find_all("form")):
            action = form_tag.get("action", "")
            method = form_tag.get("method", "GET").upper()
            form_id = form_tag.get("id", f"form_{idx}")
            form_name = form_tag.get("name", "")
            
            inputs = []
            has_csrf_token = False
            csrf_token_name = ""
            
            for input_tag in form_tag.find_all(["input", "textarea", "select"]):
                name = input_tag.get("name")
                input_type = input_tag.get("type", "text").lower()
                value = input_tag.get("value", "")
                
                if name:
                    # Detect potential CSRF tokens
                    is_token = any(term in name.lower() for term in ["csrf", "token", "xsrf", "_token"])
                    if is_token or (input_type == "hidden" and len(value) > 20):
                        has_csrf_token = True
                        csrf_token_name = name
                        
                    inputs.append({
                        "name": name,
                        "type": input_type,
                        "required": input_tag.has_attr("required"),
                        "value": value[:100] if value else "" # Limit logged content
                    })
                    
            forms.append({
                "form_id": form_id,
                "form_name": form_name,
                "action": action,
                "method": method,
                "inputs": inputs,
                "has_csrf_token": has_csrf_token,
                "csrf_token_name": csrf_token_name,
                "source_page": page_url
            })
            
        return forms
