# Safe Background Tasks - Usage Guide

## Why This Exists

Background tasks in FastAPI using `asyncio.create_task()` can fail silently and crash your application. This utility ensures all background tasks log exceptions instead of crashing the app.

## Usage

### Before (❌ Dangerous)
```python
import asyncio

async def send_email():
    # If this raises an exception, it could crash the app
    await email_service.send(...)

# Fire and forget - no error handling
asyncio.create_task(send_email())
```

### After (✅ Safe)
```python
from app.utils.background_tasks import create_safe_task

async def send_email():
    # If this raises an exception, it's logged but app continues
    await email_service.send(...)

# Safe execution with error logging
create_safe_task(send_email(), task_name="send_email_user_123")
```

## API Reference

### `create_safe_task(coro, *, task_name="background_task")`

Creates a background task that logs exceptions instead of crashing.

**Parameters:**
- `coro`: The coroutine to run (async function call)
- `task_name`: Descriptive name for logging (helps with debugging)

**Returns:**
- `asyncio.Task`: The created task (usually ignored)

**Example:**
```python
from app.utils.background_tasks import create_safe_task

async def process_order(order_id: int):
    # Your async processing logic
    await generate_pdf(order_id)
    await send_notifications(order_id)
    # etc.

# Schedule it
create_safe_task(
    process_order(order_id=123),
    task_name=f"process_order_{123}"
)
```

### `wait_for_background_tasks(timeout=30.0)`

Waits for all background tasks to complete (used during shutdown).

**Parameters:**
- `timeout`: Max seconds to wait (default: 30)

**Example:**
```python
from app.utils.background_tasks import wait_for_background_tasks

# During application shutdown
await wait_for_background_tasks(timeout=10.0)
```

## Best Practices

### 1. ✅ Use Descriptive Task Names
```python
# Good
create_safe_task(
    send_invoice_email(order.id, user.email),
    task_name=f"invoice_email_order_{order.id}"
)

# Bad
create_safe_task(send_invoice_email(order.id, user.email))
```

### 2. ✅ Include Identifiers in Task Names
```python
# Good - includes order ID for debugging
task_name = f"post_order_tasks_{order_id}"

# Bad - generic name
task_name = "background_task"
```

### 3. ✅ Keep Background Tasks Short
```python
# Good - quick operations
async def send_notification():
    await push_service.send(...)  # < 5 seconds

# Consider celery/redis for long tasks
async def generate_complex_report():
    for i in range(10000):  # Could take minutes
        ...  # Use proper background job queue instead
```

### 4. ✅ Don't Await Background Tasks
```python
# Good - fire and forget
create_safe_task(cleanup_old_files(), task_name="cleanup")
# ... rest of your code continues immediately

# Bad - defeats the purpose
task = create_safe_task(cleanup_old_files(), task_name="cleanup")
await task  # Don't do this! Use regular await instead
```

### 5. ✅ Log Task Completion in Critical Cases
```python
async def critical_notification_task():
    try:
        await send_critical_alert()
        logger.info("Critical alert sent successfully")
    except Exception as e:
        logger.error("CRITICAL: Failed to send alert - %s", e)
        # Maybe send to fallback channel

create_safe_task(
    critical_notification_task(),
    task_name="critical_alert"
)
```

## What Happens When a Task Fails?

Before (❌):
```
[No log entry]
[App crashes or becomes unstable]
```

After (✅):
```
2026-04-26 14:23:45 - app.utils.background_tasks - ERROR - Background task 'send_email_order_123' failed with exception (app continues running)
Traceback (most recent call last):
  File "/app/utils/background_tasks.py", line 23, in _safe_wrapper
    await coro
  File "/app/services/email.py", line 45, in send_email
    ...
SMTPException: Connection refused
```

## Migration Checklist

To migrate existing code:

1. Import the utility:
   ```python
   from app.utils.background_tasks import create_safe_task
   ```

2. Find all `asyncio.create_task()` calls:
   ```bash
   grep -r "asyncio.create_task" app/
   ```

3. Replace with `create_safe_task()`:
   ```python
   # Before
   asyncio.create_task(my_async_function())
   
   # After
   create_safe_task(
       my_async_function(),
       task_name="my_async_function"
   )
   ```

4. Add descriptive task names with IDs where applicable

## Already Migrated

The following services have been updated:

- ✅ `app/services/order_service.py` - All 4 background task calls
  - `post_order_tasks_{order_id}`
  - `post_cancel_tasks_{order_id}`
  - `admin_cancel_tasks_{order_id}`
  - `status_update_tasks_{order_id}`

## Monitoring

To track background task failures, monitor logs for:
```
Background task '...' failed with exception
```

Set up alerts if you see spikes in these messages.

## FAQ

**Q: Will this slow down my API responses?**  
A: No! Background tasks still run asynchronously. The only overhead is wrapping them in a try-except block.

**Q: Can I still use `asyncio.create_task()` directly?**  
A: You can, but it's not recommended. Use `create_safe_task()` for production code.

**Q: What if I need the task result?**  
A: If you need the result, don't use background tasks - just `await` the coroutine directly.

**Q: How many background tasks can I create?**  
A: No hard limit, but keep it reasonable. If you're creating thousands, consider a proper job queue (Celery, RQ, etc.).

**Q: Will tasks be retried on failure?**  
A: No, this utility only logs failures. Add retry logic inside your task if needed:
```python
async def task_with_retry():
    for attempt in range(3):
        try:
            await risky_operation()
            return
        except Exception as e:
            if attempt == 2:
                raise
            await asyncio.sleep(2 ** attempt)

create_safe_task(task_with_retry(), task_name="retry_task")
```

## Related

- See `DEPLOYMENT_FIXES.md` for full deployment guide
- See `app/core/middleware.py` for exception handling middleware
- See `app/main.py` for application lifecycle management
