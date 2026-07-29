"""
Lesson 4 — Demo 2: load the Lesson 3 scraped CSV into a DataFrame and work with it.

A DataFrame is a table: rows, columns, and an index. This is the core of the
lesson. We load the S&P 500 constituents the class scraped in Lesson 3, inspect
it, select and filter, then group and aggregate by sector.

Falls back to the Lesson 3 backup CSV so this runs even without the students'
own scrape. Run from the repo root:
    python lessons/lesson-04-numpy-pandas-data-analysis/demos/02-pandas-dataframes/load_and_inspect.py
"""

from pathlib import Path

import pandas as pd

# The Lesson 3 backup CSV of S&P 500 constituents (symbol, name, sector, date_added).
CSV_PATH = (
    Path(__file__).resolve().parents[3]
    / "lesson-03-python-fundamentals"
    / "homework"
    / "scripts"
    / "backup_sp500.csv"
)


def load_constituents(path: Path) -> pd.DataFrame:
    """Read the scraped constituents CSV into a DataFrame."""
    return pd.read_csv(path)


def main() -> None:
    df = load_constituents(CSV_PATH)

    # --- inspect: the three commands you run on any new DataFrame --------
    print("head():")
    print(df.head())
    print("\nshape (rows, cols):", df.shape)
    print("\ncolumns:", list(df.columns))

    # --- select a column, filter rows -----------------------------------
    tech = df[df["sector"] == "Information Technology"]   # boolean filter
    print(f"\nInformation Technology names ({len(tech)}):")
    print(tech["name"].head().to_string(index=False))

    # --- handle missing data explicitly ---------------------------------
    missing = df["date_added"].isna().sum()
    print(f"\nrows missing a date_added: {missing}")

    # --- add a calculated column ----------------------------------------
    df["ticker_len"] = df["symbol"].str.len()             # length of each ticker
    print("\nlongest tickers:")
    print(df.nlargest(3, "ticker_len")[["symbol", "name", "ticker_len"]].to_string(index=False))

    # --- group and aggregate: companies per sector ----------------------
    by_sector = df.groupby("sector").size().sort_values(ascending=False)
    print("\ncompanies per sector:")
    print(by_sector.to_string())


if __name__ == "__main__":
    main()
