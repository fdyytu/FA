"""add ppob categories

Revision ID: 202401171200
Revises: previous_revision
Create Date: 2024-01-17 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '202401171200'
down_revision = None  # This is the first migration
branch_labels = None
depends_on = None

def upgrade():
    # Create ppob_categories table
    op.create_table(
        'ppob_categories',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('code', sa.String(), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('icon', sa.String(), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('code'),
        sa.UniqueConstraint('name')
    )
    op.create_index('ix_ppob_categories_code', 'ppob_categories', ['code'])
    op.create_index('ix_ppob_categories_name', 'ppob_categories', ['name'])

    # Create ppob_transactions table
    op.create_table(
        'ppob_transactions',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=True),
        sa.Column('transaction_code', sa.String(), nullable=True),
        sa.Column('category_id', sa.Integer(), nullable=True),
        sa.Column('product_code', sa.String(), nullable=True),
        sa.Column('product_name', sa.String(), nullable=True),
        sa.Column('customer_number', sa.String(), nullable=True),
        sa.Column('customer_name', sa.String(), nullable=True),
        sa.Column('amount', sa.Float(), nullable=True),
        sa.Column('admin_fee', sa.Float(), nullable=True),
        sa.Column('total_amount', sa.Float(), nullable=True),
        sa.Column('status', sa.String(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.ForeignKeyConstraint(['category_id'], ['ppob_categories.id'], name='fk_ppob_transactions_category'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('transaction_code')
    )
    op.create_index('ix_ppob_transactions_transaction_code', 'ppob_transactions', ['transaction_code'])

    # Create ppob_products table
    op.create_table(
        'ppob_products',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('category_id', sa.Integer(), nullable=True),
        sa.Column('product_code', sa.String(), nullable=True),
        sa.Column('product_name', sa.String(), nullable=True),
        sa.Column('description', sa.String(), nullable=True),
        sa.Column('price', sa.Float(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.ForeignKeyConstraint(['category_id'], ['ppob_categories.id'], name='fk_ppob_products_category'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('product_code')
    )
    op.create_index('ix_ppob_products_product_code', 'ppob_products', ['product_code'])

    # Insert default categories
    op.execute("""
        INSERT INTO ppob_categories (name, code, description, is_active)
        VALUES 
        ('Pulsa', 'pulsa', 'Pulsa all operator', true),
        ('Paket Data', 'data', 'Paket data internet', true),
        ('PLN', 'pln', 'Pembayaran listrik PLN', true)
    """)

def downgrade():
    # Drop tables in reverse order
    op.drop_table('ppob_products')
    op.drop_table('ppob_transactions')
    op.drop_table('ppob_categories')
