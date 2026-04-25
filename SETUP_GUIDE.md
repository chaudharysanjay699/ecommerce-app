# Complete Setup Guide

This guide covers the complete setup process for migrating the database and creating admin users.

---

## Step 1: Fix Database Permissions

### Problem
Your database user (`vidharthi_user`) does not have permission to create tables in the public schema.

### Solution

Choose one of these methods:

#### Method A: Using PowerShell Script (Recommended)

1. **Ensure PostgreSQL 16.3+ client tools are installed**:
   ```powershell
   # Check if psql is available and its version
   psql --version
   # Expected: psql (PostgreSQL) 16.3 or higher
   
   # If not installed or version is older, download PostgreSQL 16.3+ from:
   # https://www.postgresql.org/download/windows/
   # Note: Only client tools are needed for this script
   ```

2. **Edit the script** (`grant_permissions.ps1`):
   - Open the file
   - Change `$MASTER_USER = "postgres"` to your RDS master user

3. **Run the script**:
   ```powershell
   .\grant_permissions.ps1
   ```
   
4. Enter your RDS master password when prompted

#### Method B: Using pgAdmin or DBeaver

1. Connect to your RDS database with these credentials:
   - **Host**: `vidharthi-store.cn6ms82i6v4t.ap-south-1.rds.amazonaws.com`
   - **Port**: `5432`
   - **Database**: `vidharthi_store`
   - **User**: Your RDS master user (usually `postgres` or `admin`)
   - **Password**: Your RDS master password

2. Open a SQL query window and run the contents of `fix_permissions.sql`:
   ```sql
   GRANT ALL PRIVILEGES ON DATABASE vidharthi_store TO vidharthi_user;
   GRANT USAGE, CREATE ON SCHEMA public TO vidharthi_user;
   GRANT ALL PRIVILEGES ON SCHEMA public TO vidharthi_user;
   ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON TABLES TO vidharthi_user;
   ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON SEQUENCES TO vidharthi_user;
   GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO vidharthi_user;
   GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO vidharthi_user;
   ```

#### Method C: Command Line (Manual)

```powershell
psql -h vidharthi-store.cn6ms82i6v4t.ap-south-1.rds.amazonaws.com -p 5432 -U YOUR_MASTER_USER -d vidharthi_store

# Then run the SQL from fix_permissions.sql
```

---

## Step 2: Run Database Migrations

After fixing permissions, run the migrations:

```powershell
alembic upgrade head
```

**Expected output:**
```
INFO  [alembic.runtime.migration] Context impl PostgresqlImpl.
INFO  [alembic.runtime.migration] Will assume transactional DDL.
INFO  [alembic.runtime.migration] Running upgrade  -> 0001_initial_consolidated, initial
INFO  [alembic.runtime.migration] Running upgrade 0001_initial_consolidated -> 0002_add_order_id_to_notifications, add order_id to notifications
...
```

If you see errors, check:
- Database connection in `.env` is correct
- Permissions were granted successfully
- RDS security group allows your IP

---

## Step 3: Create Admin Users  

Run the admin user creation script:

```powershell
python -m scripts.create_admin
```

**This will create two users:**

### Admin User
- **Phone**: `9999999991`
- **Email**: `admin@vidharthi.com`
- **Password**: `Admin@123`
- **Role**: Admin (can manage products, orders, etc.)

### Super Admin User
- **Phone**: `9999999990`
- **Email**: `superadmin@vidharthi.com`
- **Password**: `SuperAdmin@123`
- **Role**: Super Admin (full access to all features)

> ⚠️ **IMPORTANT**: Change these passwords immediately after first login!

---

## Step 4: Verify Setup

1. **Start your application**:
   ```powershell
   uvicorn app.main:app --reload
   ```

2. **Test login** using the admin credentials

3. **Change the default passwords** through your app's password change feature

---

## Troubleshooting

### Migration: "permission denied for schema public"
- You didn't grant permissions correctly
- Go back to Step 1

### Migration: "could not connect to server"
- Check your `.env` DATABASE_URL
- Verify RDS security group allows your IP
- Ensure RDS instance is running

### Admin creation: "User already exists"
- The script is idempotent (safe to run multiple times)
- If you need to reset a user, delete them from the database first

### Admin creation: "could not connect to database"
- Same troubleshooting as migration connection issues
- Make sure migrations ran successfully first

---

## Summary of Commands

```powershell
# 1. Fix permissions
.\grant_permissions.ps1

# 2. Run migrations
alembic upgrade head

# 3. Create admin users
python -m scripts.create_admin

# 4. Start the app
uvicorn app.main:app --reload
```

---

## Files Created

- `fix_permissions.sql` - SQL commands to grant permissions
- `grant_permissions.ps1` - PowerShell script to connect and grant permissions
- `scripts/create_admin.py` - Script to create admin users
- `FIX_PERMISSIONS_GUIDE.md` - Detailed permission fix guide
- `SETUP_GUIDE.md` - This file

---

## Need Help?

If you encounter issues:

1. Check the RDS security group allows your IP address
2. Verify you're using the correct master user credentials
3. Ensure the database and user exist in AWS RDS
4. Check the `.env` file has the correct DATABASE_URL
5. Look at the full error message for specific issues
