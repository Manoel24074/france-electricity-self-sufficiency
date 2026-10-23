from __future__ import annotations

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

from utils.prep import REGION_COORDINATES

COLORS = {
    "Nuclear": "#7357C8",
    "Wind onshore": "#00A88F",
    "Wind offshore": "#3CC8BA",
    "Solar": "#F2B544",
    "Hydro": "#4386E8",
    "Thermal": "#E9784B",
    "Bioenergy": "#92B85A",
    "Import": "#E9784B",
    "Export": "#4386E8",
}
INK = "#15283b"
GRID = "#e9eef2"


def style_figure(figure: go.Figure, height: int = 450) -> go.Figure:
    figure.update_layout(
        template="plotly_white",
        paper_bgcolor="#ffffff",
        plot_bgcolor="#ffffff",
        font=dict(family="DM Sans", color=INK),
        height=height,
        margin=dict(l=12, r=12, t=55, b=12),
        hoverlabel=dict(bgcolor="#102438", font_color="#ffffff"),
    )
    return figure


def exchange_map(summary: pd.DataFrame) -> go.Figure:
    frame = summary.copy()
    frame[["latitude", "longitude"]] = frame["region"].apply(
        lambda name: pd.Series(REGION_COORDINATES.get(name, (46.5, 2.5)))
    )
    frame["Flow"] = frame["exchange_mw"].apply(
        lambda value: "Import" if value >= 0 else "Export"
    )
    frame["Balance"] = frame["exchange_mw"].apply(
        lambda value: f"{abs(value) / 1000:.2f} GW "
        + ("import" if value >= 0 else "export")
    )
    figure = px.scatter_geo(
        frame,
        lat="latitude",
        lon="longitude",
        size=frame["exchange_mw"].abs(),
        color="Flow",
        color_discrete_map={"Import": COLORS["Import"], "Export": COLORS["Export"]},
        hover_name="region",
        hover_data={
            "Balance": True,
            "coverage_pct": ":.0f",
            "latitude": False,
            "longitude": False,
            "exchange_mw": False,
            "Flow": False,
        },
        size_max=46,
        projection="mercator",
        labels={"coverage_pct": "Production / demand (%)"},
    )
    figure.update_geos(
        scope="europe",
        center={"lat": 46.6, "lon": 2.4},
        projection_scale=5.7,
        showland=True,
        landcolor="#edf1f4",
        showcountries=True,
        countrycolor="#cad3dc",
        showocean=True,
        oceancolor="#f8fafc",
        showcoastlines=False,
        lataxis_range=[41.5, 51.5],
        lonaxis_range=[-5.8, 10.2],
    )
    figure.update_layout(title="Regional exchanges by sign", legend_title_text="Mean flow")
    return style_figure(figure, 490)


def exchange_ranking(summary: pd.DataFrame) -> go.Figure:
    frame = summary.sort_values("exchange_mw").copy()
    frame["Flow"] = frame["exchange_mw"].apply(
        lambda value: "Net exporter" if value < 0 else "Net importer"
    )
    figure = px.bar(
        frame,
        x="exchange_mw",
        y="region",
        orientation="h",
        color="Flow",
        color_discrete_map={
            "Net importer": COLORS["Import"],
            "Net exporter": COLORS["Export"],
        },
        labels={"exchange_mw": "Mean physical exchange (MW)", "region": ""},
        hover_data={"exchange_mw": ":,.0f", "Flow": False},
    )
    figure.add_vline(x=0, line_color=INK, line_width=1)
    figure.update_layout(
        title="Mean exchange balance",
        showlegend=False,
        xaxis=dict(zeroline=False, gridcolor=GRID),
        yaxis=dict(categoryorder="array", categoryarray=frame["region"].tolist()),
    )
    return style_figure(figure, 490)


def coverage_ranking(summary: pd.DataFrame) -> go.Figure:
    frame = summary.sort_values("coverage_pct").copy()
    frame["Coverage"] = frame["coverage_pct"].apply(
        lambda value: "Above 100%" if value >= 100 else "Below 100%"
    )
    figure = px.bar(
        frame,
        x="coverage_pct",
        y="region",
        orientation="h",
        color="Coverage",
        color_discrete_map={"Above 100%": "#167b72", "Below 100%": "#a6b3c1"},
        labels={"coverage_pct": "Mean generation ÷ mean demand (%)", "region": ""},
        hover_data={"coverage_pct": ":.1f", "Coverage": False},
    )
    figure.add_vline(
        x=100, line_dash="dash", line_color=INK, annotation_text="100% reference"
    )
    figure.update_layout(
        showlegend=True,
        legend_title_text="",
        xaxis=dict(gridcolor=GRID, rangemode="tozero"),
        yaxis=dict(categoryorder="array", categoryarray=frame["region"].tolist()),
    )
    return style_figure(figure, 470)


