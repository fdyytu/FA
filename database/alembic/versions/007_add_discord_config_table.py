"""Add discord_configs table

Revision ID: 007_add_discord_config_table
Revises: 006_add_discord_tables
Create Date: 2024-06-14 18:56:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '007_add_discord_config_table'
down_revision = '006_add_discord_tables'
branch_labels = None
depends_on = None


def upgrade():
    """Create discord_configs table"""
    op.create_table('discord_configs',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('token', sa.Text(), nullable=False),
        sa.Column('guild_id', sa.String(length=50), nullable=True),
        sa.Column('command_prefix', sa.String(length=10), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=True),
        sa.Column('is_encrypted', sa.Boolean(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_discord_configs_id'), 'discord_configs', ['id'], unique=False)
    
    # Set default values
    op.execute("ALTER TABLE discord_configs ALTER COLUMN name SET DEFAULT 'Default Config'")
    op.execute("ALTER TABLE discord_configs ALTER COLUMN command_prefix SET DEFAULT '!'")
    op.execute("ALTER TABLE discord_configs ALTER COLUMN is_active SET DEFAULT true")
    op.execute("ALTER TABLE discord_configs ALTER COLUMN is_encrypted SET DEFAULT true")


def downgrade():
    """Drop discord_configs table"""
    op.drop_index(op.f('ix_discord_configs_id'), table_name='discord_configs')
    op.drop_table('discord_configs')
