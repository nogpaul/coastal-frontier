"""ACLED API client.

Handles OAuth authentication and (eventually) event ingestion. The OAuth
password-grant flow exchanges username and password for short-lived access
tokens; tokens are then used in the Authorization header of API requests.

This module is intentionally a thin wrapper around the requests library —
no clever abstractions, just clear functions with proper error handling.
"""
from __future__ import annotations

import logging
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone

import requests

from .config import (
    ACLED_API_BASE,
    ACLED_PASSWORD,
    ACLED_TOKEN_URL,
    ACLED_USERNAME,
)

logger = logging.getLogger(__name__)

# Default timeout for any single HTTP call to ACLED, in seconds.
# Generous enough for slow networks, low enough that hangs are noticed.
HTTP_TIMEOUT: int = 30


class AcledError(Exception):
    """Base exception for all ACLED API errors."""


class AcledAuthError(AcledError):
    """Raised when OAuth authentication fails."""


class AcledRateLimitError(AcledError):
    """Raised when ACLED returns 429 Too Many Requests."""


@dataclass(frozen=True)
class AcledToken:
    """An OAuth access token with expiry tracking.

    Frozen because tokens are immutable: once issued, they don't change.
    If we need a new token we create a new instance.
    """

    access_token: str
    expires_at: datetime  # UTC
    refresh_token: str

    @property
    def is_expired(self) -> bool:
        """True if the token has expired (with a 60s safety margin)."""
        return datetime.now(timezone.utc) >= self.expires_at - timedelta(seconds=60)


def get_access_token(
    username: str = ACLED_USERNAME,
    password: str = ACLED_PASSWORD,
    token_url: str = ACLED_TOKEN_URL,
) -> AcledToken:
    """Authenticate with ACLED and return a fresh access token.

    Uses OAuth password-grant flow. The returned token is valid for ~24 hours;
    a refresh token is included for getting new access tokens without
    re-sending the password.

    Raises:
        AcledAuthError: if credentials are rejected or the response is malformed.
    """
    logger.info("Requesting OAuth token from ACLED")

    try:
        response = requests.post(
            token_url,
            headers={"Content-Type": "application/x-www-form-urlencoded"},
            data={
                "username": username,
                "password": password,
                "grant_type": "password",
                "client_id": "acled",
                "scope": "authenticated",
            },
            timeout=HTTP_TIMEOUT,
        )
    except requests.RequestException as exc:
        raise AcledAuthError(f"Network error contacting ACLED: {exc}") from exc

    if response.status_code != 200:
        # Don't include the response body verbatim — ACLED can echo credentials
        # back in error messages. Log status and reason only.
        raise AcledAuthError(
            f"Token request rejected: HTTP {response.status_code} {response.reason}"
        )

    try:
        payload = response.json()
        access_token = payload["access_token"]
        refresh_token = payload["refresh_token"]
        expires_in = int(payload.get("expires_in", 86400))
    except (ValueError, KeyError) as exc:
        raise AcledAuthError(f"Malformed token response: missing {exc}") from exc

    expires_at = datetime.now(timezone.utc) + timedelta(seconds=expires_in)
    logger.info("Token acquired; expires in %ds (%s)", expires_in, expires_at.isoformat())

    return AcledToken(
        access_token=access_token,
        expires_at=expires_at,
        refresh_token=refresh_token,
    )


def smoke_test(token: AcledToken) -> int:
    """Make a minimal API call to verify the token works end-to-end.

    Requests one event from anywhere — the smallest possible query — and
    returns the number of rows received. If this works, the auth pipeline
    is sound and we can proceed to real ingestion.

    Raises:
        AcledError: if the API call fails for any reason.
    """
    logger.info("Running smoke test against ACLED API")

    try:
        response = requests.get(
            f"{ACLED_API_BASE}/acled/read",
            headers={"Authorization": f"Bearer {token.access_token}"},
            params={"limit": 1, "_format": "json"},
            timeout=HTTP_TIMEOUT,
        )
    except requests.RequestException as exc:
        raise AcledError(f"Network error during smoke test: {exc}") from exc

    if response.status_code == 429:
        raise AcledRateLimitError("ACLED returned 429 Too Many Requests")
    if response.status_code != 200:
        raise AcledError(
            f"Smoke test request failed: HTTP {response.status_code} {response.reason}"
        )

    payload = response.json()
    row_count = len(payload.get("data", []))
    logger.info("Smoke test successful; received %d event(s)", row_count)
    return row_count
