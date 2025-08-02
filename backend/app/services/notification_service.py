from typing import List, Optional
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import and_

from app.models.notification import Notification


class NotificationService:
    def __init__(self, db: Session):
        self.db = db

    def create_notification(
        self,
        user_id: int,
        message: str,
        type: str,
        link: Optional[str] = None
    ) -> Notification:
        """
        Create a new notification for a user.
        
        Args:
            user_id: The ID of the user to notify
            message: The notification message
            type: The type of notification (e.g., "TASK", "SYSTEM", "CHAT")
            link: Optional URL or deep link related to the notification
        """
        notification = Notification(
            user_id=user_id,
            message=message,
            type=type,
            link=link,
            is_read=False,
            created_at=datetime.utcnow()
        )
        
        self.db.add(notification)
        self.db.commit()
        self.db.refresh(notification)
        
        return notification

    def get_user_notifications(
        self,
        user_id: int,
        limit: int = 50,
        skip: int = 0,
        unread_only: bool = False
    ) -> List[Notification]:
        """Get notifications for a specific user."""
        query = self.db.query(Notification).filter(Notification.user_id == user_id)
        
        if unread_only:
            query = query.filter(Notification.is_read == False)
            
        return query.order_by(Notification.created_at.desc()).offset(skip).limit(limit).all()

    def mark_as_read(self, notification_id: int, user_id: int) -> Optional[Notification]:
        """Mark a specific notification as read."""
        notification = self.db.query(Notification).filter(
            and_(
                Notification.id == notification_id,
                Notification.user_id == user_id
            )
        ).first()
        
        if notification:
            notification.is_read = True
            notification.read_at = datetime.utcnow()
            self.db.commit()
            self.db.refresh(notification)
            
        return notification
