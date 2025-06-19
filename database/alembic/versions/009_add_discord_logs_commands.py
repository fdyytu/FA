"""Add Discord logs and commands tables

Revision ID: 009_add_discord_logs_commands
Revises: 008_fix_admin_foreign_keys
Create Date: 2024-06-16 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '009_add_discord_logs_commands'
down_revision = '003_add_discord_models'
branch_labels = None
depends_on = None

def upgrade():
    # Create discord_logs table
    op.create_table('discord_logs',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=True),
        sa.Column('bot_id', sa.Integer(), nullable=True),
        sa.Column('level', sa.String(length=20), nullable=False, server_default='INFO'),
        sa.Column('message', sa.Text(), nullable=False),
        sa.Column('action', sa.String(length=100), nullable=True),
        sa.Column('channel_id', sa.String(length=50), nullable=True),
        sa.Column('guild_id', sa.String(length=50), nullable=True),
        sa.Column('error_details', sa.Text(), nullable=True),
        sa.Column('metadata', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.ForeignKeyConstraint(['user_id'], ['discord_users.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['bot_id'], ['discord_bots.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_discord_logs_id'), 'discord_logs', ['id'], unique=False)
    op.create_index(op.f('ix_discord_logs_level'), 'discord_logs', ['level'], unique=False)
    op.create_index(op.f('ix_discord_logs_action'), 'discord_logs', ['action'], unique=False)
    op.create_index(op.f('ix_discord_logs_created_at'), 'discord_logs', ['created_at'], unique=False)

    # Create discord_commands table
    op.create_table('discord_commands',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=True),
        sa.Column('command_name', sa.String(length=100), nullable=False),
        sa.Column('command_args', sa.Text(), nullable=True),
        sa.Column('channel_id', sa.String(length=50), nullable=False),
        sa.Column('guild_id', sa.String(length=50), nullable=False),
        sa.Column('success', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('execution_time', sa.Numeric(precision=10, scale=4), nullable=True),
        sa.Column('error_message', sa.Text(), nullable=True),
        sa.Column('response_message', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.ForeignKeyConstraint(['user_id'], ['discord_users.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_discord_commands_id'), 'discord_commands', ['id'], unique=False)
    op.create_index(op.f('ix_discord_commands_command_name'), 'discord_commands', ['command_name'], unique=False)
    op.create_index(op.f('ix_discord_commands_success'), 'discord_commands', ['success'], unique=False)
    op.create_index(op.f('ix_discord_commands_created_at'), 'discord_commands', ['created_at'], unique=False)

    # Create discord_bot_status table
    op.create_table('discord_bot_status',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('bot_id', sa.Integer(), nullable=False),
        sa.Column('status', sa.String(length=20), nullable=False),
        sa.Column('latency', sa.Numeric(precision=10, scale=4), nullable=True),
        sa.Column('guild_count', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('user_count', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('uptime', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('memory_usage', sa.Numeric(precision=10, scale=2), nullable=True),
        sa.Column('cpu_usage', sa.Numeric(precision=5, scale=2), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.ForeignKeyConstraint(['bot_id'], ['discord_bots.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_discord_bot_status_id'), 'discord_bot_status', ['id'], unique=False)
    op.create_index(op.f('ix_discord_bot_status_bot_id'), 'discord_bot_status', ['bot_id'], unique=False)
    op.create_index(op.f('ix_discord_bot_status_created_at'), 'discord_bot_status', ['created_at'], unique=False)

def downgrade():
    # Drop tables in reverse order
    op.drop_index(op.f('ix_discord_bot_status_created_at'), table_name='discord_bot_status')
    op.drop_index(op.f('ix_discord_bot_status_bot_id'), table_name='discord_bot_status')
    op.drop_index(op.f('ix_discord_bot_status_id'), table_name='discord_bot_status')
    op.drop_table('discord_bot_status')
    
    op.drop_index(op.f('ix_discord_commands_created_at'), table_name='discord_commands')
    op.drop_index(op.f('ix_discord_commands_success'), table_name='discord_commands')
    op.drop_index(op.f('ix_discord_commands_command_name'), table_name='discord_commands')
    op.drop_index(op.f('ix_discord_commands_id'), table_name='discord_commands')
    op.drop_table('discord_commands')
    
    op.drop_index(op.f('ix_discord_logs_created_at'), table_name='discord_logs')
    op.drop_index(op.f('ix_discord_logs_action'), table_name='discord_logs')
    op.drop_index(op.f('ix_discord_logs_level'), table_name='discord_logs')
    op.drop_index(op.f('ix_discord_logs_id'), table_name='discord_logs')
    op.drop_table('discord_logs')
