"""
Lesson 4 — Demo 2b: numeric analysis of the sample yield data with Pandas.

`load_and_inspect.py` works the S&P 500 constituents CSV (categorical data — select,
filter, groupby). Here we turn the same DataFrame tools on `sample_rates.csv`, a small
Treasury-yield time series, and ask purely numeric questions: what do these columns
look like on average, how tightly do the two tenors move together, and how volatile
is the 10y day to day?

This is broader than `../03-analysis/analyze.py`, which computes daily % change, a
rolling *average*, and the 2s10s spread — this file adds descriptive statistics,
correlation, and rolling *volatility* instead of repeating that work.

Run from the repo root:
    python lessons/lesson-04-numpy-pandas-data-analysis/demos/02-pandas-dataframes/numeric_analysis.py
"""

from pathlib import Path

import pandas as pd

ROLLING_WINDOW = 3  # trading days

CSV_PATH = Path(__file__).resolve().parent / "sample_rates.csv"


def load_rates(path: Path) -> pd.DataFrame:
    """Load the yield time series, parse dates, and fill the one missing value."""
    df = pd.read_csv(path, parse_dates=["date"]).set_index("date")
    # Explicit missing-data decision: carry the last observation forward.
    df["us_2y"] = df["us_2y"].ffill()
    return df


def describe_rates(df: pd.DataFrame) -> pd.DataFrame:
    """Descriptive stats (count, mean, std, min, quartiles, max) per column."""
    return df.describe()


def correlation(df: pd.DataFrame) -> pd.DataFrame:
    """How tightly the two tenors move together."""
    return df[["us_2y", "us_10y"]].corr()


def add_volatility(df: pd.DataFrame) -> pd.DataFrame:
    """Add rolling volatility (std of daily levels) for the 10y."""
    df = df.copy()
    df["us_10y_roll_vol"] = df["us_10y"].rolling(ROLLING_WINDOW).std()
    return df


def main() -> None:
    df = load_rates(CSV_PATH)

    print("describe():")
    print(describe_rates(df).round(3))

    print("\ncorrelation (us_2y vs us_10y):")
    print(correlation(df).round(3))

    df = add_volatility(df)
    print(f"\n{ROLLING_WINDOW}-day rolling volatility of us_10y (last 5 days):")
    print(df["us_10y_roll_vol"].tail().round(4).to_string())

    # Round only here, at the display boundary.
    cumulative_change = df["us_10y"].iloc[-1] - df["us_10y"].iloc[0]
    print(f"\ncumulative us_10y change (first to last obs): {cumulative_change:.3f}")

    min_date, max_date = df["us_10y"].idxmin(), df["us_10y"].idxmax()
    print(f"lowest us_10y:  {df['us_10y'].min():.3f} on {min_date.date()}")
    print(f"highest us_10y: {df['us_10y'].max():.3f} on {max_date.date()}")


if __name__ == "__main__":
    main()
