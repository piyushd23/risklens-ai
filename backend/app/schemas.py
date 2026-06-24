from datetime import datetime
from typing import List, Optional, Any
from pydantic import BaseModel, EmailStr, Field

# Token Schemas
class Token(BaseModel):
    access_token: str
    token_type: str
    role: str
    username: str

class TokenData(BaseModel):
    username: Optional[str] = None
    role: Optional[str] = None

class RefreshTokenRequest(BaseModel):
    refresh_token: str

# Role Schemas
class RoleBase(BaseModel):
    name: str
    description: Optional[str] = None

class RoleResponse(RoleBase):
    id: int
    class Config:
        from_attributes = True

# User Schemas
class UserBase(BaseModel):
    username: str
    email: EmailStr

class UserCreate(UserBase):
    password: str
    role_id: int

class UserResponse(UserBase):
    id: int
    role_id: int
    is_active: bool
    created_at: datetime
    role: Optional[RoleResponse] = None

    class Config:
        from_attributes = True

class UserLogin(BaseModel):
    username: str
    password: str

# Target Schemas
class TargetBase(BaseModel):
    name: str
    url: str
    description: Optional[str] = None
    environment: str = "Production"
    crawl_depth: int = 3
    include_paths: Optional[str] = None
    exclude_paths: Optional[str] = None
    auth_type: str = "None"
    auth_config: Optional[str] = None # JSON string

class TargetCreate(TargetBase):
    pass

class TargetResponse(TargetBase):
    id: int
    created_by: int
    created_at: datetime

    class Config:
        from_attributes = True

# Asset Schemas
class AssetBase(BaseModel):
    url: str
    asset_type: str
    method: str
    parameters: Optional[str] = None
    headers: Optional[str] = None
    cookies: Optional[str] = None

class AssetResponse(AssetBase):
    id: int
    target_id: int
    discovered_at: datetime

    class Config:
        from_attributes = True

# Risk Score Schemas
class RiskScoreResponse(BaseModel):
    id: int
    finding_id: int
    priority_score: float
    recommended_action: Optional[str] = None
    remediation_priority: str
    model_version: str

    class Config:
        from_attributes = True

# Finding Schemas
class FindingBase(BaseModel):
    title: str
    description: str
    severity: str
    cvss_score: float
    confidence_level: str
    owasp_category: str
    evidence: Optional[str] = None
    risk_explanation: Optional[str] = None
    remediation_guidance: Optional[str] = None
    is_false_positive: bool = False

class FindingResponse(FindingBase):
    id: int
    assessment_id: int
    discovered_at: datetime
    risk_score: Optional[RiskScoreResponse] = None

    class Config:
        from_attributes = True

# Assessment Schemas
class AssessmentBase(BaseModel):
    target_id: int

class AssessmentCreate(AssessmentBase):
    pass

class AssessmentResponse(AssessmentBase):
    id: int
    status: str
    progress: int
    log_data: Optional[str] = None
    started_at: datetime
    completed_at: Optional[datetime] = None
    created_by: int
    target: Optional[TargetResponse] = None

    class Config:
        from_attributes = True

# Report Schemas
class ReportResponse(BaseModel):
    id: int
    assessment_id: int
    name: str
    report_type: str
    file_path: str
    created_by: int
    created_at: datetime

    class Config:
        from_attributes = True

# Analytics Schemas
class AnalyticsResponse(BaseModel):
    id: int
    target_id: int
    security_score: float
    compliance_score: float
    total_vulns: int
    critical_vulns: int
    high_vulns: int
    medium_vulns: int
    low_vulns: int
    calculated_at: datetime

    class Config:
        from_attributes = True

# Audit Log Schemas
class AuditLogResponse(BaseModel):
    id: int
    user_id: Optional[int] = None
    username: Optional[str] = None
    action: str
    details: Optional[str] = None
    ip_address: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True

# Notification Schemas
class NotificationResponse(BaseModel):
    id: int
    user_id: int
    message: str
    is_read: bool
    created_at: datetime

    class Config:
        from_attributes = True

# Dashboard Stats Schemas
class DashboardStats(BaseModel):
    total_targets: int
    total_scans: int
    total_findings: int
    overall_security_score: float
    overall_compliance_score: float
    severity_distribution: dict
    owasp_distribution: dict
    recent_scans: List[AssessmentResponse]
    recent_findings: List[FindingResponse]
