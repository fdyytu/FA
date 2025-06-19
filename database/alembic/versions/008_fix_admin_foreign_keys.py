"""fix admin foreign keys

Revision ID: 008_fix_admin_foreign_keys
Revises: 007_add_discord_config_table
Create Date: 2025-06-15 17:15:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '008_fix_admin_foreign_keys'
down_revision = '007_add_discord_config_table'
branch_labels = None
depends_on = None


def upgrade():
    """Add foreign key constraints to admin related tables"""
    
    # Add foreign key constraint to admin_audit_logs table
    try:
        op.create_foreign_key(
            'fk_admin_audit_logs_admin_id',
            'admin_audit_logs',
            'admins',
            ['admin_id'],
            ['id'],
            ondelete='CASCADE'
        )
    except Exception as e:
        print(f"Warning: Could not add foreign key to admin_audit_logs: {e}")
    
    # Add foreign key constraint to admin_notification_settings table
    try:
        op.create_foreign_key(
            'fk_admin_notification_settings_admin_id',
            'admin_notification_settings',
            'admins',
            ['admin_id'],
            ['id'],
            ondelete='CASCADE'
        )
    except Exception as e:
        print(f"Warning: Could not add foreign key to admin_notification_settings: {e}")


def downgrade():
    """Remove foreign key constraints"""
    
    # Remove foreign key constraint from admin_notification_settings table
    try:
        op.drop_constraint('fk_admin_notification_settings_admin_id', 'admin_notification_settings', type_='foreignkey')
    except Exception as e:
        print(f"Warning: Could not remove foreign key from admin_notification_settings: {e}")
    
    # Remove foreign key constraint from admin_audit_logs table
    try:
        op.drop_constraint('fk_admin_audit_logs_admin_id', 'admin_audit_logs', type_='foreignkey')
    except Exception as e:
        print(f"Warning: Could not remove foreign key from admin_audit_logs: {e}")