def national_trend(frame: pd.DataFrame, metric: str = "demand_mw") -> go.Figure:
    labels = {
        "demand_mw": "Average demand (GW)",
        "generation_mw": "Average generation (GW)",
        "renewables_mw": "Average renewable generation (GW)",
    }
    monthly = (
        frame.groupby(["month", "region"], as_index=False)[
            ["demand_mw", "generation_mw", "renewables_mw"]
        ]
        .mean()
        .groupby("month", as_index=False)[
            ["demand_mw", "generation_mw", "renewables_mw"]
        ]
        .sum()
    )
    figure = go.Figure()
    figure.add_trace(
        go.Scatter(
            x=monthly["month"],
            y=monthly[metric] / 1000,
            mode="lines",
            name=labels[metric],
            line=dict(color="#167b72", width=3),
            fill="tozeroy",
            fillcolor="rgba(22,123,114,.10)",
        )
    )
    figure.update_layout(title=labels[metric], hovermode="x unified", yaxis_title="GW")
    figure.update_xaxes(gridcolor=GRID)
    figure.update_yaxes(gridcolor=GRID, rangemode="tozero")
    return style_figure(figure, 360)


def monthly_mix(monthly: pd.DataFrame, generation_columns: dict[str, str]) -> go.Figure:
    figure = go.Figure()
    for label in generation_columns:
        figure.add_trace(
            go.Bar(
                x=monthly["month"],
                y=monthly[label],
                name=label,
                marker_color=COLORS[label],
                hovertemplate="%{x|%b %Y}<br>"
                + label
                + ": %{y:,.0f} MW<extra></extra>",
            )
        )
    figure.add_trace(
        go.Scatter(
            x=monthly["month"],
            y=monthly["Demand"],
            name="Demand",
            mode="lines",
            line=dict(color=INK, width=2.5, dash="dot"),
            hovertemplate="%{x|%b %Y}<br>Demand: %{y:,.0f} MW<extra></extra>",
        )
    )
    figure.update_layout(
        barmode="stack",
        title="Generation by source and demand",
        hovermode="x unified",
        yaxis_title="Monthly average power (MW)",
        legend=dict(orientation="h", y=-0.25, x=0, title_text=""),
    )
    figure.update_xaxes(gridcolor=GRID, title_text="")
    figure.update_yaxes(gridcolor=GRID, rangemode="tozero")
    return style_figure(figure, 470)


def monthly_heatmap(frame: pd.DataFrame, region: str, metric: str) -> go.Figure:
    regional = frame.loc[frame["region"] == region].copy()
    monthly = regional.groupby(["year", regional["date"].dt.month.rename("month")])[
        metric
    ].mean().reset_index(name="value")
    pivot = monthly.pivot(index="year", columns="month", values="value")
    metric_label = {
        "renewable_share_pct": "Renewable share (%)",
        "coverage_pct": "Production coverage (%)",
    }.get(metric, metric.replace("_", " ").title())
    figure = px.imshow(
        pivot,
        aspect="auto",
        color_continuous_scale=["#edf5f4", "#75b8aa", "#167b72", "#102438"],
        labels={"x": "Month", "y": "Year", "color": metric_label},
        x=["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"],
    )
    figure.update_layout(title="Seasonality at a glance", coloraxis_colorbar=dict(len=0.8))
    return style_figure(figure, 330)


def scenario_comparison(
    demand_mw: float, generation_mw: float, additional_mw: float
) -> go.Figure:
    figure = go.Figure()
    figure.add_trace(
        go.Bar(
            x=["Baseline", "Wind + solar uplift"],
            y=[generation_mw / 1000, (generation_mw + additional_mw) / 1000],
            name="Generation",
            marker_color="#167b72",
        )
    )
    figure.add_trace(
        go.Scatter(
            x=["Baseline", "Wind + solar uplift"],
            y=[demand_mw / 1000, demand_mw / 1000],
            mode="lines+markers",
            name="Demand (held fixed)",
            line=dict(color=INK, width=3, dash="dot"),
        )
    )
    figure.update_layout(
        title="Scenario balance vs. fixed demand",
        yaxis_title="Average power (GW)",
        legend=dict(orientation="h", y=-0.25, x=0),
    )
    figure.update_yaxes(gridcolor=GRID, rangemode="tozero")
    return style_figure(figure, 390)
