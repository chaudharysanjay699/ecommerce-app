"""
Firebase Cloud Messaging (FCM) HTTP v1 API sender.

Uses the service account JSON to obtain a short-lived OAuth2 access token,
then POSTs messages to the FCM v1 endpoint via httpx.

Required .env variables:
    FIREBASE_PROJECT_ID=your-project-id
    FIREBASE_SERVICE_ACCOUNT_JSON=/path/to/serviceAccountKey.json

If either variable is empty the helpers log a warning and return silently,
so the rest of the application keeps working during local development.
"""
from __future__ import annotations

import asyncio
import json
import logging
from typing import Sequence

import httpx

from app.core.config import settings

logger = logging.getLogger(__name__)

FCM_ENDPOINT = (
    "https://fcm.googleapis.com/v1/projects/{project_id}/messages:send"
)
_SCOPES = ["https://www.googleapis.com/auth/firebase.messaging"]

# Chunk size: FCM v1 only accepts one message at a time, but we batch DB
# lookups and fire concurrent requests in groups.
_CONCURRENCY = 20


def _is_configured() -> bool:
    return bool(settings.FIREBASE_PROJECT_ID and settings.FIREBASE_SERVICE_ACCOUNT_JSON)


def _get_access_token() -> str:
    """Obtain a short-lived OAuth2 bearer token from the service account.

    This call is synchronous (google-auth library) and must be run in a
    thread-pool executor when called from async code.
    """
    import google.auth.transport.requests
    import google.oauth2.service_account

    sa_path = settings.FIREBASE_SERVICE_ACCOUNT_JSON

    # Support inline JSON string as well as a file path
    if sa_path.strip().startswith("{"):
        info = json.loads(sa_path)
        credentials = google.oauth2.service_account.Credentials.from_service_account_info(
            info, scopes=_SCOPES
        )
    else:
        credentials = google.oauth2.service_account.Credentials.from_service_account_file(
            sa_path, scopes=_SCOPES
        )

    request = google.auth.transport.requests.Request()
    credentials.refresh(request)
    return credentials.token  # type: ignore[return-value]


async def _get_access_token_async() -> str:
    """Async wrapper around the synchronous _get_access_token."""
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, _get_access_token)


async def _send_single(
    client: httpx.AsyncClient,
    token: str,
    title: str,
    body: str,
    access_token: str,
    data: dict | None = None,
) -> None:
    """Send one FCM message to a single device token."""
    payload: dict = {
        "message": {
            "token": token,
            "notification": {"title": title, "body": body},
            "android": {"priority": "high"},
            "apns": {"headers": {"apns-priority": "10"}},
        }
    }
    if data:
        payload["message"]["data"] = {k: str(v) for k, v in data.items()}

    url = FCM_ENDPOINT.format(project_id=settings.FIREBASE_PROJECT_ID)
    try:
        resp = await client.post(
            url,
            json=payload,
            headers={
                "Authorization": f"Bearer {access_token}",
                "Content-Type": "application/json",
            },
            timeout=10.0,
        )
        if resp.status_code not in (200, 201):
            logger.warning(
                "FCM send failed for token …%s: %s %s",
                token[-8:],
                resp.status_code,
                resp.text[:200],
            )
    except Exception:
        logger.exception("FCM request error for token …%s", token[-8:])


async def send_push(
    tokens: Sequence[str],
    title: str,
    body: str,
    data: dict | None = None,
) -> None:
    """Send a push notification to one or more FCM tokens.

    Skips silently if FCM is not configured.
    Fires requests concurrently in batches of _CONCURRENCY.
    """
    if not _is_configured():
        logger.warning("FCM not configured (FIREBASE_PROJECT_ID / FIREBASE_SERVICE_ACCOUNT_JSON missing). Skipping push.")
        return

    if not tokens:
        return

    try:
        access_token = await _get_access_token_async()
    except Exception:
        logger.exception("Failed to obtain FCM access token — skipping push.")
        return

    async with httpx.AsyncClient() as client:
        # Process in chunks to avoid hammering FCM with too many concurrent requests
        token_list = list(tokens)
        for i in range(0, len(token_list), _CONCURRENCY):
            chunk = token_list[i : i + _CONCURRENCY]
            await asyncio.gather(
                *[
                    _send_single(client, t, title, body, access_token, data)
                    for t in chunk
                ]
            )

    logger.info("FCM push sent to %d device(s): %s", len(token_list), title)
