"""Build compact aggregates from the World Bank Global Financial Development Database.

Reads the raw GFDD workbook (Aug 2022 + Nov 2021 vintages), computes coverage,
time-trend, cross-country, and top-mover aggregates, and writes them to a small
JSON file consumed by the interactive HTML report.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

INPUT_PATH = Path.home() / "Downloads" / "20220909-global-financial-development-database.xlsx"
OUTPUT_PATH = Path(__file__).parent / "gfdd_data.json"

ID_COLS = ["iso3", "iso2", "imfn", "country", "region", "income", "year"]

TREND_START_YEAR = 1990  # first year included in time-trend aggregates
LATEST_WINDOW_START_YEAR = 2015  # years >= this are eligible as a country's "latest" value
EARLY_WINDOW = (2000, 2004)  # inclusive year range averaged for the "before" side of top movers
RECENT_WINDOW = (2017, 2021)  # inclusive year range averaged for the "after" side of top movers
TOP_N_MOVERS = 8  # movers kept per indicator, ranked by |delta|
MIN_GROUP_OBSERVATIONS = 3  # minimum reporting countries for a year's median to be trustworthy
MIN_COMMON_COUNTRIES_FOR_MOVERS = 5  # minimum countries with both early- and recent-window data
ROUND_DECIMALS = 4  # decimal places kept for exported statistical values (not currency)

HEADLINE_CODES = [
    "di14",  # Domestic credit to private sector (% GDP)
    "di01",  # Private credit by deposit money banks to GDP (%)
    "ai05",  # Financial institution account (% age 15+)
    "ai25",  # ATMs per 100,000 adults
    "ai01",  # Bank accounts per 1,000 adults
    "dm01",  # Stock market capitalization to GDP (%)
    "dm02",  # Stock market total value traded to GDP (%)
    "di05",  # Liquid liabilities to GDP (%)
    "ei07",  # Bank return on assets (%)
    "ei01",  # Bank net interest margin (%)
    "oi02",  # Bank Z-score
    "si01",  # Bank nonperforming loans to gross loans (%)
    "si02",  # Bank capital to total assets (%)
    "am01",  # Value traded excluding top 10 traded companies to total value traded (%)
]

TOPIC_NAMES = {
    "ai": "Access", "am": "Access",
    "di": "Depth", "dm": "Depth",
    "ei": "Efficiency", "em": "Efficiency",
    "si": "Stability", "sm": "Stability",
    "oi": "Other", "om": "Other",
}

PILLAR_NAMES = {"i": "Institutions", "m": "Markets"}


def fix_mojibake(series: pd.Series) -> pd.Series:
    """Repair a mis-decoded apostrophe (U+FFFD / smart quote) in metadata text."""
    return series.fillna("").str.replace("�", "'", regex=False).str.replace("’", "'", regex=False).str.strip()


def build_indicator_dict(meta_df: pd.DataFrame) -> dict[str, dict[str, str]]:
    """Map short column codes (e.g. "di14") to indicator metadata.

    "short" codes are how GFDD.DI.14-style Indicator Codes appear as data-sheet
    column headers: topic letters + sub-index, lowercased, dot-free.
    """
    meta = meta_df[meta_df["Indicator Code"].str.startswith("GFDD.", na=False)].copy()
    code_parts = meta["Indicator Code"].str.split(".", expand=True)
    meta["short"] = (code_parts[1] + code_parts[2]).str.lower()
    meta["prefix"] = meta["short"].str.extract(r"^([a-z]+)")[0]
    meta["name"] = fix_mojibake(meta["Indicator Name"])
    meta["definition"] = fix_mojibake(meta["Short Definition"])
    meta["topic"] = meta["prefix"].map(TOPIC_NAMES).fillna("Other")
    meta["pillar"] = meta["prefix"].str[-1].map(PILLAR_NAMES).fillna("Other")

    fields = ["Indicator Code", "name", "definition", "topic", "pillar"]
    records = meta.set_index("short")[fields].rename(columns={"Indicator Code": "code"})
    return records.to_dict(orient="index")


def melt_panel(df: pd.DataFrame, id_cols: list[str]) -> pd.DataFrame:
    """Reshape a wide country-year-by-indicator panel into long (id..., code, value) rows."""
    value_cols = [c for c in df.columns if c not in id_cols]
    long_df = df.melt(id_vars=id_cols, value_vars=value_cols, var_name="code", value_name="value")
    long_df["value"] = pd.to_numeric(long_df["value"], errors="coerce")
    long_df = long_df.dropna(subset=["value"])
    long_df["year"] = pd.to_numeric(long_df["year"], errors="coerce").astype("Int64")
    return long_df


def round_val(x: float | None, ndigits: int = ROUND_DECIMALS) -> float | None:
    """Round a statistical value for JSON export; NaN/None become null, not 0."""
    if x is None or (isinstance(x, float) and np.isnan(x)):
        return None
    return round(float(x), ndigits)


def compute_coverage(long_df: pd.DataFrame, indicators: dict[str, dict]) -> dict[str, dict[str, int]]:
    """Per-indicator reporting footprint: country count, observation count, year span."""
    coverage = {}
    for code, group in long_df.groupby("code"):
        if code not in indicators:
            continue
        coverage[code] = {
            "n_countries": int(group["iso3"].nunique()),
            "n_country_years": int(len(group)),
            "first_year": int(group["year"].min()),
            "last_year": int(group["year"].max()),
        }
    return coverage


def _yearly_stat_series(group: pd.DataFrame, quantiles: bool) -> list[dict[str, Any]]:
    """Median (optionally + IQR) by year, dropping years below MIN_GROUP_OBSERVATIONS."""
    if quantiles:
        agg = group.groupby("year")["value"].agg(
            p50="median", p25=lambda s: s.quantile(0.25), p75=lambda s: s.quantile(0.75), n="count"
        )
    else:
        agg = group.groupby("year")["value"].agg(p50="median", n="count")
    agg = agg[agg["n"] >= MIN_GROUP_OBSERVATIONS]
    records = agg.reset_index().to_dict(orient="records")
    for rec in records:
        rec["year"] = int(rec["year"])
        rec["n"] = int(rec["n"])
        for stat in ("p50", "p25", "p75"):
            if stat in rec:
                rec[stat] = round_val(rec[stat])
    return records


def compute_time_trends(long_df: pd.DataFrame, indicators: dict[str, dict]) -> dict[str, dict[str, Any]]:
    """Median trend since TREND_START_YEAR, globally and split by region / income group."""
    trend_df = long_df[long_df["year"] >= TREND_START_YEAR]
    trends = {}
    for code, sub in trend_df.groupby("code"):
        if code not in indicators:
            continue
        global_series = _yearly_stat_series(sub, quantiles=True)
        if not global_series:
            continue

        by_region = {
            region: series
            for region, rsub in sub.groupby("region")
            if isinstance(region, str) and (series := _yearly_stat_series(rsub, quantiles=False))
        }
        by_income = {
            income: series
            for income, isub in sub.groupby("income")
            if isinstance(income, str) and (series := _yearly_stat_series(isub, quantiles=False))
        }
        trends[code] = {"global": global_series, "by_region": by_region, "by_income": by_income}
    return trends


def compute_latest_values(long_df: pd.DataFrame, indicators: dict[str, dict]) -> dict[str, list[dict[str, Any]]]:
    """Each country's most recent observation (year >= LATEST_WINDOW_START_YEAR) per indicator."""
    window = long_df[long_df["year"] >= LATEST_WINDOW_START_YEAR]
    latest = {}
    for code, sub in window.groupby("code"):
        if code not in indicators or sub.empty:
            continue
        idx = sub.groupby("iso3")["year"].idxmax()
        picked = sub.loc[idx].sort_values("value", ascending=False)
        latest[code] = [
            {
                "iso3": r.iso3, "country": r.country, "region": r.region,
                "income": r.income, "year": int(r.year), "value": round_val(r.value),
            }
            for r in picked.itertuples()
        ]
    return latest


