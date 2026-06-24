from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.models import User, Role
from app.schemas import UserResponse, RoleResponse
from app.auth import RoleChecker, get_current_user

router = APIRouter(prefix="/users", tags=["Users"])

@router.get("/", response_model=List[UserResponse])
def get_users(db: Session = Depends(get_db), 
              current_user: User = Depends(RoleChecker(allowed_roles=["ADMIN"]))):
    return db.query(User).all()

@router.get("/roles", response_model=List[RoleResponse])
def get_roles(db: Session = Depends(get_db)):
    return db.query(Role).all()
