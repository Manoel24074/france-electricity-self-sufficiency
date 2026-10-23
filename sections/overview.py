import streamlit as st

from utils.ui import render_page_navigation, story_context
from utils.viz import coverage_ranking, exchange_map, exchange_ranking, national_trend

_, period, summary, years = story_context()

st.markdown(
    f'<div class="eyebrow">Chapter 01 · The national picture · {years[0]}–{years[1]}</div>'
    "<h1>There is no single regional electricity story.</h1>",
    unsafe_allow_html=True,
)
st.markdown(
    "Regional exchanges tell us where the balance leans. Production coverage adds "
    "another lens—but neither is a measure of isolation from the grid."
)
render_page_navigation(1)

national_demand = summary["demand_mw"].sum()
national_generation = summary["generation_mw"].sum()
net_importers = int(summary["exchange_mw"].gt(0).sum())
metrics = st.columns(4)
metrics[0].metric("Mean demand · GW", f"{national_demand / 1000:,.1f}")
metrics[1].metric("Mean generation · GW", f"{national_generation / 1000:,.1f}")
metrics[2].metric("Production / demand", f"{national_generation / national_demand:.0%}")
metrics[3].metric("Net-importing regions", f"{net_importers} / {len(summary)}")

largest_importer = summary.loc[summary["exchange_mw"].idxmax()]
largest_exporter = summary.loc[summary["exchange_mw"].idxmin()]
st.markdown(
    f'<div class="insight-banner"><strong>Read the map:</strong> '
    f'{largest_importer["region"]} is the largest average importer '
    f'({largest_importer["exchange_mw"] / 1000:+.1f} GW); '
    f'{largest_exporter["region"]} is the largest average exporter '
    f'({largest_exporter["exchange_mw"] / 1000:+.1f} GW). '
    "A positive exchange is an import; a negative exchange is an export.</div>",
    unsafe_allow_html=True,
)

left, right = st.columns([1.05, 0.95], gap="medium")
with left:
    st.plotly_chart(exchange_map(summary), width="stretch", theme=None)
with right:
    st.plotly_chart(exchange_ranking(summary), width="stretch", theme=None)

st.caption(
    "Map markers use approximate regional centroids, not region boundaries. Exchanges "
    "are not source-to-destination flows and do not show which region supplied another."
)

st.markdown("## Production coverage: a useful ratio, not independence")
coverage, note = st.columns([1.15, 0.85], gap="large")
with coverage:
    st.plotly_chart(coverage_ranking(summary), width="stretch", theme=None)
with note:
    st.markdown(
        """
        <div class="story-card">
          <div class="section-label">How to read this</div>
          <strong>Mean generation ÷ mean demand</strong>
          <p>Above 100% means average generation is greater than average demand
          over the selected window. Below 100% means the reverse.</p>
          <p>This comparison does not account for when electricity is generated,
          network constraints, losses, storage, or the direction of every flow.
          It is not a self-sufficiency or reliability score.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

st.markdown("## The national trend changes with the question")
metric = st.selectbox(
    "Choose the monthly trend",
    ["Demand", "Generation", "Renewable generation"],
    key="overview_trend",
)
column = {
    "Demand": "demand_mw",
    "Generation": "generation_mw",
    "Renewable generation": "renewables_mw",
}[metric]
st.plotly_chart(national_trend(period, column), width="stretch", theme=None)
st.caption(
    "The chart sums regional monthly mean power values to make a national-scale "
    "comparison. It is not a total-energy series."
)
render_page_navigation(1)
