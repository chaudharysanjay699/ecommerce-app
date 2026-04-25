# Fix PostgreSQL Permission Denied Error

## Problem
The database user `vidharthi_user` does not have permission to create tables in the public schema on your AWS RDS database.

## Solution

### Option 1: Using PowerShell Script (Recommended)

1. **Install PostgreSQL client tools** (if not already installed):
   - Download from: https://www.postgresql.org/download/windows/
   - Or install via Chocolatey: `choco install postgresql`

2. **Update the master username** in `grant_permissions.ps1`:
   - Open `grant_permissions.ps1`
   - Change `$MASTER_USER = "postgres"` to your actual RDS master user

3. **Run the script**:
   ```powershell
   .\grant_permissions.ps1
   ```
   
4. **Enter the master user password** when prompted

5. **Run the migration**:
   ```powershell
   alembic upgrade head
   ```

---

### Option 2: Using a Database GUI Tool

If you prefer using a GUI tool like pgAdmin, DBeaver, or DataGrip:

1. **Connect to your RDS database as the master user**:
   - Host: `vidharthi-store.cn6ms82i6v4t.ap-south-1.rds.amazonaws.com`
   - Port: `5432`
   - Database: `vidharthi_store`
   - User: Your RDS master user (e.g., `postgres` or `admin`)

2. **Run the SQL commands** from `fix_permissions.sql`:
   ```sql
   GRANT ALL PRIVILEGES ON DATABASE vidharthi_store TO vidharthi_user;
   GRANT USAGE, CREATE ON SCHEMA public TO vidharthi_user;
   GRANT ALL PRIVILEGES ON SCHEMA public TO vidharthi_user;
   ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON TABLES TO vidharthi_user;
   ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON SEQUENCES TO vidharthi_user;
   GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO vidharthi_user;
   GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO vidharthi_user;
   ```

3. **Run the migration**:
   ```powershell
   alembic upgrade head
   ```

---

### Option 3: Using psql Command Directly

```powershell
psql -h vidharthi-store.cn6ms82i6v4t.ap-south-1.rds.amazonaws.com -p 5432 -U postgres -d vidharthi_store -f fix_permissions.sql
```

Replace `postgres` with your actual RDS master user.

---

## Troubleshooting

### "psql: command not found"
- Install PostgreSQL client tools (see Option 1, step 1)

### "Connection timeout" or "Could not connect"
- Check your RDS security group allows your IP address
- Verify the database endpoint is correct
- Ensure the RDS instance is publicly accessible (if connecting from outside AWS)

### "FATAL: password authentication failed"
- Double-check you're using the master user credentials
- Reset the master password in AWS RDS console if needed

---

## After Fixing Permissions

Once permissions are granted, you can proceed with:

1. **Run migrations**:
   ```powershell
   alembic upgrade head
   ```

2. **Create admin user** - See the script section below

3. **Create super admin user** - See the script section below

---

## Next Steps: Create Admin Users

After the migration succeeds, I'll help you create the admin and super admin users.
