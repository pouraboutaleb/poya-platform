from typing import Optional, Dict, Any
from sqlalchemy.orm import Session
from datetime import datetime
from ..models.audit import AuditLog
from ..models.user import User


class AuditService:
    """Service for handling audit logging."""
    
    def __init__(self, db: Session):
        self.db = db
    
    def log_action(
        self,
        user_id: int,
        action: str,
        resource_type: str,
        resource_id: Optional[int] = None,
        details: Optional[Dict[str, Any]] = None,
        ip_address: Optional[str] = None
    ) -> AuditLog:
        """Log an audit action."""
        audit_log = AuditLog(
            user_id=user_id,
            action=action,
            resource_type=resource_type,
            resource_id=resource_id,
            details=details or {},
            ip_address=ip_address,
            timestamp=datetime.utcnow()
        )
        
        self.db.add(audit_log)
        self.db.commit()
        self.db.refresh(audit_log)
        
        return audit_log
    
    def log_login(self, user_id: int, ip_address: Optional[str] = None) -> AuditLog:
        """Log a user login."""
        return self.log_action(
            user_id=user_id,
            action="login",
            resource_type="auth",
            ip_address=ip_address
        )
    
    def log_logout(self, user_id: int, ip_address: Optional[str] = None) -> AuditLog:
        """Log a user logout."""
        return self.log_action(
            user_id=user_id,
            action="logout",
            resource_type="auth",
            ip_address=ip_address
        )
    
    def log_create(
        self,
        user_id: int,
        resource_type: str,
        resource_id: int,
        details: Optional[Dict[str, Any]] = None
    ) -> AuditLog:
        """Log a resource creation."""
        return self.log_action(
            user_id=user_id,
            action="create",
            resource_type=resource_type,
            resource_id=resource_id,
            details=details
        )
    
    def log_update(
        self,
        user_id: int,
        resource_type: str,
        resource_id: int,
        details: Optional[Dict[str, Any]] = None
    ) -> AuditLog:
        """Log a resource update."""
        return self.log_action(
            user_id=user_id,
            action="update",
            resource_type=resource_type,
            resource_id=resource_id,
            details=details
        )
    
    def log_delete(
        self,
        user_id: int,
        resource_type: str,
        resource_id: int,
        details: Optional[Dict[str, Any]] = None
    ) -> AuditLog:
        """Log a resource deletion."""
        return self.log_action(
            user_id=user_id,
            action="delete",
            resource_type=resource_type,
            resource_id=resource_id,
            details=details
        )
    
    def get_audit_logs(
        self,
        user_id: Optional[int] = None,
        action: Optional[str] = None,
        resource_type: Optional[str] = None,
        limit: int = 100
    ) -> list[AuditLog]:
        """Get audit logs with optional filtering."""
        query = self.db.query(AuditLog)
        
        if user_id:
            query = query.filter(AuditLog.user_id == user_id)
        if action:
            query = query.filter(AuditLog.action == action)
        if resource_type:
            query = query.filter(AuditLog.resource_type == resource_type)
        
        return query.order_by(AuditLog.timestamp.desc()).limit(limit).all()
