# Application Stability Fixes - Deployment Guide

## Issues Identified and Fixed

### 1. **Background Task Crashes** ❌ → ✅
**Problem:** Background tasks using `asyncio.create_task()` were failing silently and could crash the entire application.

**Solution:** 
- Created `app/utils/background_tasks.py` with `create_safe_task()` function
- All background tasks now log exceptions instead of crashing
- Task references are tracked to prevent garbage collection
- Tasks can be gracefully awaited during shutdown

### 2. **Weak Exception Handling** ❌ → ✅
**Problem:** Middleware had minimal error logging and could crash on unhandled exceptions.

**Solution:**
- Enhanced `app/core/middleware.py` with comprehensive exception handling
- Added specific handlers for database errors (OperationalError, DBAPIError)
- All exceptions now logged with full traceback
- Returns proper JSON responses instead of generic errors

### 3. **Database Connection Issues** ❌ → ✅
**Problem:** Database connections could fail without proper recovery, causing cascading failures.

**Solution:**
- Enhanced `app/core/database.py` with robust connection pooling
- Added `pool_pre_ping=True` to verify connections before use
- Added `pool_recycle=3600` to recycle stale connections
- Added proper session cleanup in finally block
- Increased pool timeout to 30 seconds

### 4. **Missing Global Exception Handlers** ❌ → ✅
**Problem:** No catch-all handlers for validation errors and unexpected exceptions.

**Solution:**
- Added global `RequestValidationError` handler
- Added global `Exception` handler as last resort
- All unhandled exceptions now logged and return proper JSON responses

### 5. **File Permission Errors** ❌ → ✅
**Problem:** Log directory creation could fail due to permissions, crashing startup.

**Solution:**
- Added try-except around log directory creation
- Graceful fallback to stdout-only logging
- Uses UTF-8 encoding for log files
- Never crashes on permission errors

### 6. **No Graceful Shutdown** ❌ → ✅
**Problem:** Background tasks could be interrupted without proper cleanup.

**Solution:**
- Enhanced lifespan manager with proper startup/shutdown
- Waits for background tasks to complete (10s timeout)
- Closes database connections cleanly
- Logs all shutdown steps

### 7. **Poor Health Check** ❌ → ✅
**Problem:** Health check didn't verify database connectivity.

**Solution:**
- Enhanced `/health` endpoint tests database connection
- Returns "degraded" status if database is unavailable
- Useful for AWS load balancer health checks

## Files Changed

```
✓ app/core/middleware.py          - Enhanced error handling
✓ app/core/database.py             - Robust connection pooling
✓ app/main.py                      - Global handlers & lifespan
✓ app/services/order_service.py    - Safe background tasks
✓ app/utils/background_tasks.py    - NEW: Safe task runner
✓ DEPLOYMENT_FIXES.md              - This file
```

## Deployment Steps for AWS EC2

### Step 1: Pull Latest Code
```bash
cd /path/to/your/app
git pull origin main
```

### Step 2: Fix Log Directory Permissions
```bash
# Create logs directory with proper permissions
sudo mkdir -p logs
sudo chown -R $USER:$USER logs
sudo chmod -R 755 logs

# OR if running in Docker
docker exec -it <container_id> mkdir -p /app/logs
docker exec -it <container_id> chmod 777 /app/logs
```

### Step 3: Update Docker Compose (if using)
Add volume mount for logs:
```yaml
services:
  app:
    volumes:
      - ./logs:/app/logs
```

### Step 4: Restart Application
```bash
# If using Docker
docker-compose down
docker-compose up -d --build

# If running directly
sudo systemctl restart your-app-service
```

### Step 5: Verify Health
```bash
curl http://localhost:8000/health

# Expected response:
# {
#   "status": "ok",
#   "version": "1.0.0",
#   "app_name": "Vidharthi Store",
#   "database": "connected"
# }
```

### Step 6: Monitor Logs
```bash
# Docker
docker logs -f <container_id>

# Direct
tail -f logs/app.log
```

## Monitoring Recommendations

### 1. Set up Log Rotation
```bash
# Create /etc/logrotate.d/your-app
sudo nano /etc/logrotate.d/your-app

# Add:
/path/to/app/logs/*.log {
    daily
    rotate 7
    compress
    delaycompress
    missingok
    notifempty
    create 0640 ubuntu ubuntu
}
```

### 2. Monitor Application Health
Set up AWS CloudWatch or a cron job:
```bash
# Add to crontab
*/5 * * * * curl -f http://localhost:8000/health || echo "App down!" | mail -s "Alert" admin@example.com
```

### 3. Set up Database Connection Monitoring
Watch for these log messages:
- `"Database connection failed during startup"`
- `"Database session error"`
- `"Database connection error on"`

### 4. Track Background Task Failures
Watch for these log messages:
- `"Background task '...' failed with exception"`
- These will now be logged instead of crashing the app

### 5. AWS CloudWatch Alarms (Recommended)
- CPU > 80% for 5 minutes
- Memory > 85% for 5 minutes
- Health check failures
- Error log count spikes

## What Changed in Code Behavior

### Before:
```python
# ❌ Could crash the entire app
asyncio.create_task(_post_order_tasks())
```

### After:
```python
# ✅ Logs errors, never crashes
create_safe_task(_post_order_tasks(), task_name="post_order_tasks_123")
```

### Before:
```python
# ❌ Generic "Internal server error"
except Exception as exc:
    return Response("Internal server error", status_code=500)
```

### After:
```python
# ✅ Detailed logging & proper JSON response
except Exception as exc:
    logger.error("Unhandled exception: %s", exc, exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "detail": "An unexpected error occurred. The issue has been logged.",
            "error_type": type(exc).__name__,
        }
    )
```

## Expected Improvements

1. **No More Silent Crashes** - All errors are logged
2. **Better Error Messages** - Users get proper JSON responses
3. **Database Resilience** - Handles connection issues gracefully  
4. **Graceful Shutdown** - Background tasks complete properly
5. **Better Monitoring** - Health endpoint shows real status
6. **Production Ready** - Handles edge cases without crashing

## Testing Checklist

After deployment, verify:

- [ ] Application starts without errors
- [ ] `/health` endpoint returns proper status
- [ ] Log file is being created and written to
- [ ] Order creation works (tests background tasks)
- [ ] Database connection errors are handled gracefully
- [ ] Application doesn't crash on any API call
- [ ] Background tasks run and log appropriately
- [ ] Application survives database connection drops
- [ ] Graceful shutdown works (stop/restart)

## Rollback Plan

If issues occur:
```bash
git checkout <previous_commit>
docker-compose down
docker-compose up -d --build
```

## Support & Debugging

If the app still stops:

1. Check logs: `docker logs <container_id> --tail 100`
2. Check health: `curl http://localhost:8000/health`
3. Check database: `docker exec -it <container_id> psql -U user -d dbname -c "SELECT 1;"`
4. Check disk space: `df -h`
5. Check memory: `free -m`
6. Check Docker stats: `docker stats <container_id>`

## Questions?

All exceptions are now logged with full tracebacks. If you see any uncaught exceptions in the logs, they indicate areas that need additional specific handling.
