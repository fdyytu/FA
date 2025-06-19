"""Add Discord Bot models

Revision ID: add_discord_models
Revises: 
Create Date: 2024-01-01 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '003_add_discord_models'
down_revision = '002_add_admin_tables'
branch_labels = None
depends_on = None

def upgrade():
    # Create enum types
    op.execute("CREATE TYPE discordbotstatus AS ENUM ('ACTIVE', 'INACTIVE', 'MAINTENANCE')")
    op.execute("CREATE TYPE currencytype AS ENUM ('wl', 'dl', 'bgl')")
    
    # Create discord_bots table
    op.create_table('discord_bots',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('bot_name', sa.String(length=100), nullable=False),
        sa.Column('bot_token', sa.Text(), nullable=False),
        sa.Column('guild_id', sa.String(length=50), nullable=False),
        sa.Column('live_stock_channel_id', sa.String(length=50), nullable=True),
        sa.Column('donation_webhook_url', sa.Text(), nullable=True),
        sa.Column('status', postgresql.ENUM('ACTIVE', 'INACTIVE', 'MAINTENANCE', name='discordbotstatus'), nullable=False, server_default='INACTIVE'),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_discord_bots_guild_id'), 'discord_bots', ['guild_id'], unique=True)
    op.create_index(op.f('ix_discord_bots_id'), 'discord_bots', ['id'], unique=False)

    # Create discord_channels table
    op.create_table('discord_channels',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('bot_id', sa.Integer(), nullable=False),
        sa.Column('channel_id', sa.String(length=50), nullable=False),
        sa.Column('channel_name', sa.String(length=100), nullable=False),
        sa.Column('channel_type', sa.String(length=50), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['bot_id'], ['discord_bots.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_discord_channels_id'), 'discord_channels', ['id'], unique=False)

    # Create discord_users table
    op.create_table('discord_users',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('discord_id', sa.String(length=50), nullable=False),
        sa.Column('discord_username', sa.String(length=100), nullable=False),
        sa.Column('grow_id', sa.String(length=100), nullable=True),
        sa.Column('is_verified', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_discord_users_discord_id'), 'discord_users', ['discord_id'], unique=True)
    op.create_index(op.f('ix_discord_users_id'), 'discord_users', ['id'], unique=False)

    # Create discord_wallets table
    op.create_table('discord_wallets',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('wl_balance', sa.Numeric(precision=15, scale=2), nullable=False, server_default='0'),
        sa.Column('dl_balance', sa.Numeric(precision=15, scale=2), nullable=False, server_default='0'),
        sa.Column('bgl_balance', sa.Numeric(precision=15, scale=2), nullable=False, server_default='0'),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['discord_users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_discord_wallets_id'), 'discord_wallets', ['id'], unique=False)
    op.create_index(op.f('ix_discord_wallets_user_id'), 'discord_wallets', ['user_id'], unique=True)

    # Create discord_transactions table
    op.create_table('discord_transactions',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('transaction_type', sa.String(length=50), nullable=False),
        sa.Column('currency_type', postgresql.ENUM('wl', 'dl', 'bgl', name='currencytype'), nullable=False),
        sa.Column('amount', sa.Numeric(precision=15, scale=2), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('reference_id', sa.String(length=100), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['discord_users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_discord_transactions_id'), 'discord_transactions', ['id'], unique=False)

    # Create live_stocks table
    op.create_table('live_stocks',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('bot_id', sa.Integer(), nullable=False),
        sa.Column('product_code', sa.String(length=100), nullable=False),
        sa.Column('product_name', sa.String(length=200), nullable=False),
        sa.Column('price_wl', sa.Numeric(precision=15, scale=2), nullable=False),
        sa.Column('stock_quantity', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('category', sa.String(length=100), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('is_featured', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('display_order', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['bot_id'], ['discord_bots.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_live_stocks_id'), 'live_stocks', ['id'], unique=False)
    op.create_index(op.f('ix_live_stocks_product_code'), 'live_stocks', ['product_code'], unique=False)

    # Create admin_world_configs table
    op.create_table('admin_world_configs',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('world_name', sa.String(length=100), nullable=False),
        sa.Column('world_description', sa.Text(), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('access_level', sa.String(length=50), nullable=False, server_default='public'),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_admin_world_configs_id'), 'admin_world_configs', ['id'], unique=False)

    # Create discord_bot_configs table
    op.create_table('discord_bot_configs',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('config_key', sa.String(length=100), nullable=False),
        sa.Column('config_value', sa.Text(), nullable=False),
        sa.Column('config_type', sa.String(length=50), nullable=False, server_default='string'),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_discord_bot_configs_config_key'), 'discord_bot_configs', ['config_key'], unique=True)
    op.create_index(op.f('ix_discord_bot_configs_id'), 'discord_bot_configs', ['id'], unique=False)

def downgrade():
    # Drop tables in reverse order
    op.drop_index(op.f('ix_discord_bot_configs_id'), table_name='discord_bot_configs')
    op.drop_index(op.f('ix_discord_bot_configs_config_key'), table_name='discord_bot_configs')
    op.drop_table('discord_bot_configs')
    
    op.drop_index(op.f('ix_admin_world_configs_id'), table_name='admin_world_configs')
    op.drop_table('admin_world_configs')
    
    op.drop_index(op.f('ix_live_stocks_product_code'), table_name='live_stocks')
    op.drop_index(op.f('ix_live_stocks_id'), table_name='live_stocks')
    op.drop_table('live_stocks')
    
    op.drop_index(op.f('ix_discord_transactions_id'), table_name='discord_transactions')
    op.drop_table('discord_transactions')
    
    op.drop_index(op.f('ix_discord_wallets_user_id'), table_name='discord_wallets')
    op.drop_index(op.f('ix_discord_wallets_id'), table_name='discord_wallets')
    op.drop_table('discord_wallets')
    
    op.drop_index(op.f('ix_discord_users_id'), table_name='discord_users')
    op.drop_index(op.f('ix_discord_users_discord_id'), table_name='discord_users')
    op.drop_table('discord_users')
    
    op.drop_index(op.f('ix_discord_channels_id'), table_name='discord_channels')
    op.drop_table('discord_channels')
    
    op.drop_index(op.f('ix_discord_bots_id'), table_name='discord_bots')
    op.drop_index(op.f('ix_discord_bots_guild_id'), table_name='discord_bots')
    op.drop_table('discord_bots')
    
    # Drop enum types
    op.execute("DROP TYPE IF EXISTS currencytype")
    op.execute("DROP TYPE IF EXISTS discordbotstatus")
