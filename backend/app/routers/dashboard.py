from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import User
from app.schemas import DashboardStats
from app.auth import RoleChecker
from app.services.analytics_service import AnalyticsService

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])

@router.get("/stats", response_model=DashboardStats)
def get_dashboard_statistics(db: Session = Depends(get_db),
                             current_user: User = Depends(RoleChecker(allowed_roles=["ADMIN", "SECURITY_ANALYST", "DEVELOPER"]))):
    stats = AnalyticsService.get_dashboard_stats(db)
    return stats
