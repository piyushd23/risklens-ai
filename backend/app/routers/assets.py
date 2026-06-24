from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.models import Asset, User
from app.schemas import AssetResponse
from app.auth import RoleChecker

router = APIRouter(prefix="/assets", tags=["Assets"])

@router.get("/target/{target_id}", response_model=List[AssetResponse])
def get_target_assets(target_id: int, db: Session = Depends(get_db),
                      current_user: User = Depends(RoleChecker(allowed_roles=["ADMIN", "SECURITY_ANALYST", "DEVELOPER"]))):
    assets = db.query(Asset).filter(Asset.target_id == target_id).all()
    return assets
