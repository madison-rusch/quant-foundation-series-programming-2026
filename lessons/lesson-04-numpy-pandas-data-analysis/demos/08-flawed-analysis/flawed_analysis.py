"""
Lesson 4 — Demo 8: analysis that runs cleanly and reaches the wrong conclusion.

Demo 6 covered bugs that crash or silently corrupt a *value* (float ==, NaN,
chained assignment). This demo is different on purpose: every line of code
here is correct Pandas/NumPy, nothing raises, nothing prints NaN. The bug is
in the REASONING — a plausible-sounding conclusion that the full data
contradicts. This is the failure mode Review has to catch when AI writes an
analysis that "looks done" because it runs and produces a tidy number.

Each function prints the FLAWED take first — exactly what a rushed read of
the output would report to a stakeholder — then the fuller picture, then
names the bias. Nothing here crashes; there's nothing to catch.

Run from the repo root:
    python lessons/lesson-04-numpy-pandas-data-analysis/demos/08-flawed-analysis/flawed_analysis.py
"""

from pathlib import Path

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


def pitfall_1_cherry_picked_window() -> None:
    """A short recent window can point the opposite direction of the full series."""
    print("--- 1. Cherry-picked window ---")
    df = pd.read_csv(RATES_CSV, parse_dates=["date"]).set_index("date")

    # The flawed take: eyeball the last 3 trading days only.
    recent = df["us_10y"].tail(3)
    move = recent.iloc[-1] - recent.iloc[0]
    print(f"last 3 days: {recent.iloc[0]} -> {recent.iloc[-1]}  ({move:+.2f})")
    print("FLAWED CONCLUSION: '10y yield is trending down, expect further declines.'\n")

    # The fuller picture: the same series over its full bundled range.
    full_move = df["us_10y"].iloc[-1] - df["us_10y"].iloc[0]
    peak_date = df["us_10y"].idxmax()
    print(f"full range:  {df['us_10y'].iloc[0]} -> {df['us_10y'].iloc[-1]}  ({full_move:+.2f})")
    print(f"peak was {df['us_10y'].max()} on {peak_date.date()}")
    print("FULLER PICTURE: yields rose into that peak, and the last 3 days are just")
    print("easing back off it - a pullback inside a range, not a new downtrend.\n")


def pitfall_2_lookahead_bias() -> None:
    """A centered rolling average uses tomorrow's price to judge today's signal."""
    print("--- 2. Look-ahead bias in a rolling signal ---")
    df = pd.read_csv(RATES_CSV, parse_dates=["date"]).set_index("date")

    # The flawed take: a "smoothed trend" built with center=True, used as a signal.
    df["smoothed_centered"] = df["us_10y"].rolling(3, center=True).mean()
    signal_centered = df["us_10y"] < df["smoothed_centered"]
    print(f"centered-average signal fires 'below trend' on {int(signal_centered.sum())} days")
    print("FLAWED CONCLUSION: 'this rule looks strong in the backtest, ship it.'\n")

    # The fuller picture: center=True at row i averages rows i-1, i, i+1 — it needs
    # TOMORROW's yield to label TODAY. That value doesn't exist yet in live trading.
    trailing = df["us_10y"].rolling(3).mean()
    signal_trailing = df["us_10y"] < trailing
    disagree = signal_centered != signal_trailing
    example = df.index[disagree][0]
    print(f"trailing-average signal (only past+today) fires on {int(signal_trailing.sum())} days")
    print(f"the two signals disagree on {int(disagree.sum())} of the 15 days")
    print(f"e.g. on {example.date()}, us_10y={df.loc[example, 'us_10y']}: the centered average "
          f"{df.loc[example, 'smoothed_centered']:.3f} needed the NEXT row's yield to compute")
    print("FULLER PICTURE: center=True is fine for a retrospective chart, but as a")
    print("trading signal it peeks at data that wasn't available yet - the backtest")
    print("numbers are inflated by information the strategy could never have had.\n")


def pitfall_3_survivorship_bias() -> None:
    """A list of current index members says nothing about firms that dropped out."""
    print("--- 3. Survivorship bias in the constituents list ---")
    df = pd.read_csv(CONSTITUENTS_CSV, parse_dates=["date_added"])

    # The flawed take: only current, still-listed members are in this file.
    early = df[df["date_added"].dt.year < 1980]
    print(f"{len(early)} of today's {len(df)} constituents were added before 1980")
    print("FLAWED CONCLUSION: 'companies added to the index before 1980 have a great "
          "long-run track record - buy old-guard names and hold.'\n")

    # The fuller picture: this file only lists SURVIVORS - companies still in the
    # index today. Everything added before 1980 that was later delisted, acquired,
    # or went bankrupt (Enron, Lehman, dozens of others) is simply absent from it.
    print("FULLER PICTURE: this dataset has no row for a company once it leaves the")
    print("index, so there's no way to compute how many pre-1980 additions failed -")
    print(f"the denominator for a 'success rate' isn't in the data at all. The {len(early)} rows")
    print("above are the ones that happened to survive; nothing here measures the ones")
    print("that didn't.\n")


def main() -> None:
    pitfall_1_cherry_picked_window()
    pitfall_2_lookahead_bias()
    pitfall_3_survivorship_bias()


if __name__ == "__main__":
    main()
