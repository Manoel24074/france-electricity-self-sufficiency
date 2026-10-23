from __future__ import annotations

import pandas as pd

GENERATION_COLUMNS = {
    "Nuclear": "nuclear_mw",
    "Wind onshore": "wind_onshore_mw",
    "Wind offshore": "wind_offshore_mw",
    "Solar": "solar_mw",
    "Hydro": "hydro_mw",
    "Thermal": "thermal_mw",
    "Bioenergy": "bioenergy_mw",
}
RENEWABLE_COLUMNS = [
    "wind_onshore_mw",
    "wind_offshore_mw",
    "solar_mw",
    "hydro_mw",
    "bioenergy_mw",
]
NUMERIC_COLUMNS = [
    "intervals",
    "demand_mw",
    *GENERATION_COLUMNS.values(),
    "exchange_mw",
]
REGION_COORDINATES = {
    "Auvergne-Rhône-Alpes": (45.6, 4.5),
    "Bourgogne-Franche-Comté": (47.2, 5.4),
    "Bretagne": (48.1, -2.9),
    "Centre-Val de Loire": (47.5, 1.7),
    "Grand Est": (48.7, 6.3),
    "Hauts-de-France": (50.2, 2.8),
    "Île-de-France": (48.7, 2.5),
    "Normandie": (49.1, 0.3),
    "Nouvelle-Aquitaine": (45.0, 0.2),
    "Occitanie": (43.7, 2.1),
    "Pays de la Loire": (47.4, -0.7),
    "Provence-Alpes-Côte d'Azur": (43.9, 6.0),
}


def clean_daily_data(frame: pd.DataFrame) -> pd.DataFrame:
    """Normalize source summaries and derive comparable daily features."""
    required = {"code", "region", "date", "nature", *NUMERIC_COLUMNS}
    missing = required.difference(frame.columns)
    if missing:
        raise ValueError(f"Dataset is missing required columns: {', '.join(sorted(missing))}")

    cleaned = frame.copy()
    cleaned["date"] = pd.to_datetime(cleaned["date"], errors="coerce")
    for column in NUMERIC_COLUMNS:
        cleaned[column] = pd.to_numeric(cleaned[column], errors="coerce")
    cleaned = cleaned.dropna(
        subset=["date", "code", "region", "nature", "demand_mw", "intervals"]
    )
    cleaned = cleaned[cleaned["intervals"] >= 36].copy()

    duplicates = cleaned.duplicated(["code", "date"], keep=False)
    if duplicates.any():
        count = cleaned.loc[duplicates, ["code", "date"]].drop_duplicates().shape[0]
        raise ValueError(f"Dataset contains {count} duplicate region-day keys.")
    if cleaned["demand_mw"].lt(0).any():
        raise ValueError("Dataset contains negative consumption readings.")

    cleaned["generation_mw"] = cleaned[list(GENERATION_COLUMNS.values())].sum(
        axis=1, min_count=1
    )
    cleaned["renewables_mw"] = cleaned[RENEWABLE_COLUMNS].sum(
        axis=1, min_count=1
    )
    cleaned["renewable_share_pct"] = (
        cleaned["renewables_mw"]
        .div(cleaned["generation_mw"].where(cleaned["generation_mw"] > 0))
        .mul(100)
    )
    cleaned["coverage_pct"] = (
        cleaned["generation_mw"]
        .div(cleaned["demand_mw"].where(cleaned["demand_mw"] > 0))
        .mul(100)
    )
    cleaned["month"] = cleaned["date"].dt.to_period("M").dt.to_timestamp()
    cleaned["year"] = cleaned["date"].dt.year
    return cleaned.sort_values(["date", "region"]).reset_index(drop=True)


def filter_period(frame: pd.DataFrame, years: tuple[int, int]) -> pd.DataFrame:
    """Apply the shared year-window selection."""
    start = pd.Timestamp(years[0], 1, 1)
    end = pd.Timestamp(years[1], 12, 31)
    return frame.loc[frame["date"].between(start, end)].copy()


def summarize_regions(frame: pd.DataFrame) -> pd.DataFrame:
    """Return region-level mean power and derived coverage for the selected period."""
    summary = (
        frame.groupby(["code", "region"], as_index=False)
        .agg(
            demand_mw=("demand_mw", "mean"),
            generation_mw=("generation_mw", "mean"),
            exchange_mw=("exchange_mw", "mean"),
            renewables_mw=("renewables_mw", "mean"),
        )
        .assign(
            coverage_pct=lambda rows: rows["generation_mw"]
            .div(rows["demand_mw"].where(rows["demand_mw"] > 0))
            .mul(100)
        )
    )
    return summary


def monthly_region_data(frame: pd.DataFrame, region: str) -> pd.DataFrame:
    """Aggregate one region to monthly mean power values."""
    regional = frame.loc[frame["region"] == region]
    aggregation = {
        label: (column, "mean")
        for label, column in GENERATION_COLUMNS.items()
    }
    aggregation.update(
        {
            "Demand": ("demand_mw", "mean"),
            "Exchange": ("exchange_mw", "mean"),
            "Renewable share": ("renewable_share_pct", "mean"),
        }
    )
    return regional.groupby("month", as_index=False).agg(**aggregation)
