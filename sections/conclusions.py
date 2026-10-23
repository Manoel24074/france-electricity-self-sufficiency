import streamlit as st

from utils.io import LICENSE_TEXT, SOURCE_URL
from utils.ui import render_page_navigation, story_context

data, period, summary, years = story_context()

st.markdown(
    f'<div class="eyebrow">Final chapter · {years[0]}–{years[1]}</div>'
    "<h1>The grid is shared. The geography is not.</h1>",
    unsafe_allow_html=True,
)
st.markdown(
    "Regional data makes imbalances visible, but a national electricity system is more "
    "than the sum of local production totals. The network, timing, storage, and demand "
    "shape what can actually be delivered."
)
render_page_navigation(4)

largest_importer = summary.loc[summary["exchange_mw"].idxmax()]
largest_exporter = summary.loc[summary["exchange_mw"].idxmin()]
under_coverage = int(summary["coverage_pct"].lt(100).sum())

insights = [
    (
        "01 · Production is uneven",
        f"{largest_importer['region']} has the largest average net import balance, "
        f"while {largest_exporter['region']} has the largest average net export balance "
        f"in this selected period.",
    ),
    (
        "02 · Coverage is not independence",
        f"{under_coverage} of {len(summary)} regions have mean production below mean "
        "consumption. Regions above 100% still depend on grid connections and the timing "
        "of generation and demand.",
    ),
    (
        "03 · More generation is not a dispatch plan",
        "A wind-and-solar uplift changes the simple accounting balance, but it does not "
        "model when output arrives, where it can flow, or how the grid responds.",
    ),
]
for index in range(0, len(insights), 3):
    columns = st.columns(3, gap="medium")
    for column, (title, text) in zip(columns, insights[index:index + 3], strict=True):
        column.markdown(
            f'<div class="story-card"><div class="section-label">{title}</div>'
            f"<p>{text}</p></div>",
            unsafe_allow_html=True,
        )

st.markdown("## What decision-makers should ask next")
st.markdown(
    """
    - Where are grid reinforcement and flexibility most valuable at the time of peak demand?
    - How do storage, pumped hydro, and demand response change the regional balance?
    - Which renewable resources complement local demand patterns across seasons?
    - What changes when we compare hourly energy, rather than averages across a day or month?
    """
)

st.markdown("## Data & transparency")
nature = ", ".join(sorted(period["nature"].dropna().unique()))
st.markdown(
    f"""
    **Source:** [RTE éCO2mix regional consolidated and definitive data]({SOURCE_URL})  
    **License:** {LICENSE_TEXT}  
    **Extract:** {len(data):,} validated region-days, {data['region'].nunique()} metropolitan
    regions, {data['date'].min():%d %B %Y}–{data['date'].max():%d %B %Y}.  
    **Source status in this selection:** {nature}.
    """
)

with st.expander("Definitions, quality checks & limitations"):
    st.markdown(
        """
        - Source readings are half-hourly. The packaged data contains daily means of
          available readings, not daily energy totals in MWh.
        - Region-days with fewer than 36 readings are excluded. A daylight-saving day
          can contain 46 or 50 half-hourly intervals.
        - The regional physical-exchange sign follows the source: positive = importer,
          negative = exporter. These balances do not show direct region-to-region routes.
        - Production is the sum of seven reported technologies. The production/demand
          ratio is descriptive and does not measure reliability or energy independence.
        - The data is derived from metering and may include estimates; recent consolidated
          observations can be revised. This dashboard keeps the source `nature` status.
        - The map uses approximate regional centroids. Overseas regions are not included.
        - The what-if model holds demand and other production fixed and applies additional
          wind and solar output directly to the net balance. It is not a forecast.
        """
    )

csv = period.to_csv(index=False).encode("utf-8")
st.download_button(
    "Download the filtered daily data",
    csv,
    file_name=f"eco2mix_daily_{years[0]}-{years[1]}.csv",
    mime="text/csv",
    type="primary",
)
st.caption(
    f"To refresh the packaged extract, run `python prep.py`. "
    f"The license and source definitions are available at the dataset page: {SOURCE_URL}."
)
render_page_navigation(4)
