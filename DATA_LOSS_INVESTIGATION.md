# 🚨 DATA LOSS INVESTIGATION - What Could Delete ALL Data?

Based on your logs showing extensive DELETE/CASCADE operations, here are the **ONLY scenarios** that could wipe out all or most of your database data:

---

## ❌ SCENARIO 1: BACKUP RESTORE EXECUTED (MOST LIKELY)

### **What Happens:**
Your backup service creates backups with these flags:
```bash
pg_dump --clean --if-exists
```

This means every backup file contains:
```sql
DROP TABLE IF EXISTS users CASCADE;
DROP TABLE IF EXISTS products CASCADE;
DROP TABLE IF EXISTS orders CASCADE;
-- ... etc for ALL tables

CREATE TABLE users (...);
CREATE TABLE products (...);
-- ... recreates empty tables
```

### **If Someone Restored a Backup:**
```bash
# This command WIPES ALL DATA and restores from backup
psql -h your-db-host -U user -d database -f backup_file.sql
```

**Result:** 
- ALL tables dropped (with CASCADE)
- ALL data deleted
- Tables recreated empty (or with old data from backup)

### **How to Check:**
```bash
# Check if a backup restore was run on May 19th
sudo docker logs ecommerce-app_api_1 --since "2026-05-19T00:00:00" --until "2026-05-19T23:59:59" 2>&1 | \
  grep -i "backup\|restore\|pg_dump\|psql.*-f"

# Check for admin API backup endpoint calls
sudo docker logs ecommerce-app_api_1 --since "2026-05-19T00:00:00" --until "2026-05-19T23:59:59" 2>&1 | \
  grep -i "/admin/backup"

# Check if someone ran psql on EC2
history | grep psql
history | grep backup
```

---

## ❌ SCENARIO 2: DOCKER VOLUME DELETED

### **What Happens:**
If someone ran:
```bash
docker-compose down -v  # The -v flag deletes volumes
docker volume rm postgres_data
docker volume prune
```

**Result:**
- Entire PostgreSQL data directory wiped
- Database starts fresh with empty tables after migrations

### **How to Check:**
```bash
# Check Docker logs for volume operations
docker events --since "2026-05-19T00:00:00" --until "2026-05-19T23:59:59" | grep volume

# Check when the postgres container was created
docker inspect ecommerce-app_db_1 | grep "Created"

# Check volume creation date
docker volume inspect postgres_data | grep "CreatedAt"
```

---

## ❌ SCENARIO 3: ALEMBIC DOWNGRADE TO BASE

### **What Happens:**
If someone ran:
```bash
alembic downgrade base  # Rolls back ALL migrations
```

This executes the `downgrade()` function in each migration, which contains:
```python
def downgrade():
    op.drop_table("wishlist_items")
    op.drop_table("order_items")
    op.drop_table("products")
    op.drop_table("users")
    # ... drops everything
```

**Result:**
- ALL tables dropped in reverse order
- Database completely empty

### **How to Check:**
```bash
# Check if alembic downgrade was run
sudo docker logs ecommerce-app_api_1 --since "2026-05-19T00:00:00" --until "2026-05-19T23:59:59" 2>&1 | \
  grep -i "alembic.*downgrade\|running downgrade"

# Check current migration version
sudo docker exec -it ecommerce-app_api_1 alembic current

# Check migration history
sudo docker exec -it ecommerce-app_api_1 alembic history
```

---

## ❌ SCENARIO 4: DATABASE DROPPED AND RECREATED

### **What Happens:**
Someone connected to PostgreSQL and ran:
```sql
DROP DATABASE vidharthi_store CASCADE;
CREATE DATABASE vidharthi_store;
```

**Result:**
- Entire database wiped
- Migrations re-run creating empty tables

### **How to Check:**
```bash
# Check PostgreSQL logs on RDS
aws rds download-db-log-file-portion \
  --db-instance-identifier vidharthi-store \
  --log-file-name error/postgresql.log.2026-05-19 \
  --output text | grep -i "DROP DATABASE\|CREATE DATABASE"

# Check connection logs
aws rds download-db-log-file-portion \
  --db-instance-identifier vidharthi-store \
  --log-file-name error/postgresql.log.2026-05-19 \
  --output text | grep -i "connection\|disconnect"
```

---

## ❌ SCENARIO 5: MASS CASCADE DELETE (Less Likely)

### **What Happens:**
Someone deleted a critical parent record that had massive CASCADE chains.

**But this is UNLIKELY to wipe ALL data** because:
- Products have `ON DELETE RESTRICT` from orders
- Users have `ON DELETE RESTRICT` from orders
- Categories have `ON DELETE RESTRICT` from products

### **How to Check:**
```bash
# Check for DELETE operations
sudo docker logs ecommerce-app_api_1 --since "2026-05-19T00:00:00" --until "2026-05-19T23:59:59" 2>&1 | \
  grep -i "DELETE FROM\|delete.*cascade"
```

---

## 🔍 COMPLETE DIAGNOSTIC SCRIPT

Run this on your EC2 instance:

