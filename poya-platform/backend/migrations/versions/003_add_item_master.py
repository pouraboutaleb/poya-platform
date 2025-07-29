"""add_item_master

Revision ID: 003_add_item_master
Revises: 002_add_tasks
Create Date: 2025-07-29

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic
revision = '003_add_item_master'
down_revision = '002_add_tasks'
branch_labels = None
depends_on = None

def upgrade():
    # Create item_categories table
    op.create_table(
        'item_categories',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('description', sa.String(), nullable=True),
        sa.Column('parent_id', sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(['parent_id'], ['item_categories.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_item_categories_id'), 'item_categories', ['id'], unique=False)

    # Create items table
    op.create_table(
        'items',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('item_code', sa.String(length=50), nullable=False),
        sa.Column('name', sa.String(length=200), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('category_id', sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(['category_id'], ['item_categories.id'], ondelete='RESTRICT'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_items_id'), 'items', ['id'], unique=False)
    op.create_index(op.f('ix_items_item_code'), 'items', ['item_code'], unique=True)

def downgrade():
    op.drop_index(op.f('ix_items_item_code'), table_name='items')
    op.drop_index(op.f('ix_items_id'), table_name='items')
    op.drop_table('items')
    op.drop_index(op.f('ix_item_categories_id'), table_name='item_categories')
    op.drop_table('item_categories')
