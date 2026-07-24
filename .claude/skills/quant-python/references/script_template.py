"""One-line summary of what this script computes.

Conventions:
    - rates: annual, continuously compounded unless noted
    - returns: simple (not log) unless noted
    - money amounts: Decimal; analytics quantities: float64
"""

from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np
import pandas as pd

TRADING_DAYS = 252  # name your periods-per-year factor; never hardcode inline


def load_prices(path: Path) -> pd.DataFrame:
    """Load a price series. Fail loud on missing/NaN rather than filling silently."""
    df = pd.read_parquet(path) if path.suffix == ".parquet" else pd.read_csv(
        path, parse_dates=["date"], index_col="date"
    )
    if df.isna().any().any():
        raise ValueError(f"NaNs present in {path}; decide drop/fill explicitly")
    return df.sort_index()


def annualized_vol(returns: np.ndarray, periods_per_year: int = TRADING_DAYS) -> float:
    """Annualized volatility of simple returns. Vol scales with sqrt(periods)."""
    return float(np.std(returns, ddof=1) * np.sqrt(periods_per_year))


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("prices", type=Path, help="Parquet/CSV price file")
    args = parser.parse_args()

    prices = load_prices(args.prices)
    returns = prices.pct_change().dropna().to_numpy()
    print(f"annualized vol: {annualized_vol(returns):.4%}")


if __name__ == "__main__":
    main()
