"""
Lesson 4 — Demo 3: analyze a time series with Pandas.

We switch from the constituents list to a bundled Treasury-yield time series
(the constituents aren't a time series). We compute the daily change, a rolling
average, and the 2s10s spread, keeping each step in a small named function.

Float-precision reminder: yields here are analytics, so float is fine — but we
still round only at the display boundary, never mid-calculation.

Run from the repo root:
    python lessons/lesson-04-numpy-pandas-data-analysis/demos/03-analysis/analyze.py
"""

from pathlib import Path

import pandas as pd

ROLLING_WINDOW = 3  # trading days

# Bundled time series lives next to the Pandas demo.
CSV_PATH = (
    Path(__file__).resolve().parents[1]
    / "02-pandas-dataframes"
    / "sample_rates.csv"
)


def load_rates(path: Path) -> pd.DataFrame:
    """Load the yield time series, parse dates, and fill the one missing value."""
    df = pd.read_csv(path, parse_dates=["date"]).set_index("date")
    # Explicit missing-data decision: carry the last observation forward.
    df["us_2y"] = df["us_2y"].ffill()
    return df


def add_analysis(df: pd.DataFrame) -> pd.DataFrame:
    """Add daily % change, a rolling average, and the 2s10s spread."""
    df = df.copy()
    df["us_10y_pct_change"] = df["us_10y"].pct_change() * 100        # daily % change
    df["us_10y_roll3"] = df["us_10y"].rolling(ROLLING_WINDOW).mean()  # 3-day average
    df["spread_2s10s"] = df["us_10y"] - df["us_2y"]                   # calculated column
    return df


def main() -> None:
    df = add_analysis(load_rates(CSV_PATH))

    print("last 5 days of analysis:")
    cols = ["us_2y", "us_10y", "us_10y_pct_change", "us_10y_roll3", "spread_2s10s"]
    print(df[cols].tail().round(3).to_string())

    # Round only here, at the display boundary.
    print(f"\nmean 10y yield:   {df['us_10y'].mean():.3f}")
    print(f"biggest 1-day move: {df['us_10y_pct_change'].abs().max():.3f}%")
    # 2y yields above 10y = an inverted curve; spread is negative throughout here.
    print(f"curve inverted (2y > 10y) every day? {bool((df['spread_2s10s'] < 0).all())}")


if __name__ == "__main__":
    main()
