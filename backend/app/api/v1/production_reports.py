from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import date, datetime, timedelta

from ...core.security import get_current_user, get_current_active_user, require_production_manager
from ...models.user import User
from ...models.production_report import ProductionReport
from ...models.production_log import ProductionLog
from ...models.stoppage import Stoppage
from ...models.item import Item
from ...schemas.production_report import (
    ProductionReportCreate,
    ProductionReportResponse,
)
from ...db.session import get_db

router = APIRouter()

@router.post("", response_model=ProductionReportResponse)
async def create_production_report(
    report_data: ProductionReportCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_production_manager)
):
    """Create a new production report - Requires production manager or higher role"""
    
    # Check if report for the same date and shift already exists
    existing_report = db.query(ProductionReport).filter(
        ProductionReport.report_date == report_data.report_date,
        ProductionReport.shift == report_data.shift
    ).first()
    
    if existing_report:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"A report for {report_data.report_date} {report_data.shift} shift already exists"
        )
    
    # Create production report
    db_report = ProductionReport(
        report_date=report_data.report_date,
        shift=report_data.shift,
        daily_challenge=report_data.daily_challenge,
        solutions_implemented=report_data.solutions_implemented,
        notes=report_data.notes,
        created_by_id=current_user.id
    )
    
    # Add production logs
    for log_data in report_data.production_logs:
        # Verify item exists
        item = db.query(Item).filter(Item.id == log_data.item_id).first()
        if not item:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Item with id {log_data.item_id} not found"
            )
        
        # Calculate efficiency
        efficiency = (log_data.quantity_produced / log_data.target_quantity * 100) if log_data.target_quantity > 0 else 0
        
        db_log = ProductionLog(
            item_id=log_data.item_id,
            quantity_produced=log_data.quantity_produced,
            target_quantity=log_data.target_quantity,
            efficiency=efficiency,
            remarks=log_data.remarks
        )
        db_report.production_logs.append(db_log)
    
    # Add stoppages
    for stoppage_data in report_data.stoppages:
        db_stoppage = Stoppage(
            type=stoppage_data.type,
            reason=stoppage_data.reason,
            duration=stoppage_data.duration,
            action_taken=stoppage_data.action_taken
        )
        db_report.stoppages.append(db_stoppage)
    
    db.add(db_report)
    db.commit()
    db.refresh(db_report)
    
    # Add created_by_name to response
    response = ProductionReportResponse.from_orm(db_report)
    response.created_by_name = current_user.full_name
    
    # Add item details to production logs
    for log in response.production_logs:
        item = db.query(Item).filter(Item.id == log.item_id).first()
        log.item_name = item.name
        log.item_code = item.item_code
    
    return response

@router.get("", response_model=List[ProductionReportResponse])
async def get_production_reports(
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    shift: Optional[str] = None,
    skip: int = 0,
    limit: int = 20,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get list of production reports with optional date range and shift filter"""
    query = db.query(ProductionReport)
    
    # Apply date range filter
    if start_date:
        query = query.filter(ProductionReport.report_date >= start_date)
    if end_date:
        query = query.filter(ProductionReport.report_date <= end_date)
    
    # Apply shift filter
    if shift:
        query = query.filter(ProductionReport.shift == shift)
    
    # Order by date and shift
    query = query.order_by(ProductionReport.report_date.desc(), ProductionReport.shift)
    
    # Apply pagination
    reports = query.offset(skip).limit(limit).all()
    
    # Prepare response with additional fields
    response_reports = []
    for report in reports:
        report_response = ProductionReportResponse.from_orm(report)
        report_response.created_by_name = report.created_by.full_name
        
        # Add item details to production logs
        for log in report_response.production_logs:
            item = db.query(Item).filter(Item.id == log.item_id).first()
            log.item_name = item.name
            log.item_code = item.item_code
        
        response_reports.append(report_response)
    
    return response_reports
