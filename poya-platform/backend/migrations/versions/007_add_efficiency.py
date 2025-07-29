"""add_efficiency_percentage

Revision ID: 007_add_efficiency
Revises: 006_add_orders
Create Date: 2025-07-29 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '007_add_efficiency'
down_revision = '006_add_orders'
branch_labels = None
depends_on = None

def upgrade():
    # Add efficiency_percentage column to production_reports if it doesn't exist
    op.add_column('production_reports', sa.Column('efficiency_percentage', sa.Float))
    
    # Create an index for faster date-based queries
    op.create_index(
        'idx_production_reports_created_at',
        'production_reports',
        ['created_at']
    )
    
    # Create indexes for faster order status queries
    op.create_index(
        'idx_orders_type_status',
        'orders',
        ['type', 'status']
    )

def downgrade():
    # Remove the indexes
    op.drop_index('idx_production_reports_created_at')
    op.drop_index('idx_orders_type_status')
    
    # Remove the efficiency_percentage column
    op.drop_column('production_reports', 'efficiency_percentage')
