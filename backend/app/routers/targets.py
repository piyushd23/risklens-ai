from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
import urllib.parse
from app.database import get_db
from app.models import Target, User
from app.schemas import TargetCreate, TargetResponse
from app.auth import RoleChecker, get_current_user
from app.services.audit_service import AuditService

router = APIRouter(prefix="/targets", tags=["Targets"])

def validate_url(url: str):
    parsed = urllib.parse.urlparse(url)
    if not parsed.scheme or not parsed.netloc:
        raise HTTPException(status_code=400, detail="Invalid target URL. Must include scheme (http/https) and domain.")
    if parsed.scheme not in ["http", "https"]:
        raise HTTPException(status_code=400, detail="Unsupported protocol. Only HTTP and HTTPS are permitted.")

@router.get("/", response_model=List[TargetResponse])
def get_targets(db: Session = Depends(get_db), 
                current_user: User = Depends(RoleChecker(allowed_roles=["ADMIN", "SECURITY_ANALYST", "DEVELOPER"]))):
    return db.query(Target).all()

@router.get("/{target_id}", response_model=TargetResponse)
def get_target(target_id: int, db: Session = Depends(get_db),
               current_user: User = Depends(RoleChecker(allowed_roles=["ADMIN", "SECURITY_ANALYST", "DEVELOPER"]))):
    target = db.query(Target).filter(Target.id == target_id).first()
    if not target:
        raise HTTPException(status_code=404, detail="Target not found")
    return target

@router.post("/", response_model=TargetResponse, status_code=status.HTTP_201_CREATED)
def create_target(target_in: TargetCreate, db: Session = Depends(get_db),
                  current_user: User = Depends(RoleChecker(allowed_roles=["ADMIN", "SECURITY_ANALYST"]))):
    validate_url(target_in.url)
    
    # Check if URL already registered
    exists = db.query(Target).filter(Target.url == target_in.url).first()
    if exists:
        raise HTTPException(status_code=400, detail="Target URL already registered")
        
    target = Target(
        name=target_in.name,
        url=target_in.url,
        description=target_in.description,
        environment=target_in.environment,
        crawl_depth=target_in.crawl_depth,
        include_paths=target_in.include_paths,
        exclude_paths=target_in.exclude_paths,
        auth_type=target_in.auth_type,
        auth_config=target_in.auth_config,
        created_by=current_user.id
    )
    
    db.add(target)
    db.commit()
    db.refresh(target)
    
    AuditService.log_event(
        db,
        action="CREATE_TARGET",
        details=f"Created target '{target.name}' at URL: {target.url}",
        user_id=current_user.id,
        username=current_user.username
    )
    
    return target

@router.delete("/{target_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_target(target_id: int, db: Session = Depends(get_db),
                  current_user: User = Depends(RoleChecker(allowed_roles=["ADMIN"]))):
    target = db.query(Target).filter(Target.id == target_id).first()
    if not target:
        raise HTTPException(status_code=404, detail="Target not found")
        
    target_name = target.name
    db.delete(target)
    db.commit()
    
    AuditService.log_event(
        db,
        action="DELETE_TARGET",
        details=f"Deleted target profile '{target_name}'",
        user_id=current_user.id,
        username=current_user.username
    )
    return
