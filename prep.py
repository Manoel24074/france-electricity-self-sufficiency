from __future__ import annotations

import argparse
import sys

import pandas as pd

from utils.io import DATA_PATH, fetch_and_cache


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Download and validate daily regional éCO2mix summaries."
    )
    parser.add_argument(
        "--start-date",
        default="2021-01-01",
        help="First date to include (YYYY-MM-DD; default: 2021-01-01).",
    )
    args = parser.parse_args()
    try:
        start_date = pd.Timestamp(args.start_date).date().isoformat()
    except (TypeError, ValueError):
        parser.error("--start-date must be a valid date in YYYY-MM-DD format")

    frame = fetch_and_cache(start_date, DATA_PATH)
    print(
        f"Saved {len(frame):,} rows × {len(frame.columns)} columns to {DATA_PATH}\n"
        f"Date range: {frame['date'].min():%Y-%m-%d} to {frame['date'].max():%Y-%m-%d}\n"
        f"Regions: {frame['region'].nunique()}",
        flush=True,
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
