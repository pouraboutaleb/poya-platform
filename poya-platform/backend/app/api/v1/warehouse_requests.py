from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime, timedelta

from ...core.security import get_current_user
from ...db.session import get_db
from ...models.user import User
from ...models.item import Item
from ...models.warehouse_request import WarehouseRequest, WarehouseRequestItem
from ...models.order import Order
from ...schemas.warehouse_request import (
    WarehouseRequest as WarehouseRequestSchema,
    WarehouseRequestCreate,
    WarehouseRequestUpdate,
    WarehouseRequestItemUpdate,
)port List
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from datetime import datetime

from ...core.security import get_current_user
from ...db.session import get_db
from ...models.user import User
from ...models.warehouse_request import WarehouseRequest, WarehouseRequestItem
from ...schemas.warehouse_request import (
    WarehouseRequest as WarehouseRequestSchema,
    WarehouseRequestCreate,
    WarehouseRequestUpdate,
)

router = APIRouter()

@router.post("/warehouse-requests", response_model=WarehouseRequestSchema)
def create_warehouse_request(
    *,
    db: Session = Depends(get_db),
    request_in: WarehouseRequestCreate,
    current_user: User = Depends(get_current_user)
):
    """Create a new warehouse request with items."""
    
    # Create warehouse request
    db_request = WarehouseRequest(
        project_name=request_in.project_name,
        description=request_in.description,
        priority=request_in.priority,
        requested_delivery_date=request_in.requested_delivery_date,
        created_by_id=current_user.id
    )
    db.add(db_request)
    
    # Create request items
    for item in request_in.request_items:
        db_item = WarehouseRequestItem(
            request=db_request,
            item_id=item.item_id,
            quantity_requested=item.quantity_requested,
            remarks=item.remarks
        )
        db.add(db_item)
    
    db.commit()
    db.refresh(db_request)
    return db_request

@router.get("/warehouse-requests", response_model=List[WarehouseRequestSchema])
def get_warehouse_requests(
    *,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1),
    status: str = None,
    start_date: datetime = None,
    end_date: datetime = None
):
    """Get all warehouse requests with optional filtering."""
    query = db.query(WarehouseRequest)

    # Apply filters
    if status:
        query = query.filter(WarehouseRequest.status == status)
    if start_date:
        query = query.filter(WarehouseRequest.created_at >= start_date)
    if end_date:
        query = query.filter(WarehouseRequest.created_at <= end_date)

    # Only warehouse staff can see all requests
    if not current_user.is_warehouse_staff:
        query = query.filter(WarehouseRequest.created_by_id == current_user.id)

    # Apply pagination
    requests = query.offset(skip).limit(limit).all()
    return requests

@router.get("/warehouse-requests/{request_id}", response_model=WarehouseRequestSchema)
def get_warehouse_request(
    *,
    db: Session = Depends(get_db),
    request_id: int,
    current_user: User = Depends(get_current_user)
):
    """Get a specific warehouse request by ID."""
    request = db.query(WarehouseRequest).filter(WarehouseRequest.id == request_id).first()
    if not request:
        raise HTTPException(status_code=404, detail="Warehouse request not found")
    
    # Check permissions
    if not current_user.is_warehouse_staff and request.created_by_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    
    return request

@router.put("/warehouse-requests/{request_id}", response_model=WarehouseRequestSchema)
def update_warehouse_request(
    *,
    db: Session = Depends(get_db),
    request_id: int,
    request_in: WarehouseRequestUpdate,
    current_user: User = Depends(get_current_user)
):
    """Update a warehouse request."""
    request = db.query(WarehouseRequest).filter(WarehouseRequest.id == request_id).first()
    if not request:
        raise HTTPException(status_code=404, detail="Warehouse request not found")

    # Only warehouse staff can update status
    if request_in.status and not current_user.is_warehouse_staff:
        raise HTTPException(status_code=403, detail="Not enough permissions to update status")

    # Only creator or warehouse staff can update request
    if not current_user.is_warehouse_staff and request.created_by_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not enough permissions")

    # Update request fields
    for field, value in request_in.dict(exclude_unset=True).items():
        setattr(request, field, value)

    db.commit()
    db.refresh(request)
    return request

@router.put("/warehouse-requests/{request_id}/items/{item_id}")
async def update_warehouse_request_item(
    *,
    db: Session = Depends(get_db),
    request_id: int,
    item_id: int,
    item_update: WarehouseRequestItemUpdate,
    current_user: User = Depends(get_current_user)
):
    """Update a warehouse request item and handle shortage workflow."""
    
    # Verify user is warehouse staff
    if not current_user.is_warehouse_staff:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    
    # Get the request item
    request_item = db.query(WarehouseRequestItem).filter(
        WarehouseRequestItem.request_id == request_id,
        WarehouseRequestItem.id == item_id
    ).first()
    
    if not request_item:
        raise HTTPException(status_code=404, detail="Warehouse request item not found")
    
    # If status is being updated to backordered, trigger shortage workflow
    if item_update.status == "backordered":
        # Get the item details
        item = db.query(Item).filter(Item.id == request_item.item_id).first()
        if not item:
            raise HTTPException(status_code=404, detail="Item not found")
        
        # Determine order type based on item category or other business rules
        order_type = "production" if item.category.name == "Manufactured" else "procurement"
        
        # Create new order
        new_order = Order(
            order_type=order_type,
            status="draft",
            priority=request_item.request.priority,  # Inherit priority from request
            quantity=request_item.quantity_requested,
            remarks=f"Auto-generated due to shortage in warehouse request #{request_id}",
            required_date=datetime.now() + timedelta(days=7),  # Example: Set due date to 7 days from now
            created_by_id=current_user.id,
            item_id=item.id,
            warehouse_request_item_id=item_id
        )
        
        db.add(new_order)
    
    # Update the request item
    for field, value in item_update.dict(exclude_unset=True).items():
        setattr(request_item, field, value)
    
    # If all items are processed, update the main request status
    request = request_item.request
    all_items_processed = all(
        item.status in ["ready", "backordered"]
        for item in request.request_items
    )
    
    if all_items_processed:
        request.status = "processing"
    
    db.commit()
    
    return {
        "message": "Item updated successfully",
        "order_created": item_update.status == "backordered"
    }
