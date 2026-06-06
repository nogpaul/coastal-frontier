# Coastal Frontier

**Measuring the southward spread of Sahel violence into littoral West Africa, 2020–2026.**

> **Headline finding:** Across three independent measures, jihadist violence has spread southward from the Sahel core into the littoral states — but the pattern is **extension, not shift**. The Sahel core has not relocated; it has radiated outward while remaining active in its original epicenters. The southern frontier advanced ~145 km over the analysis window; the littoral share of regional events roughly tripled; the center of gravity barely moved. The 6.5× disparity between frontier-speed and bulk-speed is the operational finding.

---

## Why this exists

After the wave of Sahel coups between 2020 and 2023 — Mali twice, Burkina Faso twice, Niger once — and the withdrawal of French (Barkhane, Sabre) and EU missions that followed, I kept reading headlines about "spillover" into coastal West Africa. But nobody seemed to be showing me at what *speed*, in what *direction*, or with what *warning signs*. The Sahel-to-coast frontier became the question I couldn't put down.

This repo is my attempt to answer that question from open data — honestly, including where the data refuses to tell the story I expected.

## The hypothesis and the result

**H1:** Since 2020, jihadist violence has spread southward from the Sahel core (Mali / Burkina Faso / Niger) into the northern littoral states (Togo, Benin, Côte d'Ivoire, Ghana) at an accelerating rate.

H1 was tested against three *pre-declared* measures with rejection criteria stated **before** the data was loaded:

| Measure | Definition | Result | Verdict |
|---|---|---|---|
| **M1 — Southern frontier** | 5th-percentile latitude of events per quarter | -0.215°/yr (~145 km south) | ✓ supports H1 |
| **M2 — Littoral share** | Share of events in Togo / Benin / Côte d'Ivoire / Ghana per quarter | +0.79 pp/yr (~2% → ~7%) | ✓ supports H1 |
| **M3 — Center of gravity** | Mean latitude of events per quarter | -0.032°/yr (~22 km south) | ✓ supports H1 (weakly) |

All three measures move in the predicted direction with positive pairwise correlations (M1↔M2 r=0.70, M1↔M3 r=0.49, M2↔M3 r=0.44).

**The disparity is the story.** M1 (frontier) outpaces M3 (bulk) by 6.5×. The frontier raced south while the bulk barely moved. This is the signature of *extension* — operations radiating outward without abandoning the core — not *relocation*. Planners should treat the Sahel-core violence and the new littoral activity as additive phenomena, not substitutive ones.

## Methodology in 30 seconds

1. Ingest UCDP GED + UCDP Candidate event data, 2020–2026, seven countries (Sahel core + littoral neighbors).
2. Apply pre-declared inclusion rules: `where_prec ≤ 4`, `date_prec ≤ 3`, `code_status == "Clear"`. All rules live as module-level constants in `src/coastal_frontier/ucdp.py`.
3. Aggregate to quarterly time series for each of three operationalizations of "southward spread."
4. Z-score, flip signs to a common direction, plot together, compute pairwise correlations.
5. Overlay external context (coups, withdrawals, Wagner / Africa Corps deployment) against detected inflection points.
6. Publish brief in PMESII-PT framework structure with declared MOEs.

Full reasoning lives in `notebooks/02_hypothesis.ipynb`.

## Data sources

**Primary — UCDP Georeferenced Event Dataset.** Versions 25.1 (stable, 1989–2024) + 26.0.4 (Candidate, 2025+). Free, peer-reviewed, downloadable from [ucdp.uu.se/downloads](https://ucdp.uu.se/downloads/). Event-level conflict data with village-level geocoding, day-level dates, full actor and dyad attribution. UCDP's 25-deaths-per-year inclusion threshold acts as a noise filter — only organized armed conflict appears, not protests or street crime.

**Secondary (kept as fallback) — ACLED via OAuth password grant.** The OAuth client at `src/coastal_frontier/acled.py` is fully functional. Access to ACLED's free API tier was denied for this project (`403 Access denied` on `/api/acled/read`), so the project pivoted to UCDP. The ACLED integration code is committed and would activate immediately on approval — `smoke_test()` works end-to-end as written.

## Repository layout

```
coastal-frontier/
├── data/
│   ├── raw/         untouched UCDP CSVs (gitignored, regenerable from source)
│   ├── interim/     filtered Parquet (per the inclusion-rule contract)
│   └── processed/   analysis-ready outputs
├── notebooks/
│   ├── 01_exploration.ipynb   first-pass EDA
│   ├── 02_hypothesis.ipynb    three measures of southward spread
│   └── 03_geography.ipynb     spatial visualization (in progress)
├── src/
│   └── coastal_frontier/
│       ├── config.py    paths + OAuth credentials, fail-fast validation
│       ├── acled.py     ACLED OAuth client (fallback, ready when access granted)
│       └── ucdp.py      UCDP GED loader with declared inclusion rules
├── sql/                 SQL queries (versioned as code)
├── reports/             figures, maps, PDF brief
├── .env.example         template for required credentials
└── requirements.txt     pinned Python dependencies
```

## Reproducing this on your machine

```bash
git clone git@github.com:nogpaul/coastal-frontier.git
cd coastal-frontier

python -m venv .venv
.\.venv\Scripts\Activate.ps1     # Windows PowerShell
# source .venv/bin/activate      # macOS / Linux

pip install -r requirements.txt
```

Download UCDP data and place CSVs into `data/raw/`:

1. Visit [ucdp.uu.se/downloads](https://ucdp.uu.se/downloads/)
2. Download **GED Global version 25.1** as CSV
3. Download **UCDP Candidate Events Dataset** latest version as CSV
4. Move both CSVs into `data/raw/` (filenames will be `GEDEvent_v25_1.csv` and `GEDEvent_v26_0_X.csv`)

Run the ingest:

```bash
python -c "from src.coastal_frontier.ucdp import run; run()"
```

This produces `data/interim/ucdp_events_filtered.parquet`. Then open the notebooks in Jupyter Lab.

The `.env.example` documents optional credentials for the ACLED fallback path. Not required for the UCDP pipeline.

## Tools used

Python (pandas, numpy, matplotlib, seaborn), SQL (via SQLite — coming in next phase), R (change-point detection — coming in next phase), QGIS (geographic analysis — coming in next phase), Power BI Desktop (interactive dashboard — planned).

## Known limitations

These shape every interpretation and live here so they're never out of sight:

- **UCDP inclusion threshold.** UCDP only records events linked to dyads that crossed 25 battle-related deaths in some year. Early-stage spillover into littoral states (small-scale incursions, isolated incidents) is under-captured until the threshold is crossed. **The M2 (littoral share) trend is therefore a lower bound** — the real southward push is likely steeper than +0.79 pp/yr.
- **Post-coup reporting suppression.** Burkina Faso (since 2022) and Niger (since 2023) restricted media operations after their respective coups. Recent Sahel-core event counts are likely *under*-stated, which could artificially inflate the M1 (frontier) signal relative to M3 (bulk). The extension finding is consistent with reporting bias *and* with genuine extension; the two are not separable from this data alone.
- **2026 data is preliminary.** UCDP's Candidate dataset is actively under review; ~48% of 2025+ events failed the `code_status == "Clear"` filter and were excluded. The 2026 sub-window in any chart should be read as a lower bound.
- **2025 coverage gap.** The data jumps from 2024 to 2026 in our filtered view; UCDP's versioning of the Candidate dataset appears to skip 2025 in the v26.0.4 release. To investigate before final brief.
- **ACLED unavailable.** This analysis uses only UCDP. A parallel ACLED analysis would catch lower-threshold events and likely show *stronger* extension signals, particularly in the littoral. The OAuth integration is ready for the day API access is granted.
- **Source-language bias.** UCDP reads many languages but under-captures Bambara, Hausa, and Fulfulde radio reporting — exactly the languages of the Sahel-coast borderlands.

## Status

Active. Hypothesis testing complete (notebooks 01–02). Geographic analysis and change-point detection in progress. Brief drafted on completion.

## Questions I'm still chewing on

- **What explains the 2023 inflection?** Burkina Faso's second coup (Sep 2022), the Niger coup (Jul 2023), the end of Operation Barkhane (Nov 2022) and Sabre (Dec 2023), and Wagner's evolution into Africa Corps all cluster in this window. Which of these explains the spike, and how separable are they?
- **Is the extension pattern symmetric across the frontier?** All four littoral countries should be checked individually — perhaps Togo and Benin show extension while Ghana and Côte d'Ivoire don't, which would reshape recommendations about where to focus security cooperation.
- **Where is 2025 in the data?** UCDP's release cycle appears to skip the year in v26.0.4. Investigation pending.
- **Would ACLED change the verdict?** ACLED's lower inclusion threshold should catch early-stage incidents UCDP misses. The directional finding (extension) should hold; the magnitude on M2 likely grows.
- **Could a same-methodology analysis on the Lake Chad Basin (Nigeria, Cameroon, Niger, Chad) serve as a control region?** Same data source, comparable conflict ecosystem — would tell us whether extension-not-shift is general to Sahel-style insurgencies or specific to the West African case.

## License

MIT — do what you want, attribution appreciated.
