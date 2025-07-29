from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime

from ..core.security import get_current_user
from ..models.user import User
from ..models.task import Task, TaskStatus
from ..schemas.task import TaskCreate, TaskResponse, TaskStatusUpdate, TaskUpdate
from ..db.session import get_db

router = APIRouter()

@router.put("/{task_id}", response_model=TaskResponse)
async def update_task(
    task_id: int,
    task_update: TaskUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update an existing task"""
    # Get existing task
    db_task = db.query(Task).filter(Task.id == task_id).first()
    if not db_task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )
    
    # Check if user has permission (creator or assignee)
    if db_task.creator_id != current_user.id and db_task.assignee_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to update this task"
        )
    
    # Verify assignee exists if provided
    if task_update.assignee_id:
        assignee = db.query(User).filter(User.id == task_update.assignee_id).first()
        if not assignee:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Specified assignee does not exist"
            )
    
    # Update task fields
    for field, value in task_update.dict(exclude_unset=True).items():
        setattr(db_task, field, value)
    
    db.commit()
    db.refresh(db_task)
    return db_task

@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_task(
    task_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Delete a task"""
    # Get existing task
    db_task = db.query(Task).filter(Task.id == task_id).first()
    if not db_task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )
    
    # Check if user has permission (only creator can delete)
    if db_task.creator_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to delete this task"
        )
    
    db.delete(db_task)
    db.commit()
    return None

@router.post("", response_model=TaskResponse)
async def create_task(
    task_data: TaskCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a new task"""
    # Create task instance
    db_task = Task(
        title=task_data.title,
        description=task_data.description,
        priority=task_data.priority,
        due_date=task_data.due_date,
        creator_id=current_user.id,
        assignee_id=task_data.assignee_id
    )
    
    # Verify assignee exists if provided
    if task_data.assignee_id:
        assignee = db.query(User).filter(User.id == task_data.assignee_id).first()
        if not assignee:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Specified assignee does not exist"
            )
    
    db.add(db_task)
    db.commit()
    db.refresh(db_task)
    return db_task

@router.get("/me", response_model=List[TaskResponse])
async def get_my_tasks(
    status: TaskStatus = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get all tasks assigned to the current user"""
    query = db.query(Task).filter(Task.assignee_id == current_user.id)
    
    if status:
        query = query.filter(Task.status == status)
    
    return query.order_by(Task.created_at.desc()).all()

@router.put("/{task_id}/status", response_model=TaskResponse)
async def update_task_status(
    task_id: int,
    status_update: TaskStatusUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update a task's status"""
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )
    
    # Check if user has permission to update the task
    if task.assignee_id != current_user.id and task.creator_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to update this task"
        )
    
    task.status = status_update.status
    task.updated_at = datetime.utcnow()
    
    db.commit()
    db.refresh(task)
    return task

@router.get("/{task_id}", response_model=TaskResponse)
async def get_task(
    task_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get a specific task by ID"""
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )
    return task
