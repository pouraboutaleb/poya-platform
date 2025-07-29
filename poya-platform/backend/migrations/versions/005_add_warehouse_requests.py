"""Add warehouse request system

Revision ID: 005_add_warehouse_requests
Revises: 004_add_production_reports
Create Date: 2025-07-29 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '005_add_warehouse_requests'
down_revision = '004_add_production_reports'
branch_labels = None
depends_on = None

def upgrade():
    # Create warehouse_requests table
    op.create_table(
        'warehouse_requests',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('project_name', sa.String(), nullable=False),
        sa.Column('description', sa.String(), nullable=True),
        sa.Column('priority', sa.String(), nullable=True),
        sa.Column('status', sa.String(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('requested_delivery_date', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_by_id', sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(['created_by_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_warehouse_requests_id'), 'warehouse_requests', ['id'], unique=False)

    # Create warehouse_request_items table
    op.create_table(
        'warehouse_request_items',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('quantity_requested', sa.Integer(), nullable=False),
        sa.Column('quantity_fulfilled', sa.Integer(), nullable=True),
        sa.Column('status', sa.String(), nullable=True),
        sa.Column('remarks', sa.String(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('request_id', sa.Integer(), nullable=False),
        sa.Column('item_id', sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(['item_id'], ['items.id'], ),
        sa.ForeignKeyConstraint(['request_id'], ['warehouse_requests.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_warehouse_request_items_id'), 'warehouse_request_items', ['id'], unique=False)

    # Add warehouse_staff column to users table
    op.add_column('users', sa.Column('is_warehouse_staff', sa.Boolean(), nullable=True, server_default='false'))

def downgrade():
    # Drop warehouse_request_items table
    op.drop_index(op.f('ix_warehouse_request_items_id'), table_name='warehouse_request_items')
    op.drop_table('warehouse_request_items')
    
    # Drop warehouse_requests table
    op.drop_index(op.f('ix_warehouse_requests_id'), table_name='warehouse_requests')
    op.drop_table('warehouse_requests')
    
    # Remove warehouse_staff column from users table
    op.drop_column('users', 'is_warehouse_staff')
