"""
Lesson 4 — Demo 7: useful Pandas methods worth knowing.

Demos 2–3 covered the core verbs (filter, groupby, pct_change, rolling). This is
a grab-bag of methods that show up constantly in real analysis but didn't fit
earlier. Each is short, vectorized, and framed on financial data so the class
sees *why* you'd reach for it — not just that it exists.

Uses the bundled Treasury-yield series and the Lesson 3 constituents CSV, both
of which run standalone. Run from the repo root:
    python lessons/lesson-04-numpy-pandas-data-analysis/demos/07-useful-methods/useful_methods.py
"""

from pathlib import Path

import numpy as np
import pandas as pd

RATES_CSV = (
    Path(__file__).resolve().parents[1]
    / "02-pandas-dataframes"
    / "sample_rates.csv"
)
CONSTITUENTS_CSV = (
    Path(__file__).resolve().parents[3]
    / "lesson-03-python-fundamentals"
    / "homework"
    / "scripts"
    / "backup_sp500.csv"
)


def describe_and_value_counts() -> None:
    """describe() summarizes numbers; value_counts() summarizes categories."""
    print("--- describe() and value_counts() ---")
    df = pd.read_csv(CONSTITUENTS_CSV)
    # One-line statistical summary of every numeric column.
    ticker_len = df["symbol"].str.len()
    print("ticker length summary:")
    print(ticker_len.describe().round(2).to_string(), "\n")
    # Frequency table for a categorical column — the fastest way to see a mix.
    print("top 5 sectors by company count:")
    print(df["sector"].value_counts().head().to_string(), "\n")


def shift_diff_cumulative() -> None:
    """shift/diff look backward in time; cumprod compounds returns."""
    print("--- shift(), diff(), and cumulative returns ---")
    df = pd.read_csv(RATES_CSV, parse_dates=["date"]).set_index("date")
    df["us_2y"] = df["us_2y"].ffill()          # handle the one gap first

    # shift(1) is 'yesterday's value' — the building block of any period-over-period calc.
    yesterday = df["us_10y"].shift(1)
    df["abs_change_bps"] = (df["us_10y"] - yesterday) * 100   # daily move in basis points

    # Cumulative product turns a return series into a growth curve.
    simple_returns = df["us_10y"].pct_change()
    df["growth_index"] = (1 + simple_returns).cumprod()       # 1.0 = starting level

    print(df[["us_10y", "abs_change_bps", "growth_index"]].tail().round(4).to_string(), "\n")


def np_where_and_clip() -> None:
    """np.where is a vectorized if/else; clip caps outliers."""
    print("--- np.where() and clip() ---")
    df = pd.read_csv(RATES_CSV, parse_dates=["date"]).set_index("date")
    # Vectorized labelling — no loop, no apply.
    df["regime"] = np.where(df["us_10y"] >= 4.45, "high", "low")
    # clip caps values into a range — useful for winsorizing before stats.
    df["us_10y_capped"] = df["us_10y"].clip(lower=4.40, upper=4.47)
    print(df[["us_10y", "regime", "us_10y_capped"]].head().to_string(), "\n")


def bucket_with_cut() -> None:
    """cut bins a continuous column into labeled ranges."""
    print("--- pd.cut() for bucketing ---")
    df = pd.read_csv(RATES_CSV)
    # Turn a continuous yield into discrete buckets — think credit tiers or ratings.
    df["bucket"] = pd.cut(
        df["us_10y"],
        bins=[4.30, 4.40, 4.45, 4.50],
        labels=["low", "mid", "high"],
    )
    print(df[["us_10y", "bucket"]].head(8).to_string(index=False))
    print("\ncount per bucket:")
    print(df["bucket"].value_counts().sort_index().to_string(), "\n")


def dt_accessor_and_resample() -> None:
    """The .dt accessor unpacks dates; resample regroups a time series by period."""
    print("--- .dt accessor and resample() ---")
    df = pd.read_csv(RATES_CSV, parse_dates=["date"]).set_index("date")
    # .dt pulls calendar parts out of a datetime column/index — great for grouping.
    weekly_high = df["us_10y"].resample("W").max()   # highest 10y per calendar week
    print("weekly max 10y yield:")
    print(weekly_high.round(3).to_string(), "\n")
    print("day-of-week of each observation (via index.day_name()):")
    print(df.index.day_name()[:5].tolist(), "\n")


def main() -> None:
    describe_and_value_counts()
    shift_diff_cumulative()
    np_where_and_clip()
    bucket_with_cut()
    dt_accessor_and_resample()


if __name__ == "__main__":
    main()
