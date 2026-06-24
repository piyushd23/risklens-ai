from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import User, Role
from app.schemas import Token, UserLogin, UserCreate, UserResponse, RefreshTokenRequest
from app.auth import verify_password, create_access_token, create_refresh_token, verify_token, get_password_hash
from app.services.audit_service import AuditService

router = APIRouter(prefix="/auth", tags=["Authentication"])

@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register(user_in: UserCreate, db: Session = Depends(get_db)):
    # Check existing username
    db_user = db.query(User).filter(User.username == user_in.username).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Username already registered")
        
    # Check existing email
    db_email = db.query(User).filter(User.email == user_in.email).first()
    if db_email:
        raise HTTPException(status_code=400, detail="Email already registered")
        
    # Check if role exists
    role = db.query(Role).filter(Role.id == user_in.role_id).first()
    if not role:
        raise HTTPException(status_code=404, detail="Requested role does not exist")
        
    hashed_password = get_password_hash(user_in.password)
    user = User(
        username=user_in.username,
        email=user_in.email,
        hashed_password=hashed_password,
        role_id=user_in.role_id,
        is_active=True
    )
    
    db.add(user)
    db.commit()
    db.refresh(user)
    
    # Audit log
    AuditService.log_event(
        db, 
        action="USER_REGISTRATION", 
        details=f"Registered user: {user.username} with role {role.name}",
        user_id=user.id,
        username=user.username
    )
    
    return user

@router.post("/login", response_model=Token)
def login(credentials: UserLogin, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == credentials.username).first()
    if not user or not verify_password(credentials.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
        
    if not user.is_active:
        raise HTTPException(status_code=400, detail="User account is deactivated")
        
    role = db.query(Role).filter(Role.id == user.role_id).first()
    role_name = role.name if role else "DEVELOPER"
    
    access_token = create_access_token(data={"sub": user.username, "role": role_name})
    refresh_token = create_refresh_token(data={"sub": user.username})
    
    # Audit log
    AuditService.log_event(
        db, 
        action="USER_LOGIN", 
        details=f"User logged in successfully under role {role_name}",
        user_id=user.id,
        username=user.username
    )
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "role": role_name,
        "username": user.username
    }

@router.post("/refresh", response_model=Token)
def refresh_token(payload: RefreshTokenRequest, db: Session = Depends(get_db)):
    data = verify_token(payload.refresh_token)
    username = data.get("sub")
    
    user = db.query(User).filter(User.username == username).first()
    if not user or not user.is_active:
        raise HTTPException(status_code=401, detail="Invalid token or inactive user")
        
    role = db.query(Role).filter(Role.id == user.role_id).first()
    role_name = role.name if role else "DEVELOPER"
    
    new_access = create_access_token(data={"sub": user.username, "role": role_name})
    new_refresh = create_refresh_token(data={"sub": user.username})
    
    return {
        "access_token": new_access,
        "token_type": "bearer",
        "role": role_name,
        "username": user.username
    }
