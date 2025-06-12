"""Add admin config and margin tables

Revision ID: 002_add_admin_tables
Revises: 001_add_wallet_tables
Create Date: 2024-01-01 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '002_add_admin_tables'
down_revision = '001_add_wallet_tables'
branch_labels = None
depends_on = None


def upgrade():
    # Create admin_configs table
    op.create_table('admin_configs',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('config_key', sa.String(length=100), nullable=False),
        sa.Column('config_value', sa.Text(), nullable=False),
        sa.Column('config_type', sa.String(length=50), nullable=True),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_admin_configs_config_key'), 'admin_configs', ['config_key'], unique=True)

    # Create ppob_margin_configs table
    op.create_table('ppob_margin_configs',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('category', sa.String(length=50), nullable=False),
        sa.Column('product_code', sa.String(length=50), nullable=True),
        sa.Column('margin_type', sa.Enum('PERCENTAGE', 'NOMINAL', name='margintype'), nullable=False),
        sa.Column('margin_value', sa.Numeric(precision=15, scale=2), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=True),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )


def downgrade():
    op.drop_table('ppob_margin_configs')
    op.drop_index(op.f('ix_admin_configs_config_key'), table_name='admin_configs')
    op.drop_table('admin_configs')
    op.execute('DROP TYPE margintype')
