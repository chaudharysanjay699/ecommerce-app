"""
Add soft delete (is_deleted, deleted_at) and super admin (is_super_admin) to users.
Replace column-level unique constraints on phone/email with partial unique indexes
so that deleted users' phone/email can be reused.

Revision ID: 0011_add_soft_delete_and_super_admin
Revises: 0010_add_low_stock_alert
Create Date: 2026-04-13 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '0011_soft_delete'
down_revision = '0010_add_low_stock_alert'
branch_labels = None
depends_on = None


def upgrade():
    # Add new columns
    op.add_column('users', sa.Column('is_super_admin', sa.Boolean(), server_default=sa.text('false'), nullable=False))
    op.add_column('users', sa.Column('is_deleted', sa.Boolean(), server_default=sa.text('false'), nullable=False))
    op.add_column('users', sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True))

    # Drop old unique constraints on phone and email (if they exist)
    op.execute("""
        DO $$
        BEGIN
            -- Drop phone constraint if it exists
            IF EXISTS (
                SELECT 1 FROM pg_constraint WHERE conname = 'users_phone_key' AND conrelid = 'users'::regclass
            ) THEN
                ALTER TABLE users DROP CONSTRAINT users_phone_key;
            END IF;
            
            -- Drop email constraint if it exists
            IF EXISTS (
                SELECT 1 FROM pg_constraint WHERE conname = 'users_email_key' AND conrelid = 'users'::regclass
            ) THEN
                ALTER TABLE users DROP CONSTRAINT users_email_key;
            END IF;
        END
        $$;
    """)

    # Create partial unique indexes (PostgreSQL) — only enforce uniqueness for non-deleted users
    op.execute(
        "CREATE UNIQUE INDEX IF NOT EXISTS uq_users_phone_active ON users (phone) WHERE is_deleted = false"
    )
    op.execute(
        "CREATE UNIQUE INDEX IF NOT EXISTS uq_users_email_active ON users (email) WHERE is_deleted = false AND email IS NOT NULL"
    )


def downgrade():
    # Drop partial unique indexes
    op.drop_index('uq_users_email_active', table_name='users')
    op.drop_index('uq_users_phone_active', table_name='users')

    # Restore original unique constraints
    op.create_unique_constraint('users_phone_key', 'users', ['phone'])
    op.create_unique_constraint('users_email_key', 'users', ['email'])

    # Remove columns
    op.drop_column('users', 'deleted_at')
    op.drop_column('users', 'is_deleted')
    op.drop_column('users', 'is_super_admin')
