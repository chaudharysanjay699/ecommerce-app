"""Safe background task execution to prevent app crashes."""
from __future__ import annotations

import asyncio
import logging
from typing import Callable, Coroutine, Any

logger = logging.getLogger(__name__)

# Global set to track running background tasks
_background_tasks: set[asyncio.Task] = set()


def create_safe_task(coro: Coroutine[Any, Any, Any], *, task_name: str = "background_task") -> asyncio.Task:
    """
    Create a background task that logs exceptions instead of crashing the app.
    
    Args:
        coro: The coroutine to run
        task_name: A descriptive name for logging purposes
        
    Returns:
        The created asyncio.Task
    """
    
    async def _safe_wrapper():
        try:
            await coro
            logger.info("Background task '%s' completed successfully", task_name)
        except asyncio.CancelledError:
            logger.warning("Background task '%s' was cancelled", task_name)
            raise
        except Exception:
            logger.exception(
                "Background task '%s' failed with exception (app continues running)",
                task_name,
            )
    
    task = asyncio.create_task(_safe_wrapper())
    
    # Keep a reference to prevent garbage collection before completion
    _background_tasks.add(task)
    task.add_done_callback(_background_tasks.discard)
    
    return task


async def wait_for_background_tasks(timeout: float = 30.0) -> None:
    """
    Wait for all background tasks to complete (useful for graceful shutdown).
    
    Args:
        timeout: Maximum time to wait in seconds
    """
    if not _background_tasks:
        return
    
    logger.info("Waiting for %d background tasks to complete...", len(_background_tasks))
    try:
        await asyncio.wait_for(
            asyncio.gather(*_background_tasks, return_exceptions=True),
            timeout=timeout,
        )
        logger.info("All background tasks completed")
    except asyncio.TimeoutError:
        logger.warning("Background tasks did not complete within %s seconds", timeout)
