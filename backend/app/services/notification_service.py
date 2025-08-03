from typing import Optional, List
from sqlalchemy.orm import Session
from ..models.user import User
from ..models.notification import Notification


class NotificationService:
    """Service for handling notifications."""
    
    def __init__(self, db: Session):
        self.db = db
    
    def create_notification(
        self,
        user_id: int,
        title: str,
        message: str,
        type: str = "info",
        data: Optional[dict] = None
    ) -> Notification:
        """Create a new notification for a user."""
        notification = Notification(
            user_id=user_id,
            title=title,
            message=message,
            type=type,
            data=data or {}
        )
        
        self.db.add(notification)
        self.db.commit()
        self.db.refresh(notification)
        
        return notification
    
    def get_user_notifications(
        self,
        user_id: int,
        unread_only: bool = False,
        limit: int = 50
    ) -> List[Notification]:
        """Get notifications for a user."""
        query = self.db.query(Notification).filter(Notification.user_id == user_id)
        
        if unread_only:
            query = query.filter(Notification.is_read == False)
        
        return query.order_by(Notification.created_at.desc()).limit(limit).all()
    
    def mark_as_read(self, notification_id: int, user_id: int) -> bool:
        """Mark a notification as read."""
        notification = self.db.query(Notification).filter(
            Notification.id == notification_id,
            Notification.user_id == user_id
        ).first()
        
        if notification:
            notification.is_read = True
            self.db.commit()
            return True
        
        return False
    
    def mark_all_as_read(self, user_id: int) -> int:
        """Mark all notifications as read for a user."""
        count = self.db.query(Notification).filter(
            Notification.user_id == user_id,
            Notification.is_read == False
        ).update({"is_read": True})
        
        self.db.commit()
        return count
    
    def delete_notification(self, notification_id: int, user_id: int) -> bool:
        """Delete a notification."""
        notification = self.db.query(Notification).filter(
            Notification.id == notification_id,
            Notification.user_id == user_id
        ).first()
        
        if notification:
            self.db.delete(notification)
            self.db.commit()
            return True
        
        return False
    
    def send_system_notification(
        self,
        title: str,
        message: str,
        user_ids: Optional[List[int]] = None,
        role_names: Optional[List[str]] = None
    ) -> List[Notification]:
        """Send a system notification to multiple users."""
        notifications = []
        
        # Get target users
        if user_ids:
            users = self.db.query(User).filter(User.id.in_(user_ids)).all()
        elif role_names:
            users = self.db.query(User).join(User.roles).filter(
                User.roles.any(name__in=role_names)
            ).all()
        else:
            # Send to all active users
            users = self.db.query(User).filter(User.is_active == True).all()
        
        # Create notifications
        for user in users:
            notification = self.create_notification(
                user_id=user.id,
                title=title,
                message=message,
                type="system"
            )
            notifications.append(notification)
        
        return notifications
