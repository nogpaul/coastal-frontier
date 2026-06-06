"""Export quarterly per-country counts for the R change-point analysis."""
from pathlib import Path
import sys

import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from src.coastal_frontier.config import DATA_INTERIM

df = pd.read_parquet(DATA_INTERIM / "ucdp_events_filtered.parquet")
df["quarter"] = pd.to_datetime(df["date_start"]).dt.to_period("Q").astype(str)

counts = (
    df.groupby(["country", "quarter"])
    .size()
    .reset_index(name="n")
    .sort_values(["country", "quarter"])
)

out_path = DATA_INTERIM / "quarterly_counts.csv"
counts.to_csv(out_path, index=False)
print(f"Wrote {len(counts):,} rows to {out_path}")
