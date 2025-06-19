"""Add wallet tables

Revision ID: 001_add_wallet_tables
Revises: 
Create Date: 2024-01-01 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import sqlite

# revision identifiers, used by Alembic.
revision = '001_add_wallet_tables'
down_revision = None
depends_on = None


def upgrade():
    # Add balance column to users table
    op.add_column('users', sa.Column('balance', sa.Numeric(15, 2), nullable=False, server_default='0'))
    
    # Create wallet_transactions table
    op.create_table('wallet_transactions',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('(CURRENT_TIMESTAMP)'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('(CURRENT_TIMESTAMP)'), nullable=True),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('transaction_code', sa.String(length=50), nullable=False),
        sa.Column('transaction_type', sa.Enum('TOPUP_MANUAL', 'TOPUP_MIDTRANS', 'TRANSFER_SEND', 'TRANSFER_RECEIVE', 'PPOB_PAYMENT', 'REFUND', name='transactiontype'), nullable=False),
        sa.Column('amount', sa.Numeric(15, 2), nullable=False),
        sa.Column('balance_before', sa.Numeric(15, 2), nullable=False),
        sa.Column('balance_after', sa.Numeric(15, 2), nullable=False),
        sa.Column('status', sa.Enum('PENDING', 'SUCCESS', 'FAILED', 'CANCELLED', name='transactionstatus'), nullable=True),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('reference_id', sa.String(length=100), nullable=True),
        sa.Column('meta_data', sa.Text(), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_wallet_transactions_id'), 'wallet_transactions', ['id'], unique=False)
    op.create_index(op.f('ix_wallet_transactions_transaction_code'), 'wallet_transactions', ['transaction_code'], unique=True)
    
    # Create transfers table
    op.create_table('transfers',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('(CURRENT_TIMESTAMP)'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('(CURRENT_TIMESTAMP)'), nullable=True),
        sa.Column('sender_id', sa.Integer(), nullable=False),
        sa.Column('receiver_id', sa.Integer(), nullable=False),
        sa.Column('transfer_code', sa.String(length=50), nullable=False),
        sa.Column('amount', sa.Numeric(15, 2), nullable=False),
        sa.Column('status', sa.Enum('PENDING', 'SUCCESS', 'FAILED', 'CANCELLED', name='transactionstatus'), nullable=True),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('sender_transaction_id', sa.Integer(), nullable=True),
        sa.Column('receiver_transaction_id', sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(['receiver_id'], ['users.id'], ),
        sa.ForeignKeyConstraint(['receiver_transaction_id'], ['wallet_transactions.id'], ),
        sa.ForeignKeyConstraint(['sender_id'], ['users.id'], ),
        sa.ForeignKeyConstraint(['sender_transaction_id'], ['wallet_transactions.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_transfers_id'), 'transfers', ['id'], unique=False)
    op.create_index(op.f('ix_transfers_transfer_code'), 'transfers', ['transfer_code'], unique=True)
    
    # Create topup_requests table
    op.create_table('topup_requests',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('(CURRENT_TIMESTAMP)'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('(CURRENT_TIMESTAMP)'), nullable=True),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('request_code', sa.String(length=50), nullable=False),
        sa.Column('amount', sa.Numeric(15, 2), nullable=False),
        sa.Column('payment_method', sa.Enum('BANK_TRANSFER', 'WALLET', 'MIDTRANS', name='paymentmethod'), nullable=False),
        sa.Column('status', sa.Enum('PENDING', 'APPROVED', 'REJECTED', name='topupstatus'), nullable=True),
        sa.Column('bank_name', sa.String(length=50), nullable=True),
        sa.Column('account_number', sa.String(length=50), nullable=True),
        sa.Column('account_name', sa.String(length=100), nullable=True),
        sa.Column('proof_image', sa.String(length=255), nullable=True),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('admin_notes', sa.Text(), nullable=True),
        sa.Column('processed_by', sa.Integer(), nullable=True),
        sa.Column('processed_at', sa.DateTime(), nullable=True),
        sa.Column('midtrans_order_id', sa.String(length=100), nullable=True),
        sa.Column('midtrans_transaction_id', sa.String(length=100), nullable=True),
        sa.Column('wallet_transaction_id', sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(['processed_by'], ['users.id'], ),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.ForeignKeyConstraint(['wallet_transaction_id'], ['wallet_transactions.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_topup_requests_id'), 'topup_requests', ['id'], unique=False)
    op.create_index(op.f('ix_topup_requests_request_code'), 'topup_requests', ['request_code'], unique=True)


def downgrade():
    # Drop tables
    op.drop_index(op.f('ix_topup_requests_request_code'), table_name='topup_requests')
    op.drop_index(op.f('ix_topup_requests_id'), table_name='topup_requests')
    op.drop_table('topup_requests')
    
    op.drop_index(op.f('ix_transfers_transfer_code'), table_name='transfers')
    op.drop_index(op.f('ix_transfers_id'), table_name='transfers')
    op.drop_table('transfers')
    
    op.drop_index(op.f('ix_wallet_transactions_transaction_code'), table_name='wallet_transactions')
    op.drop_index(op.f('ix_wallet_transactions_id'), table_name='wallet_transactions')
    op.drop_table('wallet_transactions')
    
    # Remove balance column from users table
    op.drop_column('users', 'balance')
