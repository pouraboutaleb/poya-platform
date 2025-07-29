from sqlalchemy import Boolean, Column, Integer, String, Table, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

# Many-to-many association table for user roles
user_roles = Table(
    "user_roles",
    Base.metadata,
    Column("user_id", Integer, ForeignKey("users.id")),
    Column("role_id", Integer, ForeignKey("roles.id")),
)

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    full_name = Column(String)
    hashed_password = Column(String)
    is_active = Column(Boolean, default=True)
    
    # Relationship with roles
    roles = relationship("Role", secondary=user_roles, back_populates="users")
    
    # Relationships with tasks
    assigned_tasks = relationship("Task", foreign_keys="[Task.assignee_id]", back_populates="assignee")
    created_tasks = relationship("Task", foreign_keys="[Task.creator_id]", back_populates="creator")
    
    # Warehouse related fields
    is_warehouse_staff = Column(Boolean, default=False)
    warehouse_requests = relationship("WarehouseRequest", back_populates="created_by")
    orders = relationship("Order", back_populates="created_by")

class Role(Base):
    __tablename__ = "roles"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    description = Column(String)
    
    # Relationship with users
    users = relationship("User", secondary=user_roles, back_populates="roles")
