# Coastal Frontier

**Measuring the southward spread of Sahel violence into littoral West Africa, 2020–2026.**

---

## Why this exists

After the wave of Sahel coups between 2020 and 2023 — Mali twice, Burkina Faso twice, Niger once — and the withdrawal of French (Barkhane, Sabre) and EU missions that followed, I kept reading headlines about "spillover" into coastal West Africa. But nobody seemed to be showing me at what *speed*, in what *direction*, or with what *warning signs*. The Sahel-to-coast frontier became the question I couldn't put down.

This repo is my attempt to answer that question from open data — honestly, including when the data refuses to tell the story I expected.

## The hypothesis

> **H1:** Since 2020, jihadist violence has spread southward from the Sahel core (Mali / Burkina Faso / Niger) into the northern littoral states (Togo, Benin, Côte d'Ivoire, Ghana) at an accelerating rate.

H1 is rejected if any of the following hold:
- Southernmost-event latitude per quarter is flat or trending north
- The share of West Africa events occurring in littoral countries has not risen since 2020
- The 2024–2026 sub-window shows plateau or reversal versus 2020–2023

These conditions were declared *before* running the numbers. If the data rejects the hypothesis, that finding stands.

## Methodology in 30 seconds

1. Ingest ACLED event data for seven countries (Mali, Burkina Faso, Niger, Togo, Benin, Côte d'Ivoire, Ghana), 2020–2026.
2. Aggregate to admin-2 (province / cercle / department) level.
3. Compute three independent measures of "southward spread": southernmost latitude per country-quarter, littoral share of regional events, distance from Sahel-core event centroid.
4. Apply change-point detection to identify when each country's trajectory shifted.
5. Overlay an external context timeline (coups, withdrawals, Wagner / Africa Corps moves) against detected inflection points.
6. Define three measures of effectiveness (MOEs) and a forward-looking watchlist of admin-2 districts.
7. Publish brief in PMESII-PT framework structure.

## Repository layout

```
coastal-frontier/
├── data/
│   ├── raw/         untouched ACLED dumps, GADM boundary files
│   ├── interim/     cleaned per-source (Parquet)
│   └── processed/   analysis-ready SQLite database
├── notebooks/       exploratory Jupyter analysis
├── src/
│   └── coastal_frontier/   reusable Python package
├── sql/             versioned SQL queries (the analytical engine)
├── reports/
│   ├── figures/     charts
│   └── maps/        GIS exports
├── .env.example     template for required credentials
└── requirements.txt exact Python dependencies
```

## Reproducing this on your machine

```bash
git clone git@github.com:nogpaul/coastal-frontier.git
cd coastal-frontier

python -m venv .venv
.\.venv\Scripts\Activate.ps1     # Windows PowerShell
# source .venv/bin/activate      # macOS / Linux

pip install -r requirements.txt

cp .env.example .env
# edit .env and fill in your ACLED API credentials
# register at https://acleddata.com/register if you don't have them
```

Then open `notebooks/01_explore.ipynb` to walk through the analysis, or run the pipeline end-to-end with `python -m coastal_frontier.run`.

## Tools

Python, SQL (SQLite), R (for change-point detection), QGIS, Power BI Desktop.

## Known limitations

These shape every interpretation in the brief and live here so they're never out of sight:

- **Reporting density bias.** ACLED events in regions with dense journalism are over-represented. Northern Côte d'Ivoire and northern Ghana have thicker French and English media coverage than rural northern Benin. Apparent rises there may partially reflect press attention.
- **Source-language bias.** Bambara, Hausa, and Fulfulde radio reporting is under-captured. The Sahel-coast borderlands operate in exactly these languages.
- **State suppression.** Post-coup Burkina Faso and Niger have restricted reporting. Recent event counts in these countries are likely *under*-stated, which could create an artificial "Sahel cooling / coast heating" signal.
- **Methodology drift.** ACLED's coding rules have been updated multiple times in the window studied. Long time-series comparisons are not strictly apples-to-apples.

## Status

Active. Ingested through Q2 2026.

## Questions I'm still chewing on

- How much of the apparent southward trend is the data catching up to reality already underway? Can I quantify reporting lag?
- The AES alliance formed in September 2023. Is there a measurable change in event characteristics in member states after that date that isn't just the post-coup baseline?
- Could a same-methodology analysis on the Lake Chad Basin (Nigeria, Cameroon, Niger, Chad) act as a control region — same data source, different conflict ecosystem?
- What would a CAMEO-coded GDELT layer add that ACLED's manual coding misses?

## License

MIT — do what you want, attribution appreciated.
