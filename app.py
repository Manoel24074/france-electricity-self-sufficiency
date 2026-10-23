from __future__ import annotations

import streamlit as st

from utils.io import DATA_PATH, LICENSE_TEXT, SOURCE_URL, load_data
from utils.ui import PAGES, render_brand

st.set_page_config(
    page_title="The Regional Grid | France electricity story",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Manrope:wght@400;500;600;700;800&display=swap');
    :root { --ink: #15283b; --muted: #64758a; --paper: #f5f7fa; --line: #e2e8ef; --teal: #167b72; }
    html, body, [class*="css"] { font-family: 'DM Sans', sans-serif; }
    .stApp { background: var(--paper); color: var(--ink); }
    h1, h2, h3 { font-family: 'Manrope', sans-serif; letter-spacing: -.035em; }
    h1 { font-size: clamp(2.1rem, 4vw, 3.25rem) !important; line-height: 1.08 !important; }
    .block-container { max-width: 1480px; padding: 1.4rem 2rem 4rem; }
    [data-testid="stSidebar"] { background: #102438; }
    [data-testid="stSidebar"] * { color: #edf4fa; }
    [data-testid="stSidebar"] [data-testid="stWidgetLabel"] { color: #d2e0eb !important; }
    [data-testid="stSidebar"] [data-testid="stCaptionContainer"] { color: #bbcad6; }
    [data-testid="stMetric"] { background: #fff; border: 1px solid var(--line); border-radius: 14px; padding: 15px 18px; box-shadow: 0 4px 16px rgba(21,40,59,.035); }
    [data-testid="stMetricValue"] { color: var(--ink) !important; }
    [data-testid="stMetricLabel"] { color: var(--muted) !important; }
    .brand-mark { display: flex; align-items: center; gap: .6rem; color: #edf4fa; font-weight: 700; letter-spacing: .12em; font-size: .78rem; padding: .35rem 0 1rem; }
    .brand-bolt { display: inline-grid; place-items: center; width: 2rem; height: 2rem; border-radius: 10px; background: #167b72; color: white; font-size: 1.15rem; }
    .eyebrow, .section-label { color: var(--teal); font-size: .76rem; font-weight: 700; letter-spacing: .13em; text-transform: uppercase; }
    .hero { padding: 1.5rem 0 1rem; }
    .hero h1 { font-size: clamp(2.5rem, 5.2vw, 4.6rem) !important; max-width: 1050px; margin: .5rem 0 1rem; }
    .hero-copy { color: #50657b; font-size: 1.13rem; max-width: 880px; line-height: 1.65; }
    .insight-banner { background: #fff; border: 1px solid #cce4df; border-left: 5px solid var(--teal); border-radius: 12px; padding: 17px 21px; color: var(--ink); line-height: 1.65; margin: .7rem 0 1rem; }
    .story-card { background: white; border: 1px solid var(--line); border-radius: 14px; padding: 20px 22px; height: 100%; box-shadow: 0 4px 16px rgba(21,40,59,.035); }
    .story-card strong { color: var(--ink); }
    .story-card p { color: var(--muted); margin: .55rem 0 0; line-height: 1.6; }
    .small-note { color: var(--muted); font-size: .88rem; }
    div[data-testid="stPlotlyChart"] { background: #fff; border: 1px solid var(--line); border-radius: 14px; padding: 8px; }
    div[data-testid="stPageLink"] a { border-radius: 11px; font-weight: 600; border: 1px solid var(--line); background: #fff; padding: .45rem .65rem; transition: border-color .18s ease, transform .18s ease, box-shadow .18s ease; }
    div[data-testid="stPageLink"] a:hover { border-color: var(--teal); transform: translateY(-1px); box-shadow: 0 5px 14px rgba(21,40,59,.08); }
    div[data-testid="stPageLink"] svg { color: var(--teal); }
    hr { border-color: var(--line); }
    @media (max-width: 760px) { .block-container { padding: 1rem 1rem 3rem; } }
    </style>
    """,
    unsafe_allow_html=True,
)

if not DATA_PATH.exists():
    st.error("The packaged dataset is missing. Run `python prep.py` from the project folder.")
    st.stop()

data = load_data(str(DATA_PATH), DATA_PATH.stat().st_mtime)
if data.empty:
    st.error("The packaged dataset has no valid region-day records.")
    st.stop()

page = st.navigation(
    [
        st.Page(path, title=title, icon=icon, url_path=slug)
        for (title, path, _), icon, slug in zip(
            PAGES,
            [
                ":material/auto_stories:",
                ":material/insights:",
                ":material/public:",
                ":material/tune:",
                ":material/flag:",
            ],
            ["story", "overview", "regions", "what-if", "takeaways"],
            strict=True,
        )
    ],
    position="sidebar",
    expanded=True,
)

with st.sidebar:
    render_brand()
    st.caption("A visual guide to France’s regional electricity balance.")
    st.markdown("---")
    st.markdown("### Set the lens")
    min_year, max_year = int(data["year"].min()), int(data["year"].max())
    st.slider(
        "Years in view",
        min_value=min_year,
        max_value=max_year,
        value=st.session_state.get("year_range", (min_year, max_year)),
        key="year_range",
        help="This shared time window filters all five story pages.",
    )
    st.selectbox(
        "Region focus",
        sorted(data["region"].unique()),
        index=(
            sorted(data["region"].unique()).index(
                st.session_state.get("selected_region", "Grand Est")
            )
            if st.session_state.get("selected_region", "Grand Est")
            in data["region"].unique()
            else 0
        ),
        key="selected_region",
        help="Used as the default region in the explorer and scenario.",
    )
    st.markdown("---")
    st.caption(f"{len(data):,} valid region-days · 12 metropolitan regions")
    st.caption(LICENSE_TEXT)
    st.link_button("Open RTE dataset", SOURCE_URL, use_container_width=True)

page.run()
