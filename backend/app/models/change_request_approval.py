from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, JSON, Enum, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum
from ..db.base_class import Base

class ApprovalLevel(str, enum.Enum):
    QC_MANAGER = "qc_manager"
    PRODUCTION_MANAGER = "production_manager"
    TECHNICAL_MANAGER = "technical_manager"

class ApprovalStatus(str, enum.Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"

class ApprovalType(str, enum.Enum):
    CHANGE_ADDENDUM = "change_addendum"
    SCRAP_REQUEST = "scrap_request"
    SPECIAL_REQUEST = "special_request"

class ChangeRequestApproval(Base):
    __tablename__ = "change_request_approval"

    id = Column(Integer, primary_key=True, index=True)
    
    # Request metadata
    request_type = Column(Enum(ApprovalType), nullable=False)
    warehouse_request_id = Column(Integer, ForeignKey("warehouse_request.id"), nullable=False)
    submitted_by_id = Column(Integer, ForeignKey("user.id"), nullable=False)
    submitted_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Request details
    description = Column(String, nullable=False)
    attachments = Column(JSON)  # Array of file URLs
    impact_analysis = Column(String)
    technical_justification = Column(String)
    
    # Approvals tracking
    qc_approval = Column(JSON, default={
        "status": "pending",
        "approved_by": None,
        "approved_at": None,
        "comments": None
    })
    production_approval = Column(JSON, default={
        "status": "pending",
        "approved_by": None,
        "approved_at": None,
        "comments": None
    })
    technical_approval = Column(JSON, default={
        "status": "pending",
        "approved_by": None,
        "approved_at": None,
        "comments": None
    })
    
    # Overall status
    is_completed = Column(Boolean, default=False)
    is_approved = Column(Boolean, default=False)
    completed_at = Column(DateTime(timezone=True))
    
    # Relationships
    warehouse_request = relationship("WarehouseRequest", back_populates="change_approvals")
    submitted_by = relationship("User", foreign_keys=[submitted_by_id])
    
    def update_approval(self, level: ApprovalLevel, user_id: int, status: ApprovalStatus, comments: str = None):
        """Update approval status for a specific level"""
        approval_data = {
            "status": status,
            "approved_by": user_id,
            "approved_at": func.now(),
            "comments": comments
        }
        
        if level == ApprovalLevel.QC_MANAGER:
            self.qc_approval = approval_data
        elif level == ApprovalLevel.PRODUCTION_MANAGER:
            self.production_approval = approval_data
        elif level == ApprovalLevel.TECHNICAL_MANAGER:
            self.technical_approval = approval_data
            
        # Check if all approvals are complete
        all_approvals = [self.qc_approval, self.production_approval, self.technical_approval]
        all_completed = all(a.get("status") != "pending" for a in all_approvals)
        all_approved = all(a.get("status") == "approved" for a in all_approvals)
        
        if all_completed:
            self.is_completed = True
            self.is_approved = all_approved
            self.completed_at = func.now()
