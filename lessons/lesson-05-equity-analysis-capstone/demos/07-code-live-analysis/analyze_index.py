"""
Lesson 5 — Demo 3 (step 2): analyze the index the brief asked about.

The manager wants three things: the trend, notable volatile periods, and numbers
clean enough for a slide. We compute, all vectorized in pandas:

    * daily simple returns          -> the raw day-to-day moves
    * a rolling mean of the close   -> the trend, with daily noise smoothed out
    * rolling annualized volatility -> where the ride got bumpy
    * running drawdown from the peak -> how far below the high-water mark we sat

These are analytics, not settlement amounts, so float is the right regime here —
we round only at the display boundary in main(), never mid-calculation.

Loads the live pull (index_prices.csv) if fetch_index.py has run, otherwise the
committed backup_sp500_1y.csv — so this step works even if the live pull failed.

Run from the repo root:
    python lessons/lesson-05-equity-analysis-capstone/demos/07-code-live-analysis/analyze_index.py
"""

from pathlib import Path

import numpy as np
import pandas as pd

TRADING_DAYS = 252  # trading days per year — the annualization factor
VOL_WINDOW = 21  # ~one trading month, the rolling volatility window
TREND_WINDOW = 50  # a common medium-term trend window (in trading days)

HERE = Path(__file__).resolve().parent
LIVE_CSV = HERE / "index_prices.csv"  # written by fetch_index.py
BACKUP_CSV = HERE / "backup_sp500_1y.csv"  # committed fallback


def resolve_data_path() -> Path:
    """Prefer the live pull; fall back to the committed backup CSV."""
    if LIVE_CSV.exists():
        return LIVE_CSV
    if BACKUP_CSV.exists():
        return BACKUP_CSV
    raise FileNotFoundError(
        "No data found. Run fetch_index.py first, or keep backup_sp500_1y.csv here."
    )


def load_prices(path: Path) -> pd.DataFrame:
    """Load the price CSV, parse dates, and sort — the close is our series."""
    df = pd.read_csv(path, parse_dates=["date"]).set_index("date").sort_index()
    # No silent NaN: a missing close would poison every downstream calc, so fail.
    if df["close"].isna().any():
        raise ValueError("Missing close prices — clean the source before analyzing.")
    return df


def add_analysis(df: pd.DataFrame) -> pd.DataFrame:
    """Add returns, a trend line, rolling volatility, and drawdown columns."""
    df = df.copy()
    # Simple (not log) daily returns: additive across assets, the everyday choice.
    df["daily_return"] = df["close"].pct_change()
    # Trend: rolling mean of the close smooths daily noise into a direction.
    df["trend"] = df["close"].rolling(TREND_WINDOW).mean()
    # Volatility: rolling std of daily returns, annualized by sqrt(periods).
    df["volatility"] = df["daily_return"].rolling(VOL_WINDOW).std() * np.sqrt(TRADING_DAYS)
    # Drawdown: how far below the running peak the index sits, as a fraction.
    running_peak = df["close"].cummax()
    df["drawdown"] = df["close"] / running_peak - 1
    return df


def summarize(df: pd.DataFrame) -> dict[str, float]:
    """Reduce the analyzed frame to the handful of numbers the brief asks for."""
    first_close = df["close"].iloc[0]
    last_close = df["close"].iloc[-1]
    return {
        "total_return": last_close / first_close - 1,
        "annualized_vol": df["daily_return"].std() * np.sqrt(TRADING_DAYS),
        "best_day": df["daily_return"].max(),
        "worst_day": df["daily_return"].min(),
        "max_drawdown": df["drawdown"].min(),
    }


def main() -> None:
    path = resolve_data_path()
    df = add_analysis(load_prices(path))
    print(f"Loaded {len(df)} trading days from {path.name}")
    print(f"  {df.index[0].date()} -> {df.index[-1].date()}\n")

    print("Last 5 days:")
    cols = ["close", "daily_return", "trend", "volatility", "drawdown"]
    print(df[cols].tail().round(4).to_string())

    stats = summarize(df)
    # Round only here, at the display boundary. Returns/vol shown as percentages.
    print("\nHeadline numbers for the manager:")
    print(f"  total return over window: {stats['total_return']:+.2%}")
    print(f"  annualized volatility:    {stats['annualized_vol']:.2%}")
    print(f"  best single day:          {stats['best_day']:+.2%}")
    print(f"  worst single day:         {stats['worst_day']:+.2%}")
    print(f"  max drawdown:             {stats['max_drawdown']:.2%}")

    # The most volatile month: highest rolling annualized vol, and when it peaked.
    peak_vol_date = df["volatility"].idxmax()
    print(
        f"\nMost volatile stretch peaked around {peak_vol_date.date()} "
        f"({df['volatility'].max():.2%} annualized)."
    )


if __name__ == "__main__":
    main()
