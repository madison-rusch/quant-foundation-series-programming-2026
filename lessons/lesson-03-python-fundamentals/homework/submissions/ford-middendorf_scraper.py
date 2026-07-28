"""
Lesson 3 — Demo 2: scrape a financially relevant public table with BeautifulSoup.

Target: the Wikipedia "List of S&P 500 companies" page, whose holdings table
is stable and well-formed — a reliable classroom target. We pull each company's
ticker, name, GICS sector, and date added, then save to CSV for Lesson 4.

This is deliberately defensive: the network call and the parse are each wrapped
so a site hiccup fails loudly with a clear message instead of a stack trace.
Run from the repo root:

    python lessons/lesson-03-python-fundamentals/demos/02-scraping-beautifulsoup/scrape_rates.py
"""

import csv
import sys
from pathlib import Path

import requests
from bs4 import BeautifulSoup

URL = "https://companiesmarketcap.com/ishares-russell-2000-etf/holdings/"
OUTPUT_CSV = Path(__file__).with_name("ford-middendorf_data.csv")
# Wikipedia blocks requests without a descriptive User-Agent.
HEADERS = {"User-Agent": "QuantFoundations-Lesson3/1.0 (classroom demo)"}


def fetch_html(url: str) -> str:
    """Download the page HTML, or fail with a clear message."""
    try:
        response = requests.get(url, headers=HEADERS, timeout=10)
        response.raise_for_status()             # turn a 404/500 into an error
        return response.text
    except requests.RequestException as exc:
        sys.exit(f"Could not fetch {url}: {exc}\nUse the backup CSV in homework/scripts/ instead.")


def parse_holdings(html: str) -> list[dict[str, str]]:
    """Extract one dict per company from the holdings table."""
    soup = BeautifulSoup(html, "lxml")
    table = soup.find("table")
    if table is None:
        sys.exit("holdings table not found — the page layout may have changed.")

    
    rows: list[dict[str, str]] = []
    # Skip the header row (index 0); each remaining row is one company.
    for tr in table.select("tbody tr"):
        cells = tr.find_all("td")
        if len(cells) < 4:                      # guard against malformed rows
            continue
        rows.append(
            {
                "weight_percent": cells[0].get_text(" ", strip = True),
                "name": cells[1].get_text(strip=True),
                "ticker": cells[2].get_text(strip=True),
                "shares_held": cells[3].get_text(strip=True)
            }
        )
    if not rows:
        sys.exit(
            "The table was found, but no holdings were parsed."
        )

    return rows

    return rows


def save_csv(rows: list[dict[str, str]], path: Path) -> None:
    """Write the scraped rows to a CSV for Lesson 4."""

    fields = ["weight_percent", "name", "ticker", "shares_held"]
    try: 
        with path.open("w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=["weight_percent", "name", "ticker", "shares_held"])
            writer.writeheader()
            writer.writerows(rows)
    except PermissionError: 
        sys.exit(f"Could not write to {path}\nThe file may be open in Excel or you may not have permission.")
    


        


def main() -> None:
    html = fetch_html(URL)
    companies = parse_holdings(html)
    print(f"Scraped {len(companies)} companies.")
    print("First 5:")
    for company in companies[:5]:
        print(" ", company["ticker"], "-", company["name"], "-", company["weight_percent"], ": ", company["shares_held"])

    save_csv(companies, OUTPUT_CSV)
    print(f"\nSaved to {OUTPUT_CSV.name} — this feeds Lesson 4.")


if __name__ == "__main__":
    main()
