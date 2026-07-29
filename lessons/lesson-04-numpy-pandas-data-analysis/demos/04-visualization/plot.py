"""
Lesson 4 — Demo 4: visualize the analyzed time series with matplotlib.

Just enough matplotlib to produce one clear chart: the 2y and 10y yields over
time, with the 3-day rolling average of the 10y. Saves to PNG so it runs
headless in class (no blocking window).

Run from the repo root:
    python lessons/lesson-04-numpy-pandas-data-analysis/demos/04-visualization/plot.py
"""

from pathlib import Path

import matplotlib

matplotlib.use("Agg")  # headless backend — save to file, don't open a window
import matplotlib.pyplot as plt

# Reuse the analysis functions rather than re-deriving them here.
import sys

sys.path.append(str(Path(__file__).resolve().parents[1] / "03-analysis"))
from analyze import add_analysis, load_rates, CSV_PATH  # noqa: E402

OUTPUT_PNG = Path(__file__).with_name("yields.png")


def main() -> None:
    df = add_analysis(load_rates(CSV_PATH))

    fig, ax = plt.subplots(figsize=(9, 5))
    ax.plot(df.index, df["us_2y"], marker="o", label="2Y yield")
    ax.plot(df.index, df["us_10y"], marker="o", label="10Y yield")
    ax.plot(df.index, df["us_10y_roll3"], linestyle="--", label="10Y 3-day avg")

    ax.set_title("US Treasury Yields — 2Y vs 10Y")
    ax.set_xlabel("Date")
    ax.set_ylabel("Yield (%)")
    ax.legend()
    fig.autofmt_xdate()
    fig.tight_layout()

    fig.savefig(OUTPUT_PNG, dpi=120)
    print(f"Saved chart to {OUTPUT_PNG.name}")


if __name__ == "__main__":
    main()
