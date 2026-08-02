"""
Homework submission: extended scraper by Jake Schulgasser

Plan (brief):
- Extra data point: `year_founded`, found in the constituents table on Wikipedia (assumed to be in cell index 7).
- Approach: copy the in-class scraper, add extraction of the 8th cell per row, attempt to coerce the first
  four characters to an integer year (defensive), and fall back to the raw first-four characters if parsing
  fails so the CSV remains consistently populated.

Notes:
- This file is a standalone submission copy. It writes its output to `jake-schulgasser_data.csv` in
  the same directory. Do not commit or push until you've reviewed the code and the generated CSV.

Follow-up steps (what you'll do next):
1. Review every line below; confirm the try/except is acceptable and that the index 7 is correct.
2. Run the script locally to create `jake-schulgasser_data.csv` and inspect it.
3. If OK, add the two files (this .py and the .csv) to `lessons/.../homework/submissions/` and commit
   following the course template.
"""

from pathlib import Path
import csv
import sys

import requests
from bs4 import BeautifulSoup

# Page and output settings
URL = "https://en.wikipedia.org/wiki/List_of_S%26P_500_companies"
TABLE_ID = "constituents"
OUTPUT_CSV = Path(__file__).with_name("jake-schulgasser_data.csv")
HEADERS = {"User-Agent": "QuantFoundations-Lesson3/1.0 (homework submission)"}


def fetch_html(url: str) -> str:
    try:
        resp = requests.get(url, headers=HEADERS, timeout=10)
        resp.raise_for_status()
        return resp.text
    except requests.RequestException as exc:
        sys.exit(f"Could not fetch {url}: {exc}\nUse the backup CSV in homework/scripts/ instead.")


def parse_constituents(html: str) -> list[dict[str, str]]:
    """Return list of company dicts with an added `year_founded` field.

    Implementation notes:
    - The page's table contains many columns; `year_founded` is expected at index 7 for this homework.
    - We attempt to extract a four-digit year safely. If the text is not numeric (e.g. contains notes,
      ranges, or words), the try/except preserves the first four characters rather than raise an error.
    """
    soup = BeautifulSoup(html, "html.parser")
    table = soup.find("table", id=TABLE_ID)
    if table is None:
        sys.exit("Constituents table not found — the page layout may have changed.")

    rows: list[dict[str, str]] = []
    for tr in table.find_all("tr")[1:]:
        cells = tr.find_all("td")
        if len(cells) < 4:
            continue

        # I added a function to include the year founded for each company
        year_text = cells[7].get_text(strip=True) if len(cells) > 7 else ""
        # I inclued a tr/except statement because some of the cells for "Founded" column include parentheses or added information that is not needed.
        try:
            year_founded = str(int(year_text[:4])) if year_text else ""
        except Exception:
            year_founded = year_text[:4] if year_text else ""

        rows.append(
            {
                "symbol": cells[0].get_text(strip=True),
                "name": cells[1].get_text(strip=True),
                "sector": cells[2].get_text(strip=True),
                "date_added": cells[5].get_text(strip=True) if len(cells) > 5 else "",
                "year_founded": year_founded,
            }
        )
    return rows


def save_csv(rows: list[dict[str, str]], path: Path) -> None:
    fieldnames = ["symbol", "name", "sector", "date_added", "year_founded"]
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    html = fetch_html(URL)
    companies = parse_constituents(html)
    print(f"Scraped {len(companies)} companies.")
    print("First 5:")
    for c in companies[:5]:
        print(" ", c["symbol"], "-", c["name"], "-", c["sector"], "-", c.get("year_founded", ""))

    save_csv(companies, OUTPUT_CSV)
    print(f"Saved to {OUTPUT_CSV.name} — review before committing.")


if __name__ == "__main__":
    main()
