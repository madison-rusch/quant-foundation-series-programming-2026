---
name: financial-dataset-cleaning
description: How to safely load, reconcile, and analyze messy multi-sheet financial/economic datasets (e.g. World Bank GFDD-style workbooks) without silently producing wrong numbers.
---

# Financial Dataset Cleaning

Apply this whenever you're asked to analyze a financial or economic dataset that ships as a
multi-sheet workbook with a separate metadata/definitions sheet, mixed data vintages, or heavy
missingness (e.g. World Bank, IMF, FRED-style downloads).

## Always read the metadata sheet before the data sheet

- Find the sheet that defines what each column code means (units, coverage years, indicator
  name). Never assume a column header is self-explanatory just because it looks like one.
- If the metadata sheet's indicator codes don't match the data sheet's column headers exactly
  (different casing, punctuation, or prefixing), say so explicitly and show the mapping you used
  — don't silently guess a match.

## Don't blend data vintages without checking column parity first

- If a workbook has more than one "Data" tab (e.g. two years of a release, or a revision),
  compare column counts and headers between them before combining. A mismatch means the
  indicator set changed between releases, not that one tab has "extra" columns to drop.

## Blank is not zero

- A missing cell in a wide (country × year × indicator) dataset almost always means "not
  reported for this country/year," not "value is zero." Never fill blanks with 0 without saying
  so and justifying it — it will silently distort any average or sum.

## Respect each indicator's actual coverage window

- Coverage varies per indicator (e.g. some report every year from 2004–2021, others only report
  specific survey years like 2011, 2014, 2017, 2021). Check the metadata's coverage field before
  computing a trend — a "declining trend" across mostly-missing years may just be reflecting
  which years happened to have data.

## Always report a code and a full name together

- When presenting results, cite both the raw column code (e.g. `ai02`) and its full metadata
  name (e.g. "Bank branches per 100,000 adults") — a table of bare codes is not reviewable by
  anyone who doesn't already have the metadata sheet memorized.

## State your row/column counts before and after cleaning

- Report how many rows/columns you started with and how many survived each cleaning step
  (dropped for missing key fields, dropped duplicate country/year combinations, etc.). A silent
  drop from 13,269 rows to 4,000 rows is the kind of thing a reviewer needs to see, not discover.
