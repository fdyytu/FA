"""Add Discord Bot tables

Revision ID: 006_add_discord_tables
Revises: 005_add_product_tables
Create Date: 2024-01-01 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '006_add_discord_tables'
down_revision = '005_add_product_tables'
branch_labels = None
depends_on = None

def upgrade():
    # Create enum types
    discord_bot_status = postgresql.ENUM('ACTIVE', 'INACTIVE', 'MAINTENANCE', name='discordbotstatus')
    discord_bot_status.create(op.get_bind())
    
    currency_type = postgresql.ENUM('WL', 'DL', 'BGL', name='currencytype')
    currency_type.create(op.get_bind())
    
    # Create discord_bots table
    op.create_table('discord_bots',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.Column('bot_name', sa.String(length=100), nullable=False),
        sa.Column('bot_token', sa.Text(), nullable=False),
        sa.Column('guild_id', sa.String(length=50), nullable=False),
        sa.Column('live_stock_channel_id', sa.String(length=50), nullable=True),
        sa.Column('donation_webhook_url', sa.Text(), nullable=True),
        sa.Column('status', discord_bot_status, nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create discord_channels table
    op.create_table('discord_channels',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.Column('bot_id', sa.Integer(), nullable=False),
        sa.Column('channel_id', sa.String(length=50), nullable=False),
        sa.Column('channel_name', sa.String(length=100), nullable=False),
        sa.Column('channel_type', sa.String(length=50), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=True),
        sa.ForeignKeyConstraint(['bot_id'], ['discord_bots.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create discord_users table
    op.create_table('discord_users',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.Column('discord_id', sa.String(length=50), nullable=False),
        sa.Column('discord_username', sa.String(length=100), nullable=False),
        sa.Column('grow_id', sa.String(length=100), nullable=True),
        sa.Column('is_verified', sa.Boolean(), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_discord_users_discord_id'), 'discord_users', ['discord_id'], unique=True)
    
    # Create discord_wallets table
    op.create_table('discord_wallets',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('wl_balance', sa.Numeric(precision=15, scale=2), nullable=False),
        sa.Column('dl_balance', sa.Numeric(precision=15, scale=2), nullable=False),
        sa.Column('bgl_balance', sa.Numeric(precision=15, scale=2), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['discord_users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create discord_transactions table
    op.create_table('discord_transactions',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('transaction_type', sa.String(length=50), nullable=False),
        sa.Column('currency_type', currency_type, nullable=False),
        sa.Column('amount', sa.Numeric(precision=15, scale=2), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('reference_id', sa.String(length=100), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['discord_users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create live_stocks table
    op.create_table('live_stocks',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.Column('bot_id', sa.Integer(), nullable=False),
        sa.Column('product_code', sa.String(length=100), nullable=False),
        sa.Column('product_name', sa.String(length=200), nullable=False),
        sa.Column('price_wl', sa.Numeric(precision=15, scale=2), nullable=False),
        sa.Column('stock_quantity', sa.Integer(), nullable=False),
        sa.Column('category', sa.String(length=100), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('is_featured', sa.Boolean(), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=True),
        sa.Column('display_order', sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(['bot_id'], ['discord_bots.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create admin_world_configs table
    op.create_table('admin_world_configs',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.Column('world_name', sa.String(length=100), nullable=False),
        sa.Column('world_description', sa.Text(), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=True),
        sa.Column('access_level', sa.String(length=50), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create discord_bot_configs table
    op.create_table('discord_bot_configs',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.Column('config_key', sa.String(length=100), nullable=False),
        sa.Column('config_value', sa.Text(), nullable=False),
        sa.Column('config_type', sa.String(length=50), nullable=True),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_discord_bot_configs_config_key'), 'discord_bot_configs', ['config_key'], unique=True)

def downgrade():
    # Drop tables
    op.drop_index(op.f('ix_discord_bot_configs_config_key'), table_name='discord_bot_configs')
    op.drop_table('discord_bot_configs')
    op.drop_table('admin_world_configs')
    op.drop_table('live_stocks')
    op.drop_table('discord_transactions')
    op.drop_table('discord_wallets')
    op.drop_index(op.f('ix_discord_users_discord_id'), table_name='discord_users')
    op.drop_table('discord_users')
    op.drop_table('discord_channels')
    op.drop_table('discord_bots')
    
    # Drop enum types
    sa.Enum(name='currencytype').drop(op.get_bind())
    sa.Enum(name='discordbotstatus').drop(op.get_bind())
