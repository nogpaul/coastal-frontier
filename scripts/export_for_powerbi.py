"""Export Coastal Frontier data tables for Power BI dashboard consumption.

Produces a set of CSV files in reports/data_for_powerbi/ that Power BI Desktop
can ingest via Get Data -> Text/CSV. CSV is preferred over SQLite for Power BI
on Windows because it avoids the ODBC-driver requirement.

Run order: notebooks 01-03, then scripts/prepare_changepoint_input.py,
then this script.

Usage:
    python scripts/export_for_powerbi.py
"""

from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from src.coastal_frontier.config import DATA_INTERIM  # noqa: E402

OUT_DIR = PROJECT_ROOT / "reports" / "data_for_powerbi"
OUT_DIR.mkdir(parents=True, exist_ok=True)

SAHEL_CORE = {"Mali", "Burkina Faso", "Niger"}
LITTORAL = {"Togo", "Benin", "Ivory Coast", "Ghana"}

# --- Load the filtered events ---
df = pd.read_parquet(DATA_INTERIM / "ucdp_events_filtered.parquet")
df["date_start"] = pd.to_datetime(df["date_start"])
df["year"] = df["date_start"].dt.year
df["quarter"] = df["date_start"].dt.to_period("Q").astype(str)
df["month"] = df["date_start"].dt.to_period("M").astype(str)
df["region"] = df["country"].apply(
    lambda c: "Sahel Core" if c in SAHEL_CORE else ("Littoral" if c in LITTORAL else "Other")
)

print(f"Loaded {len(df):,} filtered events")

# --- 1. events.csv: event-level table for map visual and detail drill-downs ---
event_cols = [
    "date_start", "year", "quarter", "month",
    "country", "region",
    "latitude", "longitude",
    "best", "high", "low",
    "type_of_violence",
]
events_export = df[[c for c in event_cols if c in df.columns]].copy()
events_export.to_csv(OUT_DIR / "events.csv", index=False)
print(f"  events.csv: {len(events_export):,} rows")

# --- 2. quarterly_counts.csv: per-country per-quarter aggregates ---
quarterly = (
    df.groupby(["country", "region", "quarter"], as_index=False)
    .agg(n_events=("country", "count"), fatalities=("best", "sum"))
    .sort_values(["country", "quarter"])
)
quarterly.to_csv(OUT_DIR / "quarterly_counts.csv", index=False)
print(f"  quarterly_counts.csv: {len(quarterly):,} rows")

# --- 3. regional_summary.csv: MOE values over time ---
def quarter_moes(group: pd.DataFrame) -> pd.Series:
    """Compute the three MOEs for a single quarter."""
    return pd.Series({
        "n_events": len(group),
        "fatalities": group["best"].sum(),
        "moe1_frontier_lat_p05": group["latitude"].quantile(0.05),
        "moe2_littoral_share_pct": (group["region"] == "Littoral").mean() * 100,
        "moe3_center_lat_mean": group["latitude"].mean(),
    })

regional = (
    df.groupby("quarter", group_keys=False)
    .apply(quarter_moes)
    .reset_index()
    .sort_values("quarter")
)
regional.to_csv(OUT_DIR / "regional_summary.csv", index=False)
print(f"  regional_summary.csv: {len(regional):,} rows")

# --- 4. country_summary.csv: per-country lifetime stats ---
country_summary = (
    df.groupby(["country", "region"], as_index=False)
    .agg(
        n_events=("country", "count"),
        fatalities=("best", "sum"),
        first_event=("date_start", "min"),
        last_event=("date_start", "max"),
    )
    .sort_values("n_events", ascending=False)
)
country_summary.to_csv(OUT_DIR / "country_summary.csv", index=False)
print(f"  country_summary.csv: {len(country_summary):,} rows")

# --- 5. change_points.csv: results from R analysis, for annotated visuals ---
change_points = pd.DataFrame([
    {"series": "Regional",  "country": "(all)",        "break_quarter": "2021Q4", "before_mean": 100.1, "after_mean": 148.0},
    {"series": "Regional",  "country": "(all)",        "break_quarter": "2022Q4", "before_mean": 148.0, "after_mean": 220.2},
    {"series": "Regional",  "country": "(all)",        "break_quarter": "2024Q2", "before_mean": 220.2, "after_mean": 127.3},
    {"series": "Country",   "country": "Burkina Faso", "break_quarter": "2022Q4", "before_mean": 40.9,  "after_mean": 124.0},
    {"series": "Country",   "country": "Burkina Faso", "break_quarter": "2023Q4", "before_mean": 124.0, "after_mean": 55.8},
    {"series": "Country",   "country": "Mali",         "break_quarter": "2021Q4", "before_mean": 47.1,  "after_mean": 80.3},
    {"series": "Country",   "country": "Mali",         "break_quarter": "2024Q2", "before_mean": 80.3,  "after_mean": 68.3},
    {"series": "Country",   "country": "Niger",        "break_quarter": "2023Q2", "before_mean": 13.6,  "after_mean": 23.5},
    {"series": "Country",   "country": "Niger",        "break_quarter": "2024Q2", "before_mean": 23.5,  "after_mean": 14.7},
    {"series": "Country",   "country": "Benin",        "break_quarter": "2022Q4", "before_mean": 2.2,   "after_mean": 4.5},
    {"series": "Country",   "country": "Benin",        "break_quarter": "2023Q4", "before_mean": 4.5,   "after_mean": 6.8},
    {"series": "Country",   "country": "Togo",         "break_quarter": "2022Q4", "before_mean": 2.3,   "after_mean": 13.0},
    {"series": "Country",   "country": "Togo",         "break_quarter": "2023Q1", "before_mean": 13.0,  "after_mean": 2.9},
])
change_points["magnitude_pct"] = (
    (change_points["after_mean"] / change_points["before_mean"]) - 1
) * 100
change_points.to_csv(OUT_DIR / "change_points.csv", index=False)
print(f"  change_points.csv: {len(change_points):,} rows")

print(f"\nAll exports written to {OUT_DIR}")
print("\nNext: open Power BI Desktop -> Get Data -> Text/CSV -> select these files.")
