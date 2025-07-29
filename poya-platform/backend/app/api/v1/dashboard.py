from fastapi import APIRouter, Depends
from sqlalchemy import func, distinct, and_, text
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from typing import List, Dict
from pydantic import BaseModel
from ..dependencies import get_db, get_current_user
from ..models.task import Task
from ..models.production_report import ProductionReport
from ..models.order import Order
from ..models.user import User

router = APIRouter()

class EfficiencyDataPoint(BaseModel):
    date: datetime
    average_efficiency: float

class ActiveOrdersCounts(BaseModel):
    procurement: int
    production: int

class DashboardSummary(BaseModel):
    task_summary: Dict[str, int]
    efficiency_trend: List[EfficiencyDataPoint]
    active_orders: ActiveOrdersCounts

@router.get("/summary", response_model=DashboardSummary)
async def get_dashboard_summary(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Get task summary
    task_summary = dict(
        db.query(Task.status, func.count(Task.id))
        .group_by(Task.status)
        .all()
    )

    # Get efficiency trend for last 30 days
    thirty_days_ago = datetime.utcnow() - timedelta(days=30)
    
    # Using SQL directly for more complex date handling and aggregation
    efficiency_query = text("""
        WITH daily_efficiency AS (
            SELECT 
                DATE(created_at) as date,
                AVG(efficiency_percentage) as avg_efficiency
            FROM production_reports
            WHERE created_at >= :start_date
            GROUP BY DATE(created_at)
        )
        SELECT 
            date,
            COALESCE(avg_efficiency, 0) as average_efficiency
        FROM generate_series(
            :start_date::date,
            CURRENT_DATE,
            '1 day'
        ) as dates(date)
        LEFT JOIN daily_efficiency ON daily_efficiency.date = dates.date
        ORDER BY date
    """)
    
    efficiency_results = db.execute(
        efficiency_query,
        {"start_date": thirty_days_ago}
    ).fetchall()

    efficiency_trend = [
        EfficiencyDataPoint(
            date=row[0],
            average_efficiency=float(row[1])
        )
        for row in efficiency_results
    ]

    # Get active orders counts
    active_orders = ActiveOrdersCounts(
        procurement=db.query(func.count(Order.id))
        .filter(
            and_(
                Order.type == 'procurement',
                Order.status.in_(['new', 'in_progress', 'pending_approval'])
            )
        ).scalar(),
        
        production=db.query(func.count(Order.id))
        .filter(
            and_(
                Order.type == 'production',
                Order.status.in_(['new', 'in_progress', 'pending_approval'])
            )
        ).scalar()
    )

    return DashboardSummary(
        task_summary=task_summary,
        efficiency_trend=efficiency_trend,
        active_orders=active_orders
    )

@router.get("/tasks/overview")
async def get_task_overview(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Returns task statistics formatted for the pie chart
    """
    task_counts = db.query(Task.status, func.count(Task.id))\
        .group_by(Task.status)\
        .all()
    
    # Format for the frontend pie chart
    return {
        "data": [
            {
                "name": status.replace("_", " ").title(),
                "value": count
            }
            for status, count in task_counts
        ]
    }

@router.get("/production/efficiency")
async def get_production_efficiency(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Returns last 30 days production efficiency data
    """
    thirty_days_ago = datetime.utcnow() - timedelta(days=30)
    
    efficiency_query = text("""
        WITH daily_efficiency AS (
            SELECT 
                DATE(created_at) as date,
                AVG(efficiency_percentage) as efficiency
            FROM production_reports
            WHERE created_at >= :start_date
            GROUP BY DATE(created_at)
        )
        SELECT 
            date,
            COALESCE(efficiency, 0) as efficiency
        FROM generate_series(
            :start_date::date,
            CURRENT_DATE,
            '1 day'
        ) as dates(date)
        LEFT JOIN daily_efficiency ON daily_efficiency.date = dates.date
        ORDER BY date
    """)
    
    results = db.execute(
        efficiency_query,
        {"start_date": thirty_days_ago}
    ).fetchall()
    
    return {
        "data": [
            {
                "date": row[0].isoformat(),
                "efficiency": float(row[1])
            }
            for row in results
        ]
    }

@router.get("/orders/active")
async def get_active_orders(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Returns counts of active procurement and production orders
    """
    active_statuses = ['new', 'in_progress', 'pending_approval']
    
    procurement_count = db.query(func.count(Order.id))\
        .filter(
            and_(
                Order.type == 'procurement',
                Order.status.in_(active_statuses)
            )
        ).scalar()
    
    production_count = db.query(func.count(Order.id))\
        .filter(
            and_(
                Order.type == 'production',
                Order.status.in_(active_statuses)
            )
        ).scalar()
    
    return {
        "data": {
            "procurement": procurement_count,
            "production": production_count
        }
    }
