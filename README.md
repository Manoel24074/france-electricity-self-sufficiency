# Where France's electricity is made — Streamlit data story

An interactive regional electricity story built from RTE's éCO2mix consolidated
and definitive data. The central question is:

> **How do regional electricity production, demand, and physical exchanges differ
> across France—and how would a simple wind-and-solar uplift change the balance?**

## Audience and story arc

- **Audience:** citizens, students, and regional decision-makers curious about
  energy transition and the electricity system.
- **Hook:** electricity is consumed everywhere, but generation is geographically
  concentrated.
- **Context:** compare reported production and consumption for 12 metropolitan
  regions over time.
- **Key insight:** regional production-to-demand coverage and measured exchanges
  show complementary, but not necessarily directly connected, regional balances.
- **Implication:** regional generation is only part of the picture; transmission,
  storage, flexibility, and demand matter too.
- **Interaction:** change the time window, select a region, inspect technology
  trends, and test a transparent arithmetic scenario.

The charts are intentionally descriptive. The dashboard does not claim that one
region directly supplies another.

## Run locally

Python 3.10 or newer is recommended.

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
streamlit run app.py
```

The packaged daily regional extract is in `data/eco2mix_daily.csv`. The app reads
that file locally, so it does not make API requests each time it loads. Use the
sidebar or the large chapter buttons at the top and bottom of each page to move
through the five-page story. The year range and region focus in the sidebar are
shared across the pages.

## Refresh the dataset

```powershell
python prep.py
```

The preparation script calls the official Open Data Soft API and asks it to
aggregate readings to one row per region and date. It fetches one calendar-year
partition per request, coerces numeric values, rejects duplicate region-days,
and keeps region-days with at least 36 source readings. Year partitions avoid
unstable pagination and are a small extract compared with downloading millions
of half-hourly records.

An optional starting date can be supplied:

```powershell
python prep.py --start-date 2022-01-01
```

## Data source and definitions

- **Dataset:** [RTE — Données éCO2mix régionales consolidées et définitives](https://www.data.gouv.fr/datasets/donnees-eco2mix-regionales-consolidees-et-definitives)
- **API used by `prep.py`:** [Open Data Soft dataset endpoint](https://odre.opendatasoft.com/api/explore/v2.1/catalog/datasets/eco2mix-regional-cons-def/records)
- **License:** Open Data Licence 2.0 (Etalab), as shown on the source dataset.
- The source describes half-hourly realized consumption, production by technology,
  and physical exchanges. It is consolidated/definitive data and is refreshed
  daily. The `nature` column is retained so definitive and consolidated observations
  remain distinguishable when the extract is refreshed.
- `demand_mw`, generation-source fields, and `exchange_mw` are daily arithmetic
  means of available source readings. **MW is average power, not daily energy in
  MWh.**
- Positive `ech_physiques` means importer; negative means exporter, following
  the source's definition.
- Production coverage is the sum of nuclear, wind (onshore and offshore), solar,
  hydro, thermal, and bioenergy means divided by mean consumption. It is a
  comparative ratio, not a measure of self-sufficiency or reliability.

## Assumptions and limitations

1. The dashboard packages 12 metropolitan regions; it does not represent
   overseas regions.
2. Region-days with fewer than 36 readings are excluded. This removes days with
   less than 75% of a nominal 48 half-hourly observations; daylight-saving days
   can naturally have 46 or 50.
3. Regional physical exchanges are shown as aggregate import/export balance.
   They are not a source-to-destination flow matrix and cannot show which region
   supplied another.
4. A region's reported production can differ from consumption because of
   exchanges, storage, pumped hydro, network losses, and source boundaries.
5. The map uses approximate regional centroids, not official administrative
   polygons.
6. The scenario holds demand and all other generation fixed. It assumes added
   wind and solar first reduce imports and then increase exports. It does not
   model weather, dispatch, curtailment, storage, network constraints, or cost;
   it is an illustration, not a forecast.
7. Recent data can be incomplete or revised. Check the date coverage and refresh
   the source before presenting exact values.

## Project files

- `app.py` — Streamlit shell, page routing, shared filters, and visual theme.
- `sections/intro.py` — the hook, audience, question, and story map.
- `sections/overview.py` — national KPIs, exchange map, comparison, and trends.
- `sections/deep_dives.py` — regional mix, seasonal heatmap, and comparisons.
- `sections/scenario.py` — interactive wind-and-solar sensitivity lab.
- `sections/conclusions.py` — takeaways, implications, data notes, and export.
- `utils/io.py` — cached loading, source/license details, and API extraction.
- `utils/prep.py` — cleaning, validation, and feature engineering.
- `utils/viz.py` — consistent Plotly chart styling and chart builders.
- `utils/ui.py` — shared navigation and selected-period context.
- `prep.py` — command-line refresh wrapper for the prepared data.
- `data/eco2mix_daily.csv` — packaged daily regional extract used by the app.
- `requirements.txt` — runtime dependencies.
- `.streamlit/config.toml` — light theme and accessible chart accent color.
- `DEMO_SCRIPT.md` — timed walkthrough outline for the 2–4 minute demo.
- `tests/test_prep.py` — focused tests for cleaning, derived features, filters,
  and the packaged extract.

## Rubric alignment

- **Narrative & problem framing:** the opening page defines audience, research
  question, hook, and a five-part storyboard; the last page closes with findings
  and practical next questions.
- **Data work:** the source and license are cited; the extract is API-aggregated,
  cleaned, checked for missing keys, duplicate region-days, negative demand,
  and low-coverage days. Derived coverage and renewable-share features are
  documented and covered by tests.
- **Visualization & UX:** five navigable pages provide shared time and region
  controls, interactive charts, a regional seasonal heatmap, comparison
  selection, and an adjustable scenario with visible assumptions.
- **Engineering quality:** modules separate app routing, I/O, preparation,
  visualization, and narrative pages; loading is cached and data is packaged
  for reproducibility.
- **Communication:** limitations and definitions appear in the dashboard and
  README, and `DEMO_SCRIPT.md` supplies a timed walkthrough.

No implementation can guarantee a particular grade; evaluation depends on the
instructor’s interpretation and the final demonstration.

## Deployment

The app is ready for Streamlit Community Cloud: upload this folder to a Git
repository, set `app.py` as the entry point, and let the platform install
`requirements.txt`. Include `data/eco2mix_daily.csv` in the repository so the
deployed app is immediately usable.
