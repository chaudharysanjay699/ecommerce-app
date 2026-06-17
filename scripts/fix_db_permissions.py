"""
Fix database permissions for app user.

Run this script as:
    python scripts/fix_db_permissions.py

You will be prompted for the postgres master password.
"""
import asyncio
import getpass
import sys

import asyncpg

# ── Config ────────────────────────────────────────────────────────────────────
RDS_HOST     = "vidharthi-store.cn6ms82i6v4t.ap-south-1.rds.amazonaws.com"
RDS_PORT     = 5432
RDS_DATABASE = "vidharthi_store"          # <-- change to your new database name
APP_USER     = "readonly_vidharthi_store"  # <-- user the app connects as
APP_PASSWORD = "vidharthi123"              # <-- user password
# ─────────────────────────────────────────────────────────────────────────────


async def fix_permissions(postgres_password: str) -> None:
    print(f"\nConnecting to {RDS_HOST}/{RDS_DATABASE} as postgres...")

    try:
        conn = await asyncpg.connect(
            host=RDS_HOST,
            port=RDS_PORT,
            database=RDS_DATABASE,
            user="postgres",
            password=postgres_password,
            ssl="require",
        )
    except Exception as e:
        print(f"\n❌ Connection failed: {e}")
        print("   → Check your postgres password and that the RDS instance is reachable.")
        sys.exit(1)

    print("✅ Connected as postgres\n")

    # ── Step 0: Create user if it doesn't exist ──────────────────────────────
    print("── Creating/checking app user ───────────────────────────────────")
    try:
        # Check if user exists
        user_exists = await conn.fetchval(
            "SELECT 1 FROM pg_user WHERE usename = $1", APP_USER
        )
        if not user_exists:
            # Create user with password
            await conn.execute(
                f"CREATE USER {APP_USER} WITH PASSWORD '{APP_PASSWORD}'"
            )
            print(f"  ✅ Created user '{APP_USER}'")
        else:
            print(f"  ✅ User '{APP_USER}' already exists")
    except Exception as e:
        print(f"  ⚠️  User creation: {e}")


    # ── Step 1: Revoke dangerous privileges first ─────────────────────────────
    print("── Revoking dangerous privileges ─────────────────────────────────")
    revoke_commands = [
        ("REVOKE CREATE on SCHEMA (no new tables)",
         f"REVOKE CREATE ON SCHEMA public FROM {APP_USER}"),

        ("REVOKE DELETE on ALL TABLES",
         f"REVOKE DELETE ON ALL TABLES IN SCHEMA public FROM {APP_USER}"),

        ("REVOKE TRUNCATE on ALL TABLES",
         f"REVOKE TRUNCATE ON ALL TABLES IN SCHEMA public FROM {APP_USER}"),

        ("REVOKE REFERENCES on ALL TABLES",
         f"REVOKE REFERENCES ON ALL TABLES IN SCHEMA public FROM {APP_USER}"),

        ("REVOKE TRIGGER on ALL TABLES",
         f"REVOKE TRIGGER ON ALL TABLES IN SCHEMA public FROM {APP_USER}"),
    ]

    for label, sql in revoke_commands:
        try:
            await conn.execute(sql)
            print(f"  ✅ {label}")
        except Exception as e:
            print(f"  ⚠️  {label}: {e}")

    # ── Step 2: Grant only SELECT, INSERT, UPDATE ─────────────────────────────
    print("\n── Granting SELECT, INSERT, UPDATE only ──────────────────────────")
    commands = [
        ("GRANT USAGE ON SCHEMA",
         f"GRANT USAGE ON SCHEMA public TO {APP_USER}"),

        ("GRANT SELECT/INSERT/UPDATE on ALL TABLES",
         f"GRANT SELECT, INSERT, UPDATE ON ALL TABLES IN SCHEMA public TO {APP_USER}"),

        ("GRANT SELECT/INSERT/UPDATE/DELETE on transactional tables (cart_items, otps, device_tokens, notifications, uploaded_files, wishlist_items)",
         f"GRANT SELECT, INSERT, UPDATE, DELETE ON TABLE cart_items, otps, device_tokens, notifications, uploaded_files, wishlist_items TO {APP_USER}"),

        ("GRANT USAGE/SELECT/UPDATE on ALL SEQUENCES",
         f"GRANT USAGE, SELECT, UPDATE ON ALL SEQUENCES IN SCHEMA public TO {APP_USER}"),

        ("ALTER DEFAULT PRIVILEGES - tables",
         f"ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT SELECT, INSERT, UPDATE ON TABLES TO {APP_USER}"),

        ("ALTER DEFAULT PRIVILEGES - sequences",
         f"ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT USAGE, SELECT, UPDATE ON SEQUENCES TO {APP_USER}"),
    ]

    for label, sql in commands:
        try:
            await conn.execute(sql)
            print(f"  ✅ {label}")
        except Exception as e:
            print(f"  ❌ {label}: {e}")

    # ── Verify ────────────────────────────────────────────────────────────────
    print("\n── Verifying permissions ─────────────────────────────────────────")
    rows = await conn.fetch(
        """
        SELECT table_name, string_agg(privilege_type, ', ' ORDER BY privilege_type) AS privileges
        FROM   information_schema.role_table_grants
        WHERE  grantee     = $1
          AND  table_schema = 'public'
        GROUP  BY table_name
        ORDER  BY table_name
        """,
        APP_USER,
    )

    if rows:
        print(f"\n✅ Permissions granted to '{APP_USER}':\n")
        for row in rows:
            print(f"   {row['table_name']:<30} {row['privileges']}")
    else:
        print(f"\n❌ Still no permissions visible for '{APP_USER}'.")
        print("   → Check that the tables exist and were created by the postgres user.")

        # Extra diagnostic
        tables = await conn.fetch(
            "SELECT tablename, tableowner FROM pg_tables WHERE schemaname = 'public' ORDER BY tablename"
        )
        if tables:
            print("\n   Tables and their owners:")
            for t in tables:
                print(f"   {t['tablename']:<30} owner: {t['tableowner']}")
        else:
            print("   No tables found in public schema — database may be empty.")

    await conn.close()
    print("\nDone.")


def main() -> None:
    print("=== Fix DB Permissions Script ===")
    print(f"Target DB   : {RDS_DATABASE} @ {RDS_HOST}")
    print(f"App user    : {APP_USER}")
    print(f"Admin user  : postgres\n")

    password = getpass.getpass("Enter postgres master password: ")

    asyncio.run(fix_permissions(password))


if __name__ == "__main__":
    main()
