from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from typing import List, Dict, Any

from app.database import get_db
from app.models import User
from app.schemas import AnalyticsResponse
from app.auth import RoleChecker
from app.services.analytics_service import AnalyticsService
from app.services.powerbi_connector import PowerBIConnector

router = APIRouter(prefix="/analytics", tags=["Analytics"])

@router.get("/trends/{target_id}", response_model=List[Dict[str, Any]])
def get_trends(target_id: int, db: Session = Depends(get_db),
               current_user: User = Depends(RoleChecker(allowed_roles=["ADMIN", "SECURITY_ANALYST", "DEVELOPER"]))):
    return AnalyticsService.get_target_trends(db, target_id)

@router.get("/powerbi/findings", response_model=List[Dict[str, Any]])
def get_powerbi_findings(db: Session = Depends(get_db)):
    """
    Publicly accessible or basic auth-protected flat table for Power BI import.
    """
    return PowerBIConnector.get_findings_table(db)

@router.get("/powerbi/trends", response_model=List[Dict[str, Any]])
def get_powerbi_trends(db: Session = Depends(get_db)):
    """
    Publicly accessible or basic auth-protected flat table for Power BI import.
    """
    return PowerBIConnector.get_trends_table(db)

@router.get("/powerbi/m-query", response_model=Dict[str, str])
def get_powerbi_query(request: Request):
    """
    Returns copy-paste Power BI Power Query M scripts.
    """
    # Calculate base URL
    base_url = str(request.base_url).rstrip("/")
    m_script = PowerBIConnector.get_powerbi_m_query(base_url)
    return {"m_query": m_script}
