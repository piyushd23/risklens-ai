from datetime import datetime
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Float, ForeignKey, Text
from sqlalchemy.orm import relationship
from app.database import Base

class Role(Base):
    __tablename__ = "roles"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True, nullable=False)
    description = Column(String, nullable=True)

    users = relationship("User", back_populates="role")

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    role_id = Column(Integer, ForeignKey("roles.id"), nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    role = relationship("Role", back_populates="users")
    audit_logs = relationship("AuditLog", back_populates="user")
    notifications = relationship("Notification", back_populates="user")

class Target(Base):
    __tablename__ = "targets"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True, nullable=False)
    url = Column(String, nullable=False)
    description = Column(String, nullable=True)
    environment = Column(String, default="Production") # Production, Staging, Development
    crawl_depth = Column(Integer, default=3)
    include_paths = Column(Text, nullable=True) # comma-separated or json
    exclude_paths = Column(Text, nullable=True) # comma-separated or json
    auth_type = Column(String, default="None") # None, Basic, Bearer, Form
    auth_config = Column(Text, nullable=True) # JSON configuration string
    created_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    assets = relationship("Asset", back_populates="target", cascade="all, delete-orphan")
    assessments = relationship("Assessment", back_populates="target", cascade="all, delete-orphan")
    analytics = relationship("Analytics", back_populates="target", cascade="all, delete-orphan")

class Asset(Base):
    __tablename__ = "assets"

    id = Column(Integer, primary_key=True, index=True)
    target_id = Column(Integer, ForeignKey("targets.id"), nullable=False)
    url = Column(String, nullable=False)
    asset_type = Column(String, nullable=False) # page, link, form, input_field, query_param, post_param
    method = Column(String, default="GET")
    parameters = Column(Text, nullable=True) # JSON representation of keys/types
    headers = Column(Text, nullable=True) # JSON response headers
    cookies = Column(Text, nullable=True) # JSON response cookies
    discovered_at = Column(DateTime, default=datetime.utcnow)

    target = relationship("Target", back_populates="assets")

class Assessment(Base):
    __tablename__ = "assessments"

    id = Column(Integer, primary_key=True, index=True)
    target_id = Column(Integer, ForeignKey("targets.id"), nullable=False)
    status = Column(String, default="PENDING") # PENDING, CRAWLING, ASSESSING, COMPLETED, FAILED
    progress = Column(Integer, default=0) # 0 to 100
    log_data = Column(Text, nullable=True) # JSON list or text logs
    started_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)
    created_by = Column(Integer, ForeignKey("users.id"), nullable=False)

    target = relationship("Target", back_populates="assessments")
    findings = relationship("Finding", back_populates="assessment", cascade="all, delete-orphan")
    reports = relationship("Report", back_populates="assessment", cascade="all, delete-orphan")

class Finding(Base):
    __tablename__ = "findings"

    id = Column(Integer, primary_key=True, index=True)
    assessment_id = Column(Integer, ForeignKey("assessments.id"), nullable=False)
    title = Column(String, nullable=False)
    description = Column(Text, nullable=False)
    severity = Column(String, nullable=False) # Critical, High, Medium, Low
    cvss_score = Column(Float, default=0.0)
    confidence_level = Column(String, default="Medium") # High, Medium, Low
    owasp_category = Column(String, nullable=False)
    evidence = Column(Text, nullable=True)
    risk_explanation = Column(Text, nullable=True)
    remediation_guidance = Column(Text, nullable=True)
    is_false_positive = Column(Boolean, default=False)
    discovered_at = Column(DateTime, default=datetime.utcnow)

    assessment = relationship("Assessment", back_populates="findings")
    risk_score = relationship("RiskScore", uselist=False, back_populates="finding", cascade="all, delete-orphan")

class Report(Base):
    __tablename__ = "reports"

    id = Column(Integer, primary_key=True, index=True)
    assessment_id = Column(Integer, ForeignKey("assessments.id"), nullable=False)
    name = Column(String, nullable=False)
    report_type = Column(String, nullable=False) # pdf, html, json
    file_path = Column(String, nullable=False)
    created_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    assessment = relationship("Assessment", back_populates="reports")

class Analytics(Base):
    __tablename__ = "analytics"

    id = Column(Integer, primary_key=True, index=True)
    target_id = Column(Integer, ForeignKey("targets.id"), nullable=False)
    security_score = Column(Float, default=100.0) # 0 to 100
    compliance_score = Column(Float, default=100.0) # 0 to 100
    total_vulns = Column(Integer, default=0)
    critical_vulns = Column(Integer, default=0)
    high_vulns = Column(Integer, default=0)
    medium_vulns = Column(Integer, default=0)
    low_vulns = Column(Integer, default=0)
    calculated_at = Column(DateTime, default=datetime.utcnow)

    target = relationship("Target", back_populates="analytics")

class RiskScore(Base):
    __tablename__ = "risk_scores"

    id = Column(Integer, primary_key=True, index=True)
    finding_id = Column(Integer, ForeignKey("findings.id"), nullable=False)
    priority_score = Column(Float, default=0.0) # AI calculated priority score (e.g. 0-100)
    recommended_action = Column(String, nullable=True)
    remediation_priority = Column(String, default="Medium") # Critical, High, Medium, Low
    model_version = Column(String, default="1.0.0")

    finding = relationship("Finding", back_populates="risk_score")

class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    username = Column(String, nullable=True)
    action = Column(String, nullable=False) # e.g. LOGIN, START_SCAN, CREATE_TARGET, EXPORT_REPORT
    details = Column(Text, nullable=True)
    ip_address = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="audit_logs")

class Notification(Base):
    __tablename__ = "notifications"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    message = Column(String, nullable=False)
    is_read = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="notifications")
