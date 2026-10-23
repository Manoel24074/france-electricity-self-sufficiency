import streamlit as st

from utils.ui import render_page_navigation, story_context

_, period, summary, years = story_context()

st.markdown(
    f"""
    <div class="hero">
      <div class="eyebrow">A regional electricity story · {years[0]}–{years[1]}</div>
      <h1>Electricity is made in one place.<br>It’s needed in another.</h1>
      <div class="hero-copy">
        France’s power system connects regions with very different production and demand.
        Explore what the regional data reveals—and where the story needs a closer look.
      </div>
    </div>
    """,
    unsafe_allow_html=True,
)
render_page_navigation(0)

largest_importer = summary.loc[summary["exchange_mw"].idxmax()]
largest_exporter = summary.loc[summary["exchange_mw"].idxmin()]
importer_count = int(summary["exchange_mw"].gt(0).sum())
col1, col2, col3 = st.columns(3)
col1.metric("Regions in view", f"{summary['region'].nunique()}")
col2.metric("Net importers", f"{importer_count} / {len(summary)}")
col3.metric("Largest exchange gap", f"{abs(largest_importer['exchange_mw'] - largest_exporter['exchange_mw']) / 1000:.1f} GW")

st.markdown(
    f"""
    <div class="insight-banner">
      <span class="section-label">The opening insight</span><br>
      <strong>{largest_importer['region']}</strong> has the largest average net import
      balance, while <strong>{largest_exporter['region']}</strong> has the largest average
      net export balance in this period. The dataset describes each region’s net exchange;
      it does not say which region supplied another.
    </div>
    """,
    unsafe_allow_html=True,
)

st.markdown("## The question behind the story")
st.markdown(
    "**How do production, demand, and physical electricity exchanges differ across "
    "France’s regions—and what might a simple renewable-output increase change?**"
)

story_cols = st.columns(3, gap="medium")
story = [
    (
        "01 · SEE THE SYSTEM",
        "Compare exchanges and production coverage across all regions. "
        "Who generates more power than local demand—and who imports?",
        "National overview",
        "sections/overview.py",
    ),
    (
        "02 · FOLLOW A REGION",
        "Explore how a region’s generation mix changes through the year, "
        "and compare monthly and seasonal patterns.",
        "Regional explorer",
        "sections/deep_dives.py",
    ),
    (
        "03 · TEST AN ASSUMPTION",
        "Adjust wind and solar output in a deliberately simple scenario. "
        "See what the arithmetic implies—and what it leaves out.",
        "What-if lab",
        "sections/scenario.py",
    ),
]
for column, (label, copy, button, path) in zip(story_cols, story, strict=True):
    with column:
        st.markdown(
            f'<div class="story-card"><div class="section-label">{label}</div>'
            f"<strong>{button}</strong><p>{copy}</p></div>",
            unsafe_allow_html=True,
        )
        st.page_link(path, label=f"Explore {button} →", use_container_width=True)

st.markdown("### Who this is for")
st.markdown(
    "For citizens, students, and regional decision-makers interested in how electricity "
    "production and demand are distributed—and why regional balance is only one part of "
    "a reliable national grid."
)
st.caption(
    "The packaged extract covers 12 metropolitan regions. Daily observations are mean "
    "power (MW), not total energy (MWh). The source and assumptions are documented in "
    "the final page."
)
render_page_navigation(0)
