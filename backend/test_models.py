#!/usr/bin/env python3
"""
Simple test to check if SQLAlchemy models can be imported and configured correctly.
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

try:
    # Import all models to test relationships
    from app.models.user import User, Role
    from app.models.task import Task
    from app.models.order import Order
    from app.models.item import Item
    from app.models.item_category import ItemCategory
    from app.models.warehouse_request import WarehouseRequest, WarehouseRequestItem
    from app.models.route_card import RouteCard
    
    print("✅ All models imported successfully")
    
    # Try to access the relationships to test SQLAlchemy configuration
    print("Testing relationships...")
    
    # Test Order.tasks relationship
    print(f"Order.tasks: {Order.tasks}")
    
    # Test Task relationships
    print(f"Task.order: {Task.order}")
    print(f"Task.route_card: {Task.route_card}")
    
    # Test RouteCard.tasks relationship
    print(f"RouteCard.tasks: {RouteCard.tasks}")
    
    # Test User task relationships
    print(f"User.assigned_tasks: {User.assigned_tasks}")
    print(f"User.created_tasks: {User.created_tasks}")
    
    print("✅ All relationship checks passed")
    
except ImportError as e:
    print(f"❌ Import error: {e}")
    sys.exit(1)
except Exception as e:
    print(f"❌ Error testing relationships: {e}")
    sys.exit(1)
