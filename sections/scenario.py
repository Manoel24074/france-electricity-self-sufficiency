import streamlit as st

from utils.ui import render_page_navigation, story_context
from utils.viz import scenario_comparison

_, period, summary, years = story_context()

st.markdown(
    f'<div class="eyebrow">Chapter 03 · The what-if lab · {years[0]}–{years[1]}</div>'
    "<h1>What if wind and solar output were higher?</h1>",
    unsafe_allow_html=True,
)
st.markdown(
    "A scenario is only as useful as its assumptions. This lab isolates one lever and "
    "keeps the arithmetic visible; it is not a prediction of how the grid would operate."
)
render_page_navigation(3)

left, right = st.columns([0.8, 1.2], gap="large")
regions = sorted(summary["region"].unique())
default_region = st.session_state.get("selected_region", "Grand Est")
if default_region not in regions:
    default_region = regions[0]
with left:
    region = st.selectbox(
        "Choose a region",
        regions,
        index=regions.index(default_region),
        key="scenario_region",
    )
    uplift = st.slider(
        "Increase average wind + solar output",
        min_value=0,
        max_value=100,
        value=25,
        step=5,
        format="%d%%",
        help="The percentage uplift is applied to this region's mean wind and solar generation.",
    )
    st.markdown(
        """
        <div class="story-card">
          <div class="section-label">Scenario assumptions</div>
          <p>Demand and every other generation source remain fixed.</p>
          <p>Extra wind and solar first reduce net imports; if the balance crosses
          zero, they increase net exports.</p>
          <p>No weather, storage, curtailment, dispatch, costs, or network limits
          are modeled.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

selected = summary.loc[summary["region"] == region].iloc[0]
regional_period = period.loc[period["region"] == region]
wind_solar_mw = regional_period[
    ["wind_onshore_mw", "wind_offshore_mw", "solar_mw"]
].sum(axis=1).mean()
additional_mw = wind_solar_mw * uplift / 100
scenario_generation = selected["generation_mw"] + additional_mw
scenario_exchange = selected["exchange_mw"] - additional_mw
scenario_coverage = scenario_generation / selected["demand_mw"] * 100

with right:
    st.plotly_chart(
        scenario_comparison(
            selected["demand_mw"], selected["generation_mw"], additional_mw
        ),
        width="stretch",
        theme=None,
    )
    metrics = st.columns(3)
    metrics[0].metric("Extra output · GW", f"{additional_mw / 1000:+.2f}")
    metrics[1].metric("Coverage after · %", f"{scenario_coverage:.0f}%")
    metrics[2].metric("Exchange after · GW", f"{scenario_exchange / 1000:+.2f}")

st.markdown("## What the scenario means")
st.markdown(
    f'<div class="insight-banner">At a <strong>{uplift}%</strong> uplift, '
    f'{region} would add about <strong>{additional_mw:,.0f} MW</strong> of average '
    f'wind and solar output under these assumptions. The arithmetic moves its '
    f'exchange balance from <strong>{selected["exchange_mw"] / 1000:+.2f} GW</strong> '
    f'to <strong>{scenario_exchange / 1000:+.2f} GW</strong>. Actual system behavior '
    "would depend on when the energy is produced and whether the grid can move or "
    "store it.</div>",
    unsafe_allow_html=True,
)
st.caption(
    "This is a static sensitivity exercise based on period averages. It does not estimate "
    "cost, emissions, reliability, investment need, or causal effects."
)
render_page_navigation(3)
