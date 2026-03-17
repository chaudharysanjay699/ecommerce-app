from logging.config import fileConfig

import sqlalchemy as sa
from sqlalchemy import engine_from_config, pool

from alembic import context

# ── Import all models so Alembic can detect them ─────────────────────────────
from app.core.database import Base
from app.core.config import settings
import app.models  # noqa: F401 – registers all ORM models

config = context.config

# Override sqlalchemy.url from .env (via pydantic settings) so it is
# never necessary to keep alembic.ini in sync with .env.
config.set_main_option("sqlalchemy.url", settings.DATABASE_URL)

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata


def run_migrations_offline() -> None:
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        compare_type=True,
    )
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    # Use a sync engine for alembic (asyncpg driver needs special handling)
    sync_url = config.get_main_option("sqlalchemy.url").replace(
        "postgresql+asyncpg", "postgresql+psycopg2"
    )
    configuration = config.get_section(config.config_ini_section, {})
    configuration["sqlalchemy.url"] = sync_url

    connectable = engine_from_config(
        configuration,
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )
    with connectable.connect() as connection:
        # Ensure the public schema exists (may fail on managed DBs with restricted perms)
        try:
            connection.execute(sa.text("CREATE SCHEMA IF NOT EXISTS public"))
            connection.commit()
        except Exception:
            connection.rollback()

        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            compare_type=True,
        )
        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
