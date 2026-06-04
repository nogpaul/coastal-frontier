"""Configuration loading and validation for the Coastal Frontier project.

Single source of truth for project-wide configuration. All other modules
import settings from here, never from os.environ directly — keeps validation,
logging, and alternate sources (e.g., secret managers) in one auditable place.
"""
from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv

# Project layout — derived from this file's location, not hardcoded.
# This file: src/coastal_frontier/config.py
# Project root: ../../../ from this file.
PROJECT_ROOT: Path = Path(__file__).resolve().parents[2]
DATA_RAW: Path = PROJECT_ROOT / "data" / "raw"
DATA_INTERIM: Path = PROJECT_ROOT / "data" / "interim"
DATA_PROCESSED: Path = PROJECT_ROOT / "data" / "processed"
REPORTS_DIR: Path = PROJECT_ROOT / "reports"
SQL_DIR: Path = PROJECT_ROOT / "sql"

# Load .env into os.environ. Idempotent — safe to call from multiple modules.
load_dotenv(PROJECT_ROOT / ".env")


def _require_env(name: str) -> str:
    """Read an environment variable or raise a clear, actionable error."""
    value = os.environ.get(name)
    placeholders = ("your_registered_email_here", "your_account_password_here")
    if not value or value in placeholders:
        raise RuntimeError(
            f"Required environment variable {name!r} is not set or still "
            f"holds a placeholder. Edit {PROJECT_ROOT / '.env'} and provide a "
            f"real value. See .env.example for the expected format."
        )
    return value


# ACLED OAuth credentials. Validated at import — if anything is missing,
# the project refuses to start. The password lives only in memory and .env;
# never log it, never print it, never commit it.
ACLED_USERNAME: str = _require_env("ACLED_USERNAME")
ACLED_PASSWORD: str = _require_env("ACLED_PASSWORD")

# ACLED API endpoints — hardcoded because they're public contract, not config.
ACLED_TOKEN_URL: str = "https://acleddata.com/oauth/token"
ACLED_API_BASE: str = "https://acleddata.com/api"

# Default database location — can be overridden via env var.
DB_PATH: Path = Path(os.environ.get("DB_PATH", str(DATA_PROCESSED / "coastal_frontier.db")))
