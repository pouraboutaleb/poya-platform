"""Add additional user roles

Revision ID: 009
Revises: 008
Create Date: 2025-08-02 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic
revision = '009'
down_revision = '008'
branch_labels = None
depends_on = None

def upgrade():
    # Insert additional roles
    roles_table = sa.table('roles',
        sa.column('name', sa.String),
        sa.column('description', sa.String)
    )
    
    op.bulk_insert(roles_table, [
        {'name': 'warehouse_manager', 'description': 'Warehouse manager'},
        {'name': 'warehouse_staff', 'description': 'Warehouse staff member'},
        {'name': 'purchasing_manager', 'description': 'Purchasing manager'},
        {'name': 'procurement_lead', 'description': 'Procurement team lead'},
        {'name': 'production_manager', 'description': 'Production manager'},
        {'name': 'production_planner', 'description': 'Production planner'},
        {'name': 'qc_manager', 'description': 'Quality control manager'},
        {'name': 'qc_inspector', 'description': 'Quality control inspector'},
    ])

def downgrade():
    # Remove the added roles
    op.execute("""
        DELETE FROM user_roles WHERE role_id IN (
            SELECT id FROM roles WHERE name IN (
                'warehouse_manager', 'warehouse_staff', 'purchasing_manager',
                'procurement_lead', 'production_manager', 'production_planner',
                'qc_manager', 'qc_inspector'
            )
        )
    """)
    
    op.execute("""
        DELETE FROM roles WHERE name IN (
            'warehouse_manager', 'warehouse_staff', 'purchasing_manager',
            'procurement_lead', 'production_manager', 'production_planner',
            'qc_manager', 'qc_inspector'
        )
    """)
