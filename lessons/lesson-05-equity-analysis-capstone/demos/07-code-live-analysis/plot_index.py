"""
Lesson 5 — Demo 3 (step 3): the "clean chart she can drop into a presentation".

Two stacked panels that answer the brief at a glance:
    top    — the index close with its 50-day trend line overlaid
    bottom — running drawdown, shaded, so volatile drops are obvious

Reuses the analysis from analyze_index.py rather than re-deriving it — one source
of truth for the numbers, whether we print them or plot them. Saves to PNG using
the headless Agg backend so it runs in class without a blocking window.

Run from the repo root:
    python lessons/lesson-05-equity-analysis-capstone/demos/07-code-live-analysis/plot_index.py
"""

from pathlib import Path

import matplotlib

matplotlib.use("Agg")  # headless: save to file, don't open a blocking window
import matplotlib.pyplot as plt

from analyze_index import (
    TREND_WINDOW,
    add_analysis,
    load_prices,
    resolve_data_path,
)

OUTPUT_PNG = Path(__file__).with_name("index_analysis.png")


def build_figure(df) -> plt.Figure:
    """Draw the two-panel index chart and return the figure."""
    fig, (ax_price, ax_dd) = plt.subplots(
        2, 1, figsize=(11, 7), sharex=True, height_ratios=[3, 1]
    )

    # Top panel: price + trend.
    ax_price.plot(df.index, df["close"], color="#1f4e79", linewidth=1.3, label="S&P 500 close")
    ax_price.plot(
        df.index,
        df["trend"],
        color="#c55a11",
        linewidth=1.6,
        linestyle="--",
        label=f"{TREND_WINDOW}-day trend",
    )
    ax_price.set_ylabel("Index level")
    ax_price.set_title("S&P 500 — past year: level, trend, and drawdown")
    ax_price.legend(loc="upper left")
    ax_price.grid(True, alpha=0.3)

    # Bottom panel: drawdown, shaded to make the volatile dips pop.
    ax_dd.fill_between(df.index, df["drawdown"] * 100, 0, color="#c00000", alpha=0.3)
    ax_dd.plot(df.index, df["drawdown"] * 100, color="#c00000", linewidth=1.0)
    ax_dd.set_ylabel("Drawdown (%)")
    ax_dd.set_xlabel("Date")
    ax_dd.grid(True, alpha=0.3)

    fig.tight_layout()
    return fig


def main() -> None:
    df = add_analysis(load_prices(resolve_data_path()))
    fig = build_figure(df)
    fig.savefig(OUTPUT_PNG, dpi=150)
    print(f"Saved chart to {OUTPUT_PNG.name}")


if __name__ == "__main__":
    main()
