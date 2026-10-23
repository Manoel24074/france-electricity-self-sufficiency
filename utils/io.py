from __future__ import annotations

from datetime import date
from pathlib import Path

import pandas as pd
import requests
import streamlit as st

from utils.prep import clean_daily_data

SOURCE_URL = (
    "https://www.data.gouv.fr/datasets/"
    "donnees-eco2mix-regionales-consolidees-et-definitives"
)
API_URL = (
    "https://odre.opendatasoft.com/api/explore/v2.1/catalog/datasets/"
    "eco2mix-regional-cons-def/records"
)
LICENSE_TEXT = (
    "Open Data Licence 2.0 (Etalab). Source: RTE éCO2mix regional consolidated "
    "and definitive data."
)
DATA_PATH = Path(__file__).resolve().parents[1] / "data" / "eco2mix_daily.csv"
PAGE_SIZE = 10_000
SELECT = ",".join(
    [
        "code_insee_region",
        "libelle_region",
        "nature",
        "date",
        "count(*) as intervals",
        "avg(consommation) as demand_mw",
        "avg(thermique) as thermal_mw",
        "avg(nucleaire) as nuclear_mw",
        "avg(eolien_terrestre) as wind_onshore_mw",
        "avg(eolien_offshore) as wind_offshore_mw",
        "avg(solaire) as solar_mw",
        "avg(hydraulique) as hydro_mw",
        "avg(bioenergies) as bioenergy_mw",
        "avg(ech_physiques) as exchange_mw",
    ]
)


@st.cache_data(show_spinner="Loading and validating the regional data…")
def load_data(path: str, modified_at: float) -> pd.DataFrame:
    del modified_at
    raw = pd.read_csv(path)
    return clean_daily_data(raw)


def fetch_and_cache(start_date: str, output_path: Path = DATA_PATH) -> pd.DataFrame:
    """Fetch API-aggregated daily summaries in bounded calendar-year requests."""
    rows: list[dict] = []
    session = requests.Session()
    session.headers.update({"User-Agent": "eco2mix-story-dashboard/1.0"})
    first_year = pd.Timestamp(start_date).year

    for year in range(first_year, date.today().year + 1):
        lower_bound = start_date if year == first_year else f"{year}-01-01"
        params = {
            "select": SELECT,
            "where": (
                f"date_heure >= '{lower_bound}T00:00:00' "
                f"and date_heure < '{year + 1}-01-01T00:00:00'"
            ),
            "group_by": "code_insee_region,libelle_region,nature,date",
            "order_by": "date asc,code_insee_region asc",
            "limit": PAGE_SIZE,
        }
        response = session.get(API_URL, params=params, timeout=90)
        response.raise_for_status()
        page = response.json().get("results")
        if not isinstance(page, list):
            raise ValueError("The data API response did not contain a results list.")
        if len(page) >= PAGE_SIZE:
            raise ValueError(
                f"The {year} partition reached the API page limit; "
                "narrow the extraction range before retrying."
            )
        rows.extend(page)
        print(f"Retrieved {len(page):,} daily regional summaries for {year}.")

    if not rows:
        raise ValueError(f"No data was returned from {start_date} onward.")

    raw = pd.DataFrame(rows).rename(
        columns={"code_insee_region": "code", "libelle_region": "region"}
    )
    cleaned = clean_daily_data(raw)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    cleaned.to_csv(output_path, index=False, date_format="%Y-%m-%d")
    return cleaned