def compute_top_movers(long_df: pd.DataFrame, indicators: dict[str, dict]) -> dict[str, list[dict[str, Any]]]:
    """Largest |change| in each indicator's country average between EARLY_WINDOW and RECENT_WINDOW."""
    early = long_df[long_df["year"].between(*EARLY_WINDOW)]
    recent = long_df[long_df["year"].between(*RECENT_WINDOW)]
    country_names = long_df[["iso3", "country"]].drop_duplicates().set_index("iso3")["country"]

    movers = {}
    for code in indicators:
        early_avg = early[early["code"] == code].groupby("iso3")["value"].mean()
        recent_avg = recent[recent["code"] == code].groupby("iso3")["value"].mean()
        common = early_avg.index.intersection(recent_avg.index)
        if len(common) < MIN_COMMON_COUNTRIES_FOR_MOVERS:
            continue
        delta = (recent_avg.loc[common] - early_avg.loc[common]).dropna()
        if delta.empty:
            continue
        top = delta.reindex(delta.abs().sort_values(ascending=False).index).head(TOP_N_MOVERS)
        movers[code] = [
            {
                "iso3": iso3, "country": country_names.get(iso3, iso3),
                "early": round_val(early_avg.loc[iso3]), "recent": round_val(recent_avg.loc[iso3]),
                "delta": round_val(delta_val),
            }
            for iso3, delta_val in top.items()
        ]
    return movers


