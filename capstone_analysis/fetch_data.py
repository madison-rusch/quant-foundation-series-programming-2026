"""Fetch 1y daily OHLCV for the S&P 500 and peer indices from Yahoo Finance.

Writes one CSV per symbol to data/, plus data/manifest.json recording
provenance (fetch time, row counts, observed date range). Skips symbols
that already have a cached CSV unless --refresh is passed.
"""
import argparse
import csv
import datetime as dt
import json
import os
import time
import urllib.error
import urllib.request

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/120 Safari/537.36"
    )
}

SYMBOLS = {
    "GSPC": ("%5EGSPC", "S&P 500", "primary"),
    "NDX": ("%5ENDX", "Nasdaq 100", "peer"),
    "DJI": ("%5EDJI", "Dow Jones Industrial Average", "peer"),
    "RUT": ("%5ERUT", "Russell 2000", "peer"),
    "VIX": ("%5EVIX", "CBOE Volatility Index", "reference"),
}

DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")


def fetch_symbol(query_symbol, attempts=3):
    url = (
        f"https://query1.finance.yahoo.com/v8/finance/chart/{query_symbol}"
        "?range=1y&interval=1d"
    )
    last_err = None
    for i in range(attempts):
        try:
            req = urllib.request.Request(url, headers=HEADERS)
            with urllib.request.urlopen(req, timeout=30) as resp:
                return json.loads(resp.read().decode())
        except (urllib.error.URLError, urllib.error.HTTPError, TimeoutError) as e:
            last_err = e
            time.sleep(1.5 * (i + 1))
    raise RuntimeError(f"failed to fetch {query_symbol} after {attempts} attempts: {last_err}")


def parse_result(payload, label):
    result = payload.get("chart", {}).get("result")
    if not result:
        err = payload.get("chart", {}).get("error")
        raise RuntimeError(f"no result for {label}: {err}")
    r = result[0]
    timestamps = r["timestamp"]
    quote = r["indicators"]["quote"][0]
    adjclose = r["indicators"].get("adjclose", [{}])[0].get("adjclose")

    rows = []
    for i, ts in enumerate(timestamps):
        close = quote["close"][i]
        if close is None:
            continue
        date = dt.datetime.fromtimestamp(ts, dt.timezone.utc).date().isoformat()
        rows.append({
            "date": date,
            "open": quote["open"][i],
            "high": quote["high"][i],
            "low": quote["low"][i],
            "close": close,
            "adjclose": adjclose[i] if adjclose else close,
            "volume": quote["volume"][i],
        })
    if not rows:
        raise RuntimeError(f"zero usable rows for {label}")
    return rows


def write_csv(path, rows):
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["date", "open", "high", "low", "close", "adjclose", "volume"])
        w.writeheader()
        w.writerows(rows)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--refresh", action="store_true", help="refetch even if cached CSV exists")
    args = ap.parse_args()

    os.makedirs(DATA_DIR, exist_ok=True)
    manifest = {"fetched_at_utc": dt.datetime.now(dt.timezone.utc).isoformat(), "symbols": {}}

    for key, (query_symbol, label, role) in SYMBOLS.items():
        csv_path = os.path.join(DATA_DIR, f"{key}.csv")
        if os.path.exists(csv_path) and not args.refresh:
            with open(csv_path, newline="", encoding="utf-8") as f:
                rows = list(csv.DictReader(f))
            print(f"[cache] {key:5s} {label:32s} {len(rows)} rows (use --refresh to refetch)")
        else:
            payload = fetch_symbol(query_symbol)
            rows = parse_result(payload, label)
            write_csv(csv_path, rows)
            print(f"[fetch] {key:5s} {label:32s} {len(rows)} rows  {rows[0]['date']} -> {rows[-1]['date']}")

        manifest["symbols"][key] = {
            "label": label,
            "role": role,
            "query_symbol": query_symbol,
            "rows": len(rows),
            "date_range": [rows[0]["date"], rows[-1]["date"]],
        }

    with open(os.path.join(DATA_DIR, "manifest.json"), "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2)
    print(f"\nmanifest written to {os.path.join(DATA_DIR, 'manifest.json')}")


if __name__ == "__main__":
    main()
