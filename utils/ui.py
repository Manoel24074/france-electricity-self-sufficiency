from __future__ import annotations

import pandas as pd
import streamlit as st

from utils.io import DATA_PATH, load_data
from utils.prep import filter_period, summarize_regions

PAGES = [
    ("Story", "sections/intro.py", "01"),
    ("National overview", "sections/overview.py", "02"),
    ("Regional explorer", "sections/deep_dives.py", "03"),
    ("What-if lab", "sections/scenario.py", "04"),
    ("Takeaways & data", "sections/conclusions.py", "05"),
]


def render_page_navigation(active_page: int) -> None:
    columns = st.columns(len(PAGES))
    for index, (label, path, number) in enumerate(PAGES):
        columns[index].page_link(
            path,
            label=f"{number}  {label}",
            icon=":material/arrow_forward:" if index == active_page else None,
            use_container_width=True,
        )


def story_context() -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, tuple[int, int]]:
    """Load data and apply the year-window shared by all story pages."""
    if not DATA_PATH.exists():
        st.error("The packaged dataset is missing. Run `python prep.py` and reload.")
        st.stop()
    data = load_data(str(DATA_PATH), DATA_PATH.stat().st_mtime)
    years = st.session_state.get(
        "year_range", (int(data["year"].min()), int(data["year"].max()))
    )
    period = filter_period(data, years)
    if period.empty:
        st.warning("No data is available in this year window.")
        st.stop()
    return data, period, summarize_regions(period), years


def render_brand() -> None:
    st.markdown(
        '<div class="brand-mark"><span class="brand-bolt">⚡</span>'
        '<span>THE REGIONAL GRID</span></div>',
        unsafe_allow_html=True,
    )
