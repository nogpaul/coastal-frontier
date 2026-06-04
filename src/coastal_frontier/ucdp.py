"""UCDP GED ingestion.

Loads UCDP Georeferenced Event Dataset CSV files from data/raw/, applies the
project's declared inclusion rules, validates the result, and persists a clean
Parquet file to data/interim/.

UCDP ships two relevant files:
  - GEDEvent_v25_1.csv  (stable annual release, 1989-2024)
  - GEDEvent_v26_0_4.csv (Candidate Events Dataset, 2025+, updated regularly)

Both have identical schemas; we load all GEDEvent_v*.csv files and dedupe by
event id. This insulates the loader from UCDP's filename versioning choices.

Reference: UCDP GED Codebook v25.1 (https://ucdp.uu.se/downloads/ged/ged251.pdf)
"""
from __future__ import annotations

import logging
from pathlib import Path

import pandas as pd

from .config import DATA_INTERIM, DATA_RAW

logger = logging.getLogger(__name__)


# --- Declared inclusion rules (the methodology contract) ---

COUNTRIES: tuple[str, ...] = (
    "Mali",
    "Burkina Faso",
    "Niger",
    "Togo",
    "Benin",
    "Ivory Coast",   # UCDP uses "Ivory Coast", not "Cote d'Ivoire"
    "Ghana",
)

YEAR_FROM: int = 2020

MAX_WHERE_PREC: int = 4   # 1=village, 4=multi-adm-1 — keep <=4
MAX_DATE_PREC: int = 3    # 1=exact day, 3=week — keep <=3


# --- Columns we care about (kept) — everything else dropped ---

KEEP_COLUMNS: tuple[str, ...] = (
    # Identifiers
    "id", "relid", "year",
    # WHEN
    "date_start", "date_end", "date_prec",
    # WHERE
    "country", "adm_1", "adm_2",
    "latitude", "longitude", "where_prec", "priogrid_gid",
    # WHO
    "side_a", "side_b", "dyad_name", "conflict_name", "type_of_violence",
    # WHAT
    "best", "high", "low",
    "deaths_a", "deaths_b", "deaths_civilians",
    # HOW SURE
    "code_status", "event_clarity", "number_of_sources",
)


def _find_input_files() -> list[Path]:
    """Locate all UCDP GED event CSVs in data/raw/.

    Returns the sorted list of matches. Both stable GED and Candidate
    versions share the GEDEvent_v*.csv naming pattern.
    """
    files = sorted(DATA_RAW.glob("GEDEvent_v*.csv"))
    if not files:
        raise FileNotFoundError(
            f"No UCDP GED CSVs found in {DATA_RAW}. Expected files matching "
            f"'GEDEvent_v*.csv' — download from https://ucdp.uu.se/downloads/"
        )
    logger.info("Found %d UCDP CSV file(s): %s", len(files), [f.name for f in files])
    return files


def _filter_to_scope(df: pd.DataFrame, source_name: str) -> pd.DataFrame:
    """Apply the declared inclusion rules. Logs row counts at each step."""
    initial = len(df)
    logger.info("%s: %d rows loaded", source_name, initial)

    df = df[df["country"].isin(COUNTRIES)].copy()
    logger.info("%s: %d rows after country filter", source_name, len(df))

    df = df[df["year"] >= YEAR_FROM]
    logger.info("%s: %d rows after year >= %d", source_name, len(df), YEAR_FROM)

    df = df[df["where_prec"] <= MAX_WHERE_PREC]
    logger.info("%s: %d rows after where_prec <= %d", source_name, len(df), MAX_WHERE_PREC)

    df = df[df["date_prec"] <= MAX_DATE_PREC]
    logger.info("%s: %d rows after date_prec <= %d", source_name, len(df), MAX_DATE_PREC)

    df = df[df["code_status"] == "Clear"]
    logger.info("%s: %d rows after code_status == 'Clear'", source_name, len(df))

    return df


def load_and_filter() -> pd.DataFrame:
    """Load all UCDP event CSVs, filter, concat, dedupe by id."""
    files = _find_input_files()
    frames: list[pd.DataFrame] = []

    for f in files:
        raw = pd.read_csv(f, low_memory=False)
        filtered = _filter_to_scope(raw, f.name)
        frames.append(filtered)

    combined = pd.concat(frames, ignore_index=True)
    before_dedup = len(combined)
    combined = combined.drop_duplicates(subset="id", keep="first")
    logger.info(
        "Combined: %d rows after concat, %d after dedup on id (%d duplicates removed)",
        before_dedup, len(combined), before_dedup - len(combined),
    )

    # Subset to declared columns, preserving order
    missing = set(KEEP_COLUMNS) - set(combined.columns)
    if missing:
        raise ValueError(
            f"Expected columns missing from UCDP data: {missing}. "
            f"Codebook may have changed; reconcile against latest version."
        )
    combined = combined[list(KEEP_COLUMNS)].copy()

    # Parse dates properly — UCDP ships them as strings
    combined["date_start"] = pd.to_datetime(combined["date_start"], errors="coerce")
    combined["date_end"] = pd.to_datetime(combined["date_end"], errors="coerce")

    logger.info(
        "Final dataset: %d events across %d countries, %d to %d",
        len(combined),
        combined["country"].nunique(),
        int(combined["year"].min()),
        int(combined["year"].max()),
    )
    return combined


def persist_interim(df: pd.DataFrame) -> Path:
    """Write filtered events to data/interim/ as Parquet."""
    DATA_INTERIM.mkdir(parents=True, exist_ok=True)
    out_path = DATA_INTERIM / "ucdp_events_filtered.parquet"
    df.to_parquet(out_path, index=False)
    logger.info("Persisted %d events to %s", len(df), out_path)
    return out_path


def run() -> Path:
    """Entry point: load, filter, persist."""
    df = load_and_filter()
    return persist_interim(df)
