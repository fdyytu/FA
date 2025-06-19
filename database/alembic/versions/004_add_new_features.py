"""Add new features: user profiles, transactions, notifications

Revision ID: 004_add_new_features
Revises: 003_add_admin_features
Create Date: 2024-01-01 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '004_add_new_features'
down_revision = '002_add_admin_tables'
branch_labels = None
depends_on = None

def upgrade():
    # Create admins table
    op.create_table('admins',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('username', sa.String(length=50), nullable=False),
        sa.Column('email', sa.String(length=100), nullable=False),
        sa.Column('full_name', sa.String(length=100), nullable=False),
        sa.Column('hashed_password', sa.Text(), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=True),
        sa.Column('is_superadmin', sa.Boolean(), nullable=True),
        sa.Column('phone_number', sa.String(length=20), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_admins_email'), 'admins', ['email'], unique=True)
    op.create_index(op.f('ix_admins_username'), 'admins', ['username'], unique=True)

    # Create user_profiles table
    op.create_table('user_profiles',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('avatar_url', sa.String(length=500), nullable=True),
        sa.Column('birth_date', sa.DateTime(), nullable=True),
        sa.Column('address', sa.Text(), nullable=True),
        sa.Column('city', sa.String(length=100), nullable=True),
        sa.Column('province', sa.String(length=100), nullable=True),
        sa.Column('postal_code', sa.String(length=10), nullable=True),
        sa.Column('identity_number', sa.String(length=20), nullable=True),
        sa.Column('identity_verified', sa.String(length=1), nullable=True),
        sa.Column('bank_account', sa.String(length=50), nullable=True),
        sa.Column('bank_name', sa.String(length=100), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_user_profiles_user_id'), 'user_profiles', ['user_id'], unique=True)

    # Create transactions table
    op.create_table('transactions',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('transaction_code', sa.String(length=50), nullable=False),
        sa.Column('transaction_type', sa.Enum('PPOB', 'TOPUP', 'TRANSFER', 'WITHDRAWAL', name='transactiontype'), nullable=False),
        sa.Column('amount', sa.Numeric(precision=15, scale=2), nullable=False),
        sa.Column('admin_fee', sa.Numeric(precision=15, scale=2), nullable=True),
        sa.Column('total_amount', sa.Numeric(precision=15, scale=2), nullable=False),
        sa.Column('status', sa.Enum('PENDING', 'SUCCESS', 'FAILED', 'CANCELLED', name='transactionstatus'), nullable=True),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('reference_id', sa.String(length=100), nullable=True),
        sa.Column('metadata', sa.Text(), nullable=True),
        sa.Column('processed_at', sa.DateTime(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_transactions_transaction_code'), 'transactions', ['transaction_code'], unique=True)
    op.create_index(op.f('ix_transactions_reference_id'), 'transactions', ['reference_id'], unique=False)

    # Create daily_mutations table
    op.create_table('daily_mutations',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('mutation_date', sa.DateTime(), nullable=False),
        sa.Column('total_transactions', sa.Integer(), nullable=True),
        sa.Column('total_amount', sa.Numeric(precision=15, scale=2), nullable=True),
        sa.Column('total_fee', sa.Numeric(precision=15, scale=2), nullable=True),
        sa.Column('success_count', sa.Integer(), nullable=True),
        sa.Column('failed_count', sa.Integer(), nullable=True),
        sa.Column('pending_count', sa.Integer(), nullable=True),
        sa.Column('transaction_types', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_daily_mutations_mutation_date'), 'daily_mutations', ['mutation_date'], unique=True)

    # Create notifications table
    op.create_table('notifications',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=True),
        sa.Column('title', sa.String(length=200), nullable=False),
        sa.Column('message', sa.Text(), nullable=False),
        sa.Column('notification_type', sa.Enum('TRANSACTION', 'SYSTEM', 'PROMOTION', 'SECURITY', name='notificationtype'), nullable=False),
        sa.Column('channel', sa.Enum('EMAIL', 'WHATSAPP', 'DISCORD', 'PUSH', 'SMS', name='notificationchannel'), nullable=False),
        sa.Column('status', sa.Enum('PENDING', 'SENT', 'FAILED', 'READ', name='notificationstatus'), nullable=True),
        sa.Column('is_read', sa.Boolean(), nullable=True),
        sa.Column('sent_at', sa.DateTime(), nullable=True),
        sa.Column('read_at', sa.DateTime(), nullable=True),
        sa.Column('metadata', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )

    # Create admin_notification_settings table
    op.create_table('admin_notification_settings',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('admin_id', sa.Integer(), nullable=False),
        sa.Column('notification_type', sa.Enum('TRANSACTION', 'SYSTEM', 'PROMOTION', 'SECURITY', name='notificationtype'), nullable=False),
        sa.Column('channel', sa.Enum('EMAIL', 'WHATSAPP', 'DISCORD', 'PUSH', 'SMS', name='notificationchannel'), nullable=False),
        sa.Column('is_enabled', sa.Boolean(), nullable=True),
        sa.Column('webhook_url', sa.String(length=500), nullable=True),
        sa.Column('phone_number', sa.String(length=20), nullable=True),
        sa.Column('email', sa.String(length=100), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['admin_id'], ['admins.id'], ),
        sa.PrimaryKeyConstraint('id')
    )

    # Create webhook_logs table
    op.create_table('webhook_logs',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('webhook_type', sa.String(length=50), nullable=False),
        sa.Column('request_method', sa.String(length=10), nullable=False),
        sa.Column('request_url', sa.String(length=500), nullable=False),
        sa.Column('request_headers', sa.Text(), nullable=True),
        sa.Column('request_body', sa.Text(), nullable=True),
        sa.Column('response_status', sa.Integer(), nullable=True),
        sa.Column('response_body', sa.Text(), nullable=True),
        sa.Column('processed', sa.Boolean(), nullable=True),
        sa.Column('error_message', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )

def downgrade():
    # Drop tables in reverse order
    op.drop_table('webhook_logs')
    op.drop_table('admin_notification_settings')
    op.drop_table('notifications')
    op.drop_table('daily_mutations')
    op.drop_table('transactions')
    op.drop_table('user_profiles')
    op.drop_table('admins')
    
    # Drop enums
    op.execute('DROP TYPE IF EXISTS notificationstatus')
    op.execute('DROP TYPE IF EXISTS notificationchannel')
    op.execute('DROP TYPE IF EXISTS notificationtype')
    op.execute('DROP TYPE IF EXISTS transactionstatus')
    op.execute('DROP TYPE IF EXISTS transactiontype')
