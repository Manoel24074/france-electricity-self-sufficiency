import plotly.express as px
import streamlit as st

from utils.prep import GENERATION_COLUMNS, monthly_region_data
from utils.ui import render_page_navigation, story_context
from utils.viz import monthly_heatmap, monthly_mix

_, period, summary, years = story_context()

st.markdown(
    f'<div class="eyebrow">Chapter 02 · The regional explorer · {years[0]}–{years[1]}</div>'
    "<h1>Zoom in. The averages start to tell a story.</h1>",
    unsafe_allow_html=True,
)
st.markdown(
    "Choose a region, inspect its monthly generation mix, then compare the seasonal "
    "pattern with another metric. All values use the year window in the sidebar."
)
render_page_navigation(2)

regions = sorted(summary["region"].unique())
default_region = st.session_state.get("selected_region", "Grand Est")
if default_region not in regions:
    default_region = regions[0]
region = default_region
st.caption(f"Focused region: **{region}** · Change the shared region focus in the sidebar.")
monthly = monthly_region_data(period, region)
regional_summary = summary.loc[summary["region"] == region].iloc[0]
metrics = st.columns(4)
metrics[0].metric("Demand · MW", f"{regional_summary['demand_mw']:,.0f}")
metrics[1].metric("Generation · MW", f"{regional_summary['generation_mw']:,.0f}")
metrics[2].metric("Generation / demand", f"{regional_summary['coverage_pct']:.0f}%")
metrics[3].metric(
    "Exchange · MW",
    f"{regional_summary['exchange_mw']:+,.0f}",
    help="Positive is net import; negative is net export.",
)

st.plotly_chart(monthly_mix(monthly, GENERATION_COLUMNS), width="stretch", theme=None)

metric_choice = st.radio(
    "Color the seasonal heatmap by",
    ["Renewable share of generation", "Production coverage"],
    horizontal=True,
    key="heatmap_metric_choice",
)
heatmap_metric = (
    "renewable_share_pct"
    if metric_choice == "Renewable share of generation"
    else "coverage_pct"
)
heatmap_col, narrative_col = st.columns([1.35, 0.65], gap="large")
with heatmap_col:
    st.plotly_chart(
        monthly_heatmap(period, region, heatmap_metric),
        width="stretch",
        theme=None,
    )
with narrative_col:
    renewable = regional_summary["renewables_mw"]
    renewable_share = renewable / regional_summary["generation_mw"] * 100
    st.markdown(
        f"""
        <div class="story-card">
          <div class="section-label">A regional reading</div>
          <strong>{region}</strong>
          <p>Average renewable generation is <strong>{renewable:,.0f} MW</strong>,
          around <strong>{renewable_share:.0f}%</strong> of the reported generation
          mix over the selected period.</p>
          <p>Seasonal patterns can suggest when a source contributes more. They do
          not tell us whether output is available at a specific peak-demand moment.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

st.markdown("## Compare a few regions")
comparison = st.multiselect(
    "Select up to four regions",
    regions,
    default=[region],
    max_selections=4,
    key="region_comparison",
)
compare_metric = st.selectbox(
    "Compare monthly",
    ["Demand", "Generation", "Renewable share"],
    key="region_compare_metric",
)
metric_columns = {
    "Demand": ("demand_mw", "Mean demand (MW)"),
    "Generation": ("generation_mw", "Mean generation (MW)"),
    "Renewable share": ("renewable_share_pct", "Renewable share (%)"),
}
selected_column, axis_title = metric_columns[compare_metric]
if comparison:
    comparison_data = period[period["region"].isin(comparison)]
    trend = (
        comparison_data.groupby(["month", "region"], as_index=False)[selected_column]
        .mean()
        .sort_values("month")
    )
    figure = px.line(
        trend,
        x="month",
        y=selected_column,
        color="region",
        markers=True,
        labels={"month": "", selected_column: axis_title, "region": "Region"},
        color_discrete_sequence=["#167b72", "#7357C8", "#E9784B", "#4386E8"],
    )
    figure.update_layout(
        title=f"{compare_metric} · monthly regional comparison",
        hovermode="x unified",
        yaxis_title=axis_title,
    )
    figure.update_xaxes(showgrid=False)
    figure.update_yaxes(gridcolor="#e9eef2")
    from utils.viz import style_figure

    st.plotly_chart(style_figure(figure, 400), width="stretch", theme=None)
else:
    st.info("Select at least one region to draw a comparison.")

st.caption(
    "Monthly means smooth daily variability. The national year-window controls are "
    "available in the sidebar; region comparisons retain the same window."
)
render_page_navigation(2)
