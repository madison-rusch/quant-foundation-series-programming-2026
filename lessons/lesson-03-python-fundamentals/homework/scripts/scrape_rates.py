"""
Lesson 3 — Demo 2: scrape a financially relevant public table with BeautifulSoup.

Target: the Wikipedia "List of S&P 500 companies" page, whose constituents table
is stable and well-formed — a reliable classroom target. We pull each company's
ticker, name, GICS sector, date added, and CIK, then save to CSV for Lesson 4.

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

URL = "https://en.wikipedia.org/wiki/List_of_S%26P_500_companies"
TABLE_ID = "constituents"                       # the id Wikipedia gives the main table
OUTPUT_CSV = Path(__file__).with_name("scraped_data.csv")
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


def parse_constituents(html: str) -> list[dict[str, str]]:
    """Extract one dict per company from the constituents table."""
    soup = BeautifulSoup(html, "lxml")
    table = soup.find("table", id=TABLE_ID)
    if table is None:
        sys.exit("Constituents table not found — the page layout may have changed.")

    rows: list[dict[str, str]] = []
    # Skip the header row (index 0); each remaining row is one company.
    for tr in table.find_all("tr")[1:]:
        cells = tr.find_all("td")
        if len(cells) < 4:                      # guard against malformed rows
            continue
        row = {
            "symbol": cells[0].get_text(strip=True),
            "name": cells[1].get_text(strip=True),
            "sector": cells[2].get_text(strip=True),
            "date_added": cells[5].get_text(strip=True) if len(cells) > 5 else "",
            "cik": cells[6].get_text(strip=True) if len(cells) > 6 else "",
        }
        if row["symbol"] and row["name"]:
            rows.append(row)
    return rows


def save_csv(rows: list[dict[str, str]], path: Path) -> None:
    """Write the scraped rows to a CSV for Lesson 4."""
    clean_rows = [row for row in rows if any(value.strip() for value in row.values())]
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["symbol", "name", "sector", "date_added", "cik"])
        writer.writeheader()
        writer.writerows(clean_rows)


def main() -> None:
    html = fetch_html(URL)
    companies = parse_constituents(html)
    print(f"Scraped {len(companies)} companies.")
    print("First 5:")
    for company in companies[:5]:
        print(" ", company["symbol"], "-", company["name"], "-", company["sector"])

    save_csv(companies, OUTPUT_CSV)
    print(f"\nSaved to {OUTPUT_CSV.name} — this feeds Lesson 4.")


if __name__ == "__main__":
    main()
