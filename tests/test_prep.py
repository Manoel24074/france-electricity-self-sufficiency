from __future__ import annotations

import unittest

import pandas as pd

from utils.io import DATA_PATH
from utils.prep import clean_daily_data, filter_period, summarize_regions


def sample_row(
    *,
    code: str = "11",
    region: str = "Île-de-France",
    date: str = "2025-01-01",
    intervals: int = 48,
) -> dict[str, object]:
    return {
        "code": code,
        "region": region,
        "nature": "Données définitives",
        "date": date,
        "intervals": intervals,
        "demand_mw": 1000,
        "thermal_mw": 100,
        "nuclear_mw": 200,
        "wind_onshore_mw": 50,
        "wind_offshore_mw": 0,
        "solar_mw": 30,
        "hydro_mw": 20,
        "bioenergy_mw": 10,
        "exchange_mw": 75,
    }


class CleanDailyDataTests(unittest.TestCase):
    def test_feature_engineering_uses_expected_technology_groups(self) -> None:
        result = clean_daily_data(pd.DataFrame([sample_row()])).iloc[0]

        self.assertEqual(result["generation_mw"], 410)
        self.assertEqual(result["renewables_mw"], 110)
        self.assertAlmostEqual(result["coverage_pct"], 41.0)
        self.assertAlmostEqual(result["renewable_share_pct"], 110 / 410 * 100)

    def test_incomplete_days_are_filtered(self) -> None:
        result = clean_daily_data(
            pd.DataFrame([sample_row(), sample_row(date="2025-01-02", intervals=35)])
        )

        self.assertEqual(len(result), 1)
        self.assertEqual(result.iloc[0]["date"], pd.Timestamp("2025-01-01"))

    def test_duplicate_region_days_fail_validation(self) -> None:
        with self.assertRaisesRegex(ValueError, "duplicate region-day"):
            clean_daily_data(pd.DataFrame([sample_row(), sample_row()]))

    def test_shared_period_filter_and_region_summary(self) -> None:
        rows = [
            sample_row(date="2024-12-31"),
            sample_row(date="2025-01-01"),
            sample_row(code="24", region="Centre-Val de Loire", date="2025-01-01"),
        ]
        cleaned = clean_daily_data(pd.DataFrame(rows))
        period = filter_period(cleaned, (2025, 2025))
        summary = summarize_regions(period)

        self.assertEqual(len(period), 2)
        self.assertEqual(set(summary["region"]), {"Île-de-France", "Centre-Val de Loire"})
        self.assertEqual(len(summary), 2)

    def test_packaged_extract_has_unique_valid_region_days(self) -> None:
        raw = pd.read_csv(DATA_PATH)
        cleaned = clean_daily_data(raw)

        self.assertEqual(cleaned["region"].nunique(), 12)
        self.assertGreaterEqual(cleaned["intervals"].min(), 36)
        self.assertFalse(cleaned.duplicated(["code", "date"]).any())
        self.assertFalse(cleaned["demand_mw"].lt(0).any())


if __name__ == "__main__":
    unittest.main()
