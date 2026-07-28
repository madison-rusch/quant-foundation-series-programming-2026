# Demo 2 — Scraping with BeautifulSoup

Roughly 35 minutes. Build a scraper the plan/code/review way: plan what we want, let Claude write
it, then read it line by line as a class. `scrape_rates.py` in this folder is the artifact.

> **Instructor: pre-run this before class.** Sites change. This demo targets a stable Wikipedia
> table, but keep the backup CSV ([../../homework/scripts/backup_sp500.csv](../../homework/scripts/backup_sp500.csv))
> open in case the network or the page misbehaves. A broken live demo is hard to recover from.

## 0. What is web scraping? (5 min)

- Scraping = programmatically reading a web page's HTML and pulling structured data out of it.
- When it's useful for quant work: no API exists, or you want a quick snapshot of a public table
  (rates, yields, index constituents, prices).
- When to be careful: sites change their layout, rate-limit you, or forbid scraping in their terms.
  Always prefer an official API or download when one exists.

Install (already in `requirements.txt` this lesson):

```bash
pip install requests beautifulsoup4 lxml
```

## 1. Plan (say it out loud, write it where the class can see it)

- **What:** pull the S&P 500 constituents from a public Wikipedia table
- **For each company:** ticker symbol, name, GICS sector, date added
- **Output:** a CSV (`scraped_data.csv`) we hand to Lesson 4
- **What can go wrong:** the request fails, the table isn't found, a row is malformed → handle each

Ask the class: *"Why is the last bullet part of the plan?"* — scraping talks to a server we don't
control, so error handling isn't optional polish, it's core to the task.

## 2. Code

Turn the plan into a prompt:

```
Write a Python script that scrapes the S&P 500 constituents table from
https://en.wikipedia.org/wiki/List_of_S%26P_500_companies using requests and BeautifulSoup.
For each company pull ticker, name, GICS sector, and date added. Wrap the network call and the
parse in error handling that fails with a clear message. Save the results to scraped_data.csv.
Include type hints and a __main__ block. Note: Wikipedia needs a descriptive User-Agent header.
```

Let Claude generate it, then paste the result into `scrape_rates.py` (or use the version already
in this folder). Run it:

```bash
python lessons/lesson-03-python-fundamentals/demos/02-scraping-beautifulsoup/scrape_rates.py
```

Expected output (row count varies as the index changes):

```
Scraped 503 companies.
First 5:
  MMM - 3M - Industrials
  AOS - A. O. Smith - Industrials
  ABT - Abbott Laboratories - Health Care
  ABBV - AbbVie - Health Care
  ACN - Accenture - Information Technology

Saved to scraped_data.csv — this feeds Lesson 4.
```

## 3. Review

Read it out loud, line by line — the point is that scraping code is *mostly* about what goes wrong:

| Line / block | Question to ask the class |
|---|---|
| `HEADERS = {"User-Agent": ...}` | Why does Wikipedia reject us without this? |
| `response.raise_for_status()` | What does this do that just calling `.get()` doesn't? |
| `except requests.RequestException` | What kinds of failure does this catch? (timeout, DNS, 500) |
| `soup.find("table", id="constituents")` | How did we know the table's `id`? (browser "Inspect") |
| `if len(cells) < 4: continue` | Why guard the row length instead of trusting every row? |
| `save_csv(...)` | Why save to disk at all, instead of just printing? (Lesson 4) |

Then ask: *"What breaks this script six months from now?"* — Wikipedia could rename the table id,
add a column, or change the page. That fragility is the honest downside of scraping.

## Talking points

- try/except isn't decoration here — the whole reason scraping needs it is that we're reading data
  from a server we don't own. This is the concrete payoff of the fundamentals block.
- The scraped CSV is the input to Lesson 4. Make that arc explicit: **scrape → clean → analyze → visualize.**
- "Read the HTML in the browser's Inspect panel first" is the real-world workflow — you can't scrape
  what you haven't located.
