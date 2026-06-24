from sqlalchemy.orm import Session
from app.models import AuditLog
from typing import Optional

class AuditService:
    @staticmethod
    def log_event(db: Session, action: str, details: Optional[str] = None, 
                  user_id: Optional[int] = None, username: Optional[str] = None,
                  ip_address: Optional[str] = None):
        """
        Creates and saves a new audit log record.
        """
        try:
            log_entry = AuditLog(
                user_id=user_id,
                username=username,
                action=action,
                details=details,
                ip_address=ip_address
            )
            db.add(log_entry)
            db.commit()
        except Exception as e:
            # Prevent audit logging failures from crashing main API flows
            db.rollback()
            print(f"Failed to write audit log: {e}")