```bash
#!/bin/bash
# save as: investigate_may19.sh

echo "🔍 DATA LOSS INVESTIGATION - May 19, 2026"
echo "=========================================="
echo ""

DATE="2026-05-19"
CONTAINER="ecommerce-app_api_1"

echo "1️⃣ Checking for BACKUP RESTORE operations..."
docker logs $CONTAINER --since "${DATE}T00:00:00" --until "${DATE}T23:59:59" 2>&1 | \
  grep -i "backup\|restore\|pg_dump\|psql" | head -20
echo ""

echo "2️⃣ Checking for ALEMBIC downgrade..."
docker logs $CONTAINER --since "${DATE}T00:00:00" --until "${DATE}T23:59:59" 2>&1 | \
  grep -i "alembic.*downgrade\|running downgrade" | head -20
echo ""

echo "3️⃣ Checking for DROP TABLE operations..."
docker logs $CONTAINER --since "${DATE}T00:00:00" --until "${DATE}T23:59:59" 2>&1 | \
  grep -i "DROP TABLE\|DROP IF EXISTS" | head -20
echo ""

echo "4️⃣ Checking for admin backup API calls..."
docker logs $CONTAINER --since "${DATE}T00:00:00" --until "${DATE}T23:59:59" 2>&1 | \
  grep -i "POST /api/v1/admin/backup\|GET /api/v1/admin/backup" | head -20
echo ""

echo "5️⃣ Checking DELETE operations count..."
DELETE_COUNT=$(docker logs $CONTAINER --since "${DATE}T00:00:00" --until "${DATE}T23:59:59" 2>&1 | grep -ic "delete")
echo "Total DELETE mentions: $DELETE_COUNT"
echo ""

echo "6️⃣ Checking CASCADE operations count..."
CASCADE_COUNT=$(docker logs $CONTAINER --since "${DATE}T00:00:00" --until "${DATE}T23:59:59" 2>&1 | grep -ic "cascade")
echo "Total CASCADE mentions: $CASCADE_COUNT"
echo ""

echo "7️⃣ Checking container restart time..."
docker inspect $CONTAINER | grep -E "StartedAt|State"
echo ""

echo "8️⃣ Checking Docker volume creation date..."
docker volume inspect postgres_data 2>/dev/null | grep CreatedAt || echo "Volume not found or using RDS"
echo ""

echo "9️⃣ Current Alembic migration version..."
docker exec -it $CONTAINER alembic current 2>/dev/null || echo "Could not check alembic"
echo ""

echo "🔟 Recent bash history (manual commands)..."
history | grep -iE "psql|backup|restore|alembic|docker.*down.*-v" | tail -10
echo ""

echo "✅ Investigation complete!"
echo ""
echo "📋 NEXT STEPS:"
echo "1. Look for 'DROP TABLE IF EXISTS' statements in logs"
echo "2. Check if backup restore was executed"
echo "3. Verify Docker volume wasn't deleted"
echo "4. Check RDS logs for database-level operations"
```

---

## 🎯 MOST LIKELY CULPRIT

Based on your backup service configuration with `--clean --if-exists` flags:

### **Someone probably restored a backup on May 19th**

This would cause:
1. ✅ DROP TABLE IF EXISTS for ALL tables (with CASCADE)
2. ✅ Massive CASCADE delete operations in logs
3. ✅ All data wiped
4. ✅ Tables recreated (empty or with old data)

---

## 🛠️ HOW TO PREVENT THIS

### 1. **Remove --clean flag from backup creation**

Edit [app/services/backup_service.py](app/services/backup_service.py#L135):

```python
# BEFORE (line 135)
"--clean",  # Add DROP commands before CREATE commands

# AFTER (remove this line completely)
# "--clean",  # REMOVED - dangerous for restores
```

### 2. **Add confirmation for restore operations**

Create a separate restore function that:
- Requires explicit confirmation
- Creates backup before restore
- Logs all restore operations
- Restricts restore to super admins only

### 3. **Audit backup API access**

Add logging to backup endpoints:
```python
logger.warning(f"CRITICAL: Backup restore requested by user {user.id} at {datetime.now()}")
```

### 4. **Enable PostgreSQL query logging on RDS**

In AWS RDS parameter group:
```
log_statement = 'ddl'  # Log all DROP/CREATE statements
log_min_duration_statement = 0  # Log all queries
```

---

## ✅ ACTION PLAN

1. **Run the diagnostic script above**
2. **Search for "DROP TABLE IF EXISTS" in logs**
3. **Check who accessed the backup API on May 19th**
4. **Review RDS connection logs**
5. **Remove --clean flag from backup service**
6. **Implement backup restore audit trail**

---

## 📞 IMMEDIATE COMMAND TO RUN

```bash
# This will show you EXACTLY what happened
sudo docker logs ecommerce-app_api_1 --since "2026-05-19T00:00:00" --until "2026-05-19T23:59:59" 2>&1 | \
  grep -i "DROP TABLE\|DROP IF EXISTS\|backup\|restore" -B10 -A10 | \
  tee critical_operations_may19.log

# Then search for the actual SQL statements
cat critical_operations_may19.log | grep -i "DROP\|CASCADE"
```

If you see **"DROP TABLE IF EXISTS"** statements in the output, **a backup was restored and that's what wiped your data**.
