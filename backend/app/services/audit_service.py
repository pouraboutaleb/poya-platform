from typing import Optional
from datetime import datetime
from sqlalchemy.orm import Session

from app.models.audit import AuditLog


class AuditService:
    def __init__(self, db: Session):
        self.db = db

    def create_log(
        self,
        user_id: int,
        action: str,
        target_entity: str,
        target_id: str,
        details: Optional[dict] = None
    ) -> AuditLog:
        """
        Create a new audit log entry.
        
        Args:
            user_id: ID of the user performing the action
            action: The type of action performed (e.g., "CREATE", "UPDATE", "DELETE")
            target_entity: The entity type being acted upon (e.g., "Item", "Order")
            target_id: The ID of the entity being acted upon
            details: Optional dictionary containing additional details about the action
        """
        audit_log = AuditLog(
            user_id=user_id,
            action=action,
            target_entity=target_entity,
            target_id=target_id,
            details=details,
            timestamp=datetime.utcnow()
        )
        
        self.db.add(audit_log)
        self.db.commit()
        self.db.refresh(audit_log)
        
        return audit_log