def compute_vintage_note(df_2022: pd.DataFrame, df_2021: pd.DataFrame) -> dict[str, Any]:
    """Headline diff between the two release vintages: countries, indicators, filled cells."""
    def indicator_cols(df: pd.DataFrame) -> list:
        return [c for c in df.columns if c not in ID_COLS and c is not None]

    def filled_cells(df: pd.DataFrame) -> int:
        return int(df[indicator_cols(df)].notna().sum().sum())

    return {
        "aug2022_countries": int(df_2022["iso3"].nunique()),
        "aug2022_indicators": len(indicator_cols(df_2022)),
        "aug2022_filled_cells": filled_cells(df_2022),
        "nov2021_countries": int(df_2021["iso3"].nunique()),
        "nov2021_indicators": len(indicator_cols(df_2021)),
        "nov2021_filled_cells": filled_cells(df_2021),
        "new_indicators_2022": ["ai15", "ai16"],
    }


def main() -> None:
    """Build gfdd_data.json from the raw GFDD workbook for the HTML report to consume."""
    print(f"Loading {INPUT_PATH} ...")
    df_2022 = pd.read_excel(INPUT_PATH, sheet_name="Data - August 2022", engine="openpyxl")
    df_2021 = pd.read_excel(INPUT_PATH, sheet_name="Data - November 2021", engine="openpyxl")
    df_2021 = df_2021.loc[:, [c for c in df_2021.columns if c is not None and not str(c).startswith("Unnamed")]]
    meta_df = pd.read_excel(INPUT_PATH, sheet_name="Metadata", engine="openpyxl")

    indicators = build_indicator_dict(meta_df)
    print(f"Indicators: {len(indicators)}")

    long_df = melt_panel(df_2022, ID_COLS)
    long_df = long_df[long_df["region"].notna()]
    print(f"Long-form rows (non-null values): {len(long_df):,}")

    coverage = compute_coverage(long_df, indicators)
    trends = compute_time_trends(long_df, indicators)
    latest = compute_latest_values(long_df, indicators)
    movers = compute_top_movers(long_df, indicators)
    vintage = compute_vintage_note(df_2022, df_2021)

    countries_meta = (
        long_df[["iso3", "country", "region", "income"]]
        .drop_duplicates()
        .sort_values("country")
        .to_dict("records")
    )

    payload = {
        "generated_from": str(INPUT_PATH.name),
        "overview": {
            "n_countries": int(long_df["iso3"].nunique()),
            "n_indicators": len(indicators),
            "year_min": int(long_df["year"].min()),
            "year_max": int(long_df["year"].max()),
            "n_regions": int(long_df["region"].nunique()),
            "n_income_groups": int(long_df["income"].nunique()),
        },
        "vintage": vintage,
        "headline_codes": [c for c in HEADLINE_CODES if c in indicators],
        "indicators": indicators,
        "coverage": coverage,
        "trends": trends,
        "latest": latest,
        "movers": movers,
        "countries": countries_meta,
    }

    OUTPUT_PATH.write_text(json.dumps(payload, allow_nan=False), encoding="utf-8")
    size_kb = OUTPUT_PATH.stat().st_size / 1024
    print(f"Wrote {OUTPUT_PATH} ({size_kb:.0f} KB)")
    print(f"Countries: {payload['overview']['n_countries']}, Indicators: {payload['overview']['n_indicators']}, "
          f"Years: {payload['overview']['year_min']}-{payload['overview']['year_max']}")


if __name__ == "__main__":
    main()
