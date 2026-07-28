"""
Lesson 3 — Demo 2: scrape a financially relevant public table with BeautifulSoup.

Target: the Wikipedia "List of S&P 500 companies" page, whose constituents table
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

URL = "https://home.treasury.gov/resource-center/data-chart-center/interest-rates/TextView?type=daily_treasury_yield_curve"
# TABLE_ID = "table-container yf-u4m6f0"
OUTPUT_CSV = Path(__file__).with_name("adamesolar_data.csv")
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


def column_key(td) -> str | None:
    """Turn a cell's `headers` attribute into a short, unique column name."""
    headers = td.get("headers")
    if not headers:
        return None
    # BeautifulSoup treats `headers` on <td>/<th> as multi-valued, so this
    # comes back as a list even though each cell references one column.
    if isinstance(headers, list):
        headers = headers[0]
    name = headers.removeprefix("view-field-").removesuffix("-table-column")
    return name.replace("-", "_")


def parse_yield_curve(html: str) -> list[dict[str, str]]:
    """Extract one dict per date from the Treasury daily yield curve table."""
    soup = BeautifulSoup(html, "lxml")

    table = soup.find("table", class_="views-view-table")
    if table is None:
        sys.exit("Yield curve table not found — the page layout may have changed.")

    tbody = table.find("tbody")
    if tbody is None:
        sys.exit("Table has no <tbody> — the page layout may have changed.")

    rows: list[dict[str, str]] = []
    for tr in tbody.find_all("tr"):
        cells = tr.find_all("td")
        if not cells:                    # spacer rows carry no data cells
            continue

        row: dict[str, str] = {}
        for td in cells:
            key = column_key(td)
            if key is None:              # cell doesn't identify its column
                continue
            # The date cell wraps a <time datetime="1990-01-02T12:00:00Z">.
            # Prefer that ISO-8601 value over the "01/02/1990" display text.
            time_tag = td.find("time")
            if time_tag is not None and time_tag.has_attr("datetime"):
                row[key] = time_tag["datetime"]
            else:
                row[key] = td.get_text(strip=True)

        if row:
            rows.append(row)

    return rows


def save_csv(rows: list[dict[str, str]], path: Path) -> None:
    """Write the scraped rows to a CSV for Lesson 4."""
    if not rows:
        sys.exit("No rows to write — the scrape returned nothing.")

    # Build the column list from the data itself, in first-seen order.
    # A dict is used rather than a set because sets don't preserve order,
    # and the table's column order is meaningful here (short maturities first).
    fieldnames = list({key: None for row in rows for key in row})

    with path.open("w", newline="", encoding="utf-8") as f:
        # restval="" fills in blanks for any row missing a column, instead
        # of raising. Not every Treasury row reports every maturity.
        writer = csv.DictWriter(f, fieldnames=fieldnames, restval="")
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    html = fetch_html(URL)
    companies = parse_yield_curve(html)
    #print(f"Scraped {len(companies)} companies.")
    #print("First 5:")
    #for company in companies[:5]:
    #    print(" ", company["symbol"], "-", company["name"], "-", company["sector"])

    save_csv(companies, OUTPUT_CSV)
    print(f"\nSaved to {OUTPUT_CSV.name} — this feeds Lesson 4.")


if __name__ == "__main__":
    main()
