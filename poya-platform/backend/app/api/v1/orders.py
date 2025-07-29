from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..db.session import get_db
from ..services.order_service import OrderService
from ..schemas.order import Order, OrderCreate, OrderUpdate
from ..core.security import get_current_active_user
from ..models.user import User

router = APIRouter()

@router.post("/{warehouse_request_item_id}/shortage", response_model=Order)
def create_shortage_order(
    warehouse_request_item_id: int,
    order_data: OrderCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Create a new order for a shortage item.
    This endpoint is called when a warehouse request item is marked as shortage.
    """
    try:
        order = OrderService.create_shortage_order(
            db=db,
            item_id=order_data.item_id,
            warehouse_request_item_id=warehouse_request_item_id,
            created_by_id=current_user.id,
            quantity=order_data.quantity,
            priority=order_data.priority
        )
        return order
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/{order_id}", response_model=Order)
def update_order(
    order_id: int,
    order_update: OrderUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Update an order's status and other details.
    When an order is marked as completed, it will automatically update the related warehouse request item.
    """
    try:
        return OrderService.update_order_status(
            db=db,
            order_id=order_id,
            status=order_update.status,
            remarks=order_update.remarks
        )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{warehouse_request_item_id}/orders", response_model=List[Order])
def get_item_orders(
    warehouse_request_item_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get all orders related to a specific warehouse request item."""
    return OrderService.get_related_orders(db, warehouse_request_item_id)

@router.get("/procurement", response_model=List[Order])
def get_procurement_orders(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get all active procurement orders."""
    return OrderService.get_procurement_orders(db)

@router.post("/{order_id}/mark-purchased", response_model=Order)
def mark_order_purchased(
    order_id: int,
    purchase_data: dict,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Mark a procurement order as purchased and create a receiving task."""
    return OrderService.mark_order_purchased(
        db=db,
        order_id=order_id,
        vendor_name=purchase_data["vendor_name"],
        price=purchase_data["price"],
        user_id=current_user.id
    )
