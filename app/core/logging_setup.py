"""Application logging configuration.

Sets up:
  - Console handler  (always active)
  - File handler     (best-effort, skipped if logs/ is not writable)
  - CloudWatch handler (active only when AWS credentials are present in settings)

CloudWatch level: WARNING and above (errors, critical).
Console/file level: INFO and above.

Usage:
    from app.core.logging_setup import configure_logging
    configure_logging()   # call once at startup
"""
from __future__ import annotations

import logging
import sys
from pathlib import Path


def configure_logging() -> None:
    """Configure root logger with console, file, and optional CloudWatch handlers."""
    from app.core.config import settings

    fmt = logging.Formatter(
        "%(asctime)s  %(levelname)-8s  %(name)s  %(message)s",
        datefmt="%Y-%m-%dT%H:%M:%S",
    )

    handlers: list[logging.Handler] = []

    # ── Console ──────────────────────────────────────────────────────────────
    console = logging.StreamHandler(sys.stdout)
    console.setLevel(logging.INFO)
    console.setFormatter(fmt)
    handlers.append(console)

    # ── File (best-effort) ───────────────────────────────────────────────────
    try:
        log_dir = Path("logs")
        log_dir.mkdir(parents=True, exist_ok=True)
        file_handler = logging.FileHandler(log_dir / "app.log", encoding="utf-8")
        file_handler.setLevel(logging.INFO)
        file_handler.setFormatter(fmt)
        handlers.append(file_handler)
    except (PermissionError, OSError) as exc:
        print(f"[logging] Could not create log file: {exc} — using console only.", file=sys.stderr)

    # ── CloudWatch (optional) ────────────────────────────────────────────────
    cw = _build_cloudwatch_handler(settings, fmt)
    if cw:
        handlers.append(cw)
        print("[logging] CloudWatch logging enabled.", file=sys.stderr)
    else:
        print("[logging] CloudWatch disabled (no AWS credentials configured).", file=sys.stderr)

    logging.basicConfig(level=logging.INFO, handlers=handlers, force=True)


def _build_cloudwatch_handler(settings, fmt: logging.Formatter) -> logging.Handler | None:
    """Return a CloudWatchLogHandler if credentials are set, else None."""
    if not (settings.AWS_ACCESS_KEY_ID and settings.AWS_SECRET_ACCESS_KEY):
        return None

    try:
        import boto3
        import watchtower

        client = boto3.client(
            "logs",
            region_name=settings.AWS_REGION,
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
        )

        handler = watchtower.CloudWatchLogHandler(
            boto3_client=client,
            log_group_name=settings.CLOUDWATCH_LOG_GROUP,
            log_stream_name=settings.CLOUDWATCH_LOG_STREAM,
            create_log_group=True,
            send_interval=5,       # flush every 5 seconds
            max_batch_count=100,
        )
        # Only ship WARNING+ to CloudWatch (skip routine INFO noise)
        handler.setLevel(logging.WARNING)
        handler.setFormatter(fmt)
        return handler

    except ImportError:
        print(
            "[logging] boto3/watchtower not installed — CloudWatch disabled. "
            "Run: pip install boto3 watchtower",
            file=sys.stderr,
        )
        return None
    except Exception as exc:
        print(f"[logging] Could not initialise CloudWatch handler: {exc}", file=sys.stderr)
        return None
