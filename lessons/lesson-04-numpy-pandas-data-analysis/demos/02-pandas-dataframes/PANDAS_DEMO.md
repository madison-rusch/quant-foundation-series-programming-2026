# Demo 2 — Pandas, Working with Data

Roughly 35 minutes. **This is the core of the lesson — spend the most energy here.** We load the
constituents CSV the class scraped in Lesson 3 and put it through the operations you use on any new
dataset. Build the transformations plan/code/review: prompt Claude, then review each step together.

`load_and_inspect.py` is the artifact. It falls back to the Lesson 3 backup CSV so it runs even if a
student's own scrape failed.

## The one idea

A **DataFrame** is a table: rows, columns, and an index. Think of it as a spreadsheet you drive with
code — or, in FinMath terms, a pricing table or time series.

## 1. Load & inspect (10 min)

```bash
python lessons/lesson-04-numpy-pandas-data-analysis/demos/02-pandas-dataframes/load_and_inspect.py
```

The three commands you run on *any* new DataFrame: `head()`, `.shape`, `.columns`. Expected output
starts:

```
head():
  symbol                 name                  sector  date_added
0    MMM                   3M             Industrials  1957-03-04
1    AOS          A. O. Smith             Industrials  2017-07-26
2    ABT  Abbott Laboratories             Health Care  1957-03-04
...
shape (rows, cols): (503, 4)
```

## 2. Select, filter, missing data, calculated columns (12 min)

| Step | Code | Question to ask the class |
|---|---|---|
| Filter rows | `df[df["sector"] == "Information Technology"]` | What does the inner `df["sector"] == ...` return on its own? (a column of True/False) |
| Missing data | `df["date_added"].isna().sum()` | What are the three honest options for a NaN? (drop, fill, fail) |
| New column | `df["ticker_len"] = df["symbol"].str.len()` | Notice we didn't loop over rows — where's the vectorization? |

## 3. Group & aggregate (13 min)

The payoff. Companies per sector, sorted:

```
companies per sector:
sector
Industrials               81
Financials                76
Information Technology    74
Health Care               59
...
```

| Code | Question to ask the class |
|---|---|
| `df.groupby("sector").size()` | Say this in English: "for each sector, count the rows." |
| `.sort_values(ascending=False)` | Why sort? What question does the sorted view answer at a glance? |

**FinMath framing:** groupby is how you go from a raw list to an answer — "how is the index
distributed across sectors?" is a portfolio-concentration question.

## Talking points

- `head`/`info`/`describe` first, always. You look before you leap on any new dataset.
- A boolean filter is just a column of True/False used as a mask — the same idea as NumPy's
  vectorization from Demo 1.
- Missing data is a *decision*, never a default. Silent NaNs corrupt financial results quietly.
- groupby is the single most useful Pandas verb for analysis — it turns rows into answers.
