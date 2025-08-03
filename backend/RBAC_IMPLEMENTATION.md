# Role-Based Access Control (RBAC) Implementation

## Overview
This document outlines the Role-Based Access Control implementation for the Poya Platform API endpoints.

## Security Module Enhancements

### Core Security Functions (`app/core/security.py`)

#### New RBAC Functions:
- `has_role(user, role_name)` - Check if user has a specific role
- `has_any_role(user, role_names)` - Check if user has any of the specified roles
- `require_roles(required_roles)` - Dependency factory for requiring specific roles
- `require_all_roles(required_roles)` - Dependency factory for requiring ALL specified roles

#### Pre-defined Role Dependencies:
- `require_admin` - Requires "admin" role
- `require_manager` - Requires "manager" or "admin" role
- `require_production_manager` - Requires "production_manager", "manager", or "admin" role
- `require_warehouse_staff` - Requires "warehouse_staff", "manager", or "admin" role
- `require_quality_control` - Requires "quality_control", "manager", or "admin" role
- `require_supervisor` - Requires "supervisor", "manager", or "admin" role

## Role Hierarchy

```
admin (highest)
├── manager
    ├── production_manager
    ├── supervisor
    ├── warehouse_staff
    └── quality_control
```

## Endpoint Security Implementation

### Items Management (`/api/v1/items`)
- **GET** `/categories` - Requires active user (any authenticated user)
- **GET** `/` - Requires active user (any authenticated user)
- **POST** `/categories` - Requires **manager** role or higher
- **POST** `/` - Requires **manager** role or higher

### Orders Management (`/api/v1/orders`)
- **GET** `/procurement` - Requires active user
- **GET** `/{warehouse_request_item_id}/orders` - Requires active user
- **POST** `/{warehouse_request_item_id}/shortage` - Requires **warehouse_staff** role or higher
- **PUT** `/{order_id}` - Requires **warehouse_staff** role or higher
- **POST** `/{order_id}/mark-purchased` - Requires **manager** role or higher

### Tasks Management (`/api/v1/tasks`)
- **GET** `/me` - Requires active user
- **GET** `/{task_id}` - Requires active user
- **POST** `/` - Requires active user
- **PUT** `/{task_id}` - Requires active user (with ownership check)
- **PUT** `/{task_id}/status` - Requires active user (with ownership check)
- **DELETE** `/{task_id}` - Requires **supervisor** role or higher

### Production Reports (`/api/v1/production-reports`)
- **GET** `/` - Requires active user
- **POST** `/` - Requires **production_manager** role or higher

### Quality Control (`/api/v1/qc-inspection`)
- **GET** `/inspection-tasks` - Requires **quality_control** role or higher
- **GET** `/route-cards/{route_card_id}/details` - Requires **quality_control** role or higher
- **POST** `/inspection-tasks/{task_id}/decision` - Requires **quality_control** role or higher

### Warehouse Requests (`/api/v1/warehouse-requests`)
- **GET** `/warehouse-requests` - Requires active user (filtered by ownership for non-warehouse staff)
- **POST** `/warehouse-requests` - Requires active user

### User Management (`/api/v1/users`)
- **GET** `/me` - Requires active user
- **GET** `/` - Requires **admin** role
- **POST** `/register` - Requires **admin** role

## Role Definitions

### Admin
- Full system access
- User management capabilities
- Can override all role restrictions

### Manager
- Can create/manage items and categories
- Can mark orders as purchased
- Access to all production and warehouse data
- Can delete any tasks

### Production Manager
- Can create production reports
- Access to production-related data
- Can manage production tasks

### Warehouse Staff
- Can create and update orders
- Can manage warehouse requests
- Access to inventory-related functions

### Quality Control
- Can access QC inspection tasks
- Can make QC decisions
- Can view route card details for inspection

### Supervisor
- Can delete tasks
- Can manage team assignments
- Access to supervisory functions

## Implementation Notes

1. **Role Inheritance**: Higher-level roles automatically have access to lower-level role functions
2. **Active User Check**: All protected endpoints require the user to be active
3. **Ownership Checks**: Some endpoints (like task updates) include additional ownership validation
4. **Graceful Degradation**: Endpoints maintain backward compatibility while adding security layers

## Error Responses

- **401 Unauthorized**: Invalid or missing authentication token
- **403 Forbidden**: User lacks required role permissions
- **400 Bad Request**: Inactive user account

## Usage Examples

```python
from app.core.security import require_manager, require_production_manager

@router.post("/items")
async def create_item(
    item_data: ItemCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_manager)  # Only managers and admins
):
    pass

@router.post("/production-reports")
async def create_report(
    report_data: ProductionReportCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_production_manager)  # Only production managers and above
):
    pass
```

## Migration Considerations

- Existing endpoints without role restrictions now require at least an active user
- Admin users should be created before deployment to prevent lockout
- Role assignments should be done through database migration or admin interface
- Consider implementing a "super admin" role for initial system setup
