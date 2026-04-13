"""
Drop old unique indexes on users.phone and users.email (ix_users_phone, ix_users_email)
that conflict with the new partial unique indexes.

Revision ID: 0012_drop_old_idx
Revises: 0011_soft_delete
Create Date: 2026-04-14 00:00:00.000000

"""
from alembic import op

# revision identifiers, used by Alembic.
revision = '0012_drop_old_idx'
down_revision = '0011_soft_delete'
branch_labels = None
depends_on = None


def upgrade():
    # Drop old column-level indexes that enforce full uniqueness
    op.execute("""
        DO $$
        BEGIN
            -- Drop ix_users_phone if it exists
            IF EXISTS (
                SELECT 1 FROM pg_indexes WHERE indexname = 'ix_users_phone' AND tablename = 'users'
            ) THEN
                DROP INDEX ix_users_phone;
            END IF;

            -- Drop ix_users_email if it exists
            IF EXISTS (
                SELECT 1 FROM pg_indexes WHERE indexname = 'ix_users_email' AND tablename = 'users'
            ) THEN
                DROP INDEX ix_users_email;
            END IF;
        END
        $$;
    """)


def downgrade():
    op.create_index('ix_users_phone', 'users', ['phone'], unique=True)
    op.create_index('ix_users_email', 'users', ['email'], unique=True)
