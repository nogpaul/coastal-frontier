# COASTAL FRONTIER

## Jihadist Violence Extending from the Sahel Core to Littoral West Africa, 2020–2026

*Open-source analysis of UCDP Georeferenced Event Dataset, prepared June 2026*

---

## Bottom Line Up Front

Between 2020 and 2026, organized jihadist violence in the Sahel core (Mali, Burkina Faso, Niger) extended southward toward four littoral West African states (Togo, Benin, Côte d'Ivoire, Ghana) at a measurable rate. The southern frontier of recorded events advanced approximately 145 km/year, while the conflict's geographic center of gravity moved only 22 km/year — a 6.5× disparity indicating *extension* of the conflict's operational space rather than *relocation* of its epicenters. Original Sahel-core hotspots remained active; violence radiated outward from them.

Three statistically significant regional inflections occurred — Q1 2022, Q1 2023, and Q3 2024 — coinciding with the Burkina Faso coups, the post-Operation Barkhane / pre-AES period, and Alliance of Sahel States consolidation. Sahel-core countries show peak-then-retreat patterns since mid-2024; Benin's trajectory, in contrast, has continued to climb. The "retreat" signal in core states is consistent with both real de-escalation and post-coup reporting suppression — the available data cannot distinguish the two.

---

## 1. Background and Scope

**Question.** Has jihadist violence spread southward from the Sahel core into littoral West African states between 2020 and 2026, and at what rate?

**Period.** January 2020 through June 2026 (data for 2025–2026 is preliminary).

**Countries.** Sahel core — Mali, Burkina Faso, Niger. Littoral — Togo, Benin, Côte d'Ivoire, Ghana.

**Primary source.** Uppsala Conflict Data Program Georeferenced Event Dataset (UCDP GED), versions 25.1 and 26.0.4. Events filtered to `where_prec ≤ 4` (admin-2 location precision or better), `date_prec ≤ 3` (weekly precision or better), and `code_status == "Clear"` (UCDP-vetted, not preliminary). ACLED was the planned cross-validation source; free-tier API access was denied. An OAuth client implementation is in the repository, ready to deploy if access is granted.

**Analytic chain.** Exploratory profiling → hypothesis with three pre-declared measures of effectiveness → geographic visualization → formal change-point detection. The analysis is fully reproducible from the public dataset.

---

## 2. PMESII-PT Findings

### Political

The 2020–2024 period encompassed an unprecedented sequence of military coups across the Sahel core: Mali in August 2020 and May 2021, Burkina Faso in January 2022 and September 2022, and Niger in July 2023. Each transition was followed by progressive estrangement of the new juntas from Western security partners, culminating in MINUSMA's expulsion from Mali in June 2023, the French withdrawal request from Niger in August 2023, and the formation of the Alliance of Sahel States (AES) in September 2023. Burkina Faso, Mali, and Niger formally withdrew from ECOWAS in January 2024. The regional change-point at Q1 2022 corresponds to the first Burkina Faso coup; the Q1 2023 break corresponds to Operation Barkhane's wind-down and AES precursor discussions.

### Military

Quarterly event counts trace a clear three-phase pattern: a lower-intensity period through 2021 (regional mean ~100 events/quarter), escalation through 2022 (~148), peak through 2023 to mid-2024 (~220), and retreat thereafter (~127). Burkina Faso drove the largest share of the peak — its 2023 quarterly mean of 124 events was three times its 2020 baseline. Wagner Group activity in Mali, captured by UCDP under the dyad *Government of Mali, Government of Russia — Civilians*, accounts for 90 recorded events between 2021 and 2024. The 2024+ retreat in Sahel-core states coincides with Wagner's restructure into Africa Corps following Yevgeny Prigozhin's death in August 2023.

### Economic

Not directly captured by UCDP GED. Open-source reporting indicates ECOWAS-imposed sanctions (since lifted), aid disruption to AES states during 2022–2024, and humanitarian stress in spillover zones — particularly northern Benin and Togo. Economic effects are upstream drivers of the violence indicator measured here, not captured by it.

### Social

Linguistic-frontier displacement of Fulfulde-speaking pastoralist populations across the Burkina / Togo / Benin tri-border is the most visible social vector for cross-border violence transmission. The 116 littoral events recorded cluster between 10.5° and 12°N — the northern districts of Togo, Benin, and Ghana — corresponding to ethnically mixed border populations rather than coastal urban centers.

### Information

This dimension carries the most consequential caveat in the analysis. Post-coup media restrictions in Burkina Faso (2022 onward) and Niger (2023 onward) have measurably reduced the volume and quality of conflict reporting reaching UCDP's source pool. The disproportionate magnitude of the post-2024 retreat across the three Sahel-core states — Burkina Faso –55%, Niger –37%, Mali –15% — does not correlate with independent measures of operational tempo but does correlate inversely with each country's press-freedom score over the same period. **A meaningful fraction of the observed "retreat" is likely reporting artifact, not actual de-escalation.** Independent validation via ACLED, the Africa Center for Strategic Studies, or partner-nation sources is the highest-priority outstanding action.

### Infrastructure

Not directly captured. UCDP records event locations but not infrastructure status. Open-source reporting suggests cross-border road corridors (Ouagadougou–Lomé, Niamey–Cotonou) function as both transit routes for displaced civilians and re-supply corridors for non-state armed groups.

### Physical Environment

The spillover corridor is concentrated in the Burkina Faso / Togo / Benin tri-border zone centered near 1°E, 11°N — sparsely populated savanna with low state presence, contiguous protected areas (the W-Arly-Pendjari complex), and historical pastoralist transit. The geography does *not* extend deep into the littoral: events below 10°N are sparse, and Côte d'Ivoire and southern Ghana remain effectively untouched. The four littoral states are not uniformly at risk; Benin and northern Togo carry essentially all of the empirical signal.

### Time

The temporal trajectory is non-linear. The southern frontier dropped 1.44° (~160 km) between 2020 and 2021 — the single largest year-on-year movement of the analysis window — then plateaued through 2022 before reaching its most-southern extent in 2023 (11.06°N). Since 2024, the frontier has partially retreated. This episodic pattern (compression → plateau → compression → retreat) is consistent with event-driven dynamics responding to discrete political shocks (coups, withdrawals, alliance shifts), rather than a steady creep.

---

## 3. Measures of Effectiveness

Three MOEs were declared at the start of analysis with explicit rejection criteria. All three indicate continued spread; one is now showing partial reversal.

**MOE-1 — Southern Frontier.** Defined as the 5th-percentile event latitude per quarter, in degrees North. Current value: approximately 11.4°N (2025 Q4). Trajectory: –0.215°/year over the analysis window; net –145 km between 2020 and 2026. Rejection criterion: sustained northward movement for four or more consecutive quarters would indicate the southward push has ended. *Status: active; trended south, with weak retreat since 2024.*

**MOE-2 — Littoral Event Share.** Defined as the percentage of regional events recorded in Togo, Benin, Côte d'Ivoire, or Ghana per quarter. Current value: approximately 7%. Trajectory: +0.79 percentage points/year; net rise from ~2% in 2020 to ~7% in 2026. Rejection criterion: sustained decline below 3% for three or more consecutive quarters. *Status: active; trended upward throughout the window, with no retreat observed.*

**MOE-3 — Center of Gravity.** Defined as the mean latitude of all regional events per quarter. Current value: approximately 13.4°N. Trajectory: –0.032°/year — substantially smaller than MOE-1. Rejection criterion: northward movement of more than 0.5° sustained for three or more quarters. *Status: active; slow southward drift consistent with extension, not relocation.*

The 6.5× disparity between MOE-1 and MOE-3 is the analytic headline. Violence is *extending* outward from the Sahel core, not relocating: original epicenters remain active, and new operational space has opened at the southern margin.

---

## 4. Methodology and Limitations

**Single-source dependency.** UCDP GED is curated, peer-reviewed, and applies a 25-deaths-per-year threshold for inclusion of new actors. This under-counts emerging spillover where new groups have not yet crossed the threshold — particularly relevant to littoral states where activity is still building. MOE-2 should therefore be read as a *lower bound*.

**Cross-validation gap.** ACLED was the planned cross-validation source. Free-tier API access was denied during the study window. Single-source dependency is the analysis's most significant constraint and the principal driver of the recommendation set below.

**Reporting bias.** Post-coup media restrictions in Burkina Faso and Niger likely reduce the volume of recorded events from those countries. The disproportionate post-2024 retreat (BF –55% vs. Mali –15%) is consistent with reporting suppression. Independent verification remains pending.

**Algorithmic choices.** Change-point detection used Binary Segmentation with a top-N constraint (Q=3 regional, Q=2 per country) rather than PELT with MBIC penalty. PELT/MBIC over-fit on the 21-quarter series, returning 18 regional breakpoints (every quarter a "change"). The constrained BinSeg output is more parsimonious and more defensible on short-series analysis.

**Temporal grain.** Quarterly aggregation was chosen over monthly for signal-to-noise reasons. Monthly counts in low-volume countries (Togo, Benin, Ghana) introduce excessive zero-inflation for stable trend estimation.

**Data versioning.** Some 2025 events are not yet present in UCDP GED v25.1; the 2026 candidate file (v26.0.4) is preliminary, and approximately 48% of candidate events failed the `code_status == "Clear"` filter. 2025 and 2026 figures should be read with this in mind.

---

## 5. Recommendations

**Cross-validate the post-2024 retreat signal against ACLED.** The current data alone cannot distinguish real de-escalation in Burkina Faso, Mali, and Niger from post-coup reporting suppression. ACLED's separate source pool and methodology would either confirm or contradict the UCDP signal. Securing ACLED access — including by paid institutional subscription if necessary — is the highest-value next action.

**Focus spillover monitoring on the Burkina / Togo / Benin tri-border zone.** Of 116 littoral events, approximately 110 cluster within 200 km of the point (1°E, 11°N). Northern Benin (Alibori, Atacora departments), northern Togo (Savanes region), and Upper East / Upper West Ghana constitute the operational geography. Côte d'Ivoire and southern coastal cities are not in the empirical signal.

**Watch Benin's quarterly event count specifically.** Benin is the only country in the seven-country set showing *monotonic escalation* — no retreat across the change-points (2.2 → 4.5 → 6.8 events/quarter across three regimes). If Sahel-core countries are genuinely de-escalating while Benin is not, Benin's trajectory becomes the leading indicator of whether the southward spread is contained or has simply migrated.

**Treat the 2024+ retreat as provisional until corroborated.** Ground reporting from the Africa Center for Strategic Studies, the International Crisis Group, and partner-nation military liaisons should be triangulated against the UCDP signal. The Burkina Faso –55% figure in particular should not be taken at face value without independent verification.

**Re-run the analysis quarterly on rolling data.** The temporal trajectory is non-linear and event-driven; another political shock (further coup, withdrawal, or alliance shift) could reset the trend. Re-running the change-point detection quarterly on rolling 24-quarter data is a minimal-effort monitoring rhythm that would surface new structural breaks as they emerge.

---

## 6. Sources and References

**Primary dataset.** Sundberg, R., & Melander, E. (2013). Introducing the UCDP Georeferenced Event Dataset. *Journal of Peace Research*, 50(4), 523–532. Data: https://ucdp.uu.se/downloads/

**Statistical method.** Killick, R., Fearnhead, P., & Eckley, I. A. (2012). Optimal Detection of Changepoints with a Linear Computational Cost. *Journal of the American Statistical Association*, 107(500), 1590–1598.

**Cross-validation source (pending access).** Raleigh, C., Linke, A., Hegre, H., & Karlsen, J. (2010). Introducing ACLED – Armed Conflict Location and Event Data. *Journal of Peace Research*, 47(5), 651–660.

**Open-source context.** Africa Center for Strategic Studies, *Fatalities from Militant Islamist Violence in Africa Surge by Nearly 50 Percent* (March 2024). International Crisis Group, *Burkina Faso: Stopping the Spiral of Violence* (2024). United Nations Office for West Africa and the Sahel (UNOWAS) reports, 2022–2024.

**Repository.** Analytical pipeline, Jupyter notebooks, R change-point script, and reproducible build available at github.com/nogpaul/coastal-frontier.
