"""
Lesson 5 — Demo 3 (step 1): pull a year of equity-index prices.

The scenario brief asks how a major index performed "over the past year". We
pull daily prices for the S&P 500 (^GSPC) from the free Yahoo Finance chart
endpoint — no API key, returns JSON — and save a tidy CSV for the analysis step.

Defensive on purpose (see Lesson 3's scraper): the network call is wrapped so a
site hiccup fails loudly with a clear message. If the live pull fails in class,
the committed backup_sp500_1y.csv next to this file is the fallback — that is
the "have a backup data source ready" note from the lesson plan.

Run from the repo root:
    python lessons/lesson-05-equity-analysis-capstone/demos/07-code-live-analysis/fetch_index.py
"""

import csv
import sys
from datetime import datetime, timezone
from pathlib import Path

import requests

SYMBOL = "^GSPC"  # S&P 500 index on Yahoo Finance
# Past ~13 months. Real briefs say "the past year" loosely — we grab a bit extra
# so rolling windows have data to warm up on from day one of the chart.
START = datetime(2025, 7, 1, tzinfo=timezone.utc)
END = datetime(2026, 7, 29, tzinfo=timezone.utc)

CHART_URL = "https://query1.finance.yahoo.com/v8/finance/chart/{symbol}"
# Yahoo returns an empty body to requests with no browser-like User-Agent.
HEADERS = {"User-Agent": "Mozilla/5.0 (QuantFoundations-Lesson5 classroom demo)"}

OUTPUT_CSV = Path(__file__).with_name("index_prices.csv")
COLUMNS = ["date", "open", "high", "low", "close", "volume"]


def fetch_chart(symbol: str, start: datetime, end: datetime) -> dict:
    """Download the raw chart JSON for one symbol, or fail with a clear message."""
    params = {
        "period1": int(start.timestamp()),
        "period2": int(end.timestamp()),
        "interval": "1d",
    }
    try:
        response = requests.get(
            CHART_URL.format(symbol=symbol),
            params=params,
            headers=HEADERS,
            timeout=20,
        )
        response.raise_for_status()  # turn a 404/500 into an error
        return response.json()
    except requests.RequestException as exc:
        sys.exit(
            f"Could not fetch {symbol} from Yahoo Finance: {exc}\n"
            f"Use the committed backup_sp500_1y.csv in this folder instead."
        )


def parse_prices(payload: dict) -> list[dict[str, object]]:
    """Flatten Yahoo's nested chart JSON into one dict per trading day."""
    result = payload["chart"]["result"][0]
    timestamps = result["timestamp"]
    quote = result["indicators"]["quote"][0]

    rows: list[dict[str, object]] = []
    for i, ts in enumerate(timestamps):
        close = quote["close"][i]
        if close is None:  # Yahoo pads non-trading rows with nulls — skip them.
            continue
        day = datetime.fromtimestamp(ts, tz=timezone.utc).strftime("%Y-%m-%d")
        rows.append(
            {
                "date": day,
                # Round only here, at the display/storage boundary — never mid-calc.
                "open": round(quote["open"][i], 2) if quote["open"][i] else "",
                "high": round(quote["high"][i], 2) if quote["high"][i] else "",
                "low": round(quote["low"][i], 2) if quote["low"][i] else "",
                "close": round(close, 2),
                "volume": int(quote["volume"][i]) if quote["volume"][i] else "",
            }
        )
    return rows


def save_csv(rows: list[dict[str, object]], path: Path) -> None:
    """Write the tidy price rows to a CSV for the analysis step."""
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=COLUMNS)
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    payload = fetch_chart(SYMBOL, START, END)
    prices = parse_prices(payload)
    print(f"Pulled {len(prices)} trading days for {SYMBOL}.")
    print(f"  first: {prices[0]['date']}  close {prices[0]['close']}")
    print(f"  last:  {prices[-1]['date']}  close {prices[-1]['close']}")

    save_csv(prices, OUTPUT_CSV)
    print(f"\nSaved to {OUTPUT_CSV.name} — this feeds analyze_index.py.")


if __name__ == "__main__":
    main()
