"""Compute trend, drawdown, volatility, cross-index, rates, and cross-asset
metrics for the S&P 500, peer indices, and US Treasury yields from the
cached CSVs in data/, and write the result to data/metrics.json.

All figures reported downstream (report.py) must trace back to a key in
this JSON — nothing is hardcoded in the report template.

Two windows are reported, and they must never be conflated:
  * the equity window (251 days) drives every equity metric;
  * the rates window (248 days) drives yield metrics, with a paired
    subset (245 obs) for stock/bond statistics.
Each section carries its own window dict so a consumer cannot mix them.
"""
import argparse
import hashlib
import json
import math
import os

import numpy as np
import pandas as pd

# Schema convention: minor bump = additive only, no existing key changed
# value or meaning. Enforced in practice by `--baseline`.
SCHEMA_VERSION = "1.1"
TRADING_DAYS = 252
RISK_FREE_ANNUAL = 0.0
JB_CRITICAL_5PCT = 5.991  # chi-square(2), 5% significance

DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")
EQUITY_SYMBOLS = ["GSPC", "NDX", "DJI", "RUT"]
ALL_SYMBOLS = EQUITY_SYMBOLS + ["VIX"]

TENORS = ["DGS5", "DGS10", "DGS30"]
TENOR_LABELS = {
    "DGS5": "5-year Treasury",
    "DGS10": "10-year Treasury",
    "DGS30": "30-year Treasury",
}
# (key, long leg, short leg) — stored in basis points throughout.
SPREADS = [("s10_5", "DGS10", "DGS5"), ("s30_10", "DGS30", "DGS10"), ("s30_5", "DGS30", "DGS5")]
SPREAD_LABELS = {"s10_5": "10y − 5y", "s30_10": "30y − 10y", "s30_5": "30y − 5y"}
ROLLING_CORR_WINDOW = 63
BIG_MOVE_BP = 10.0
# First-order price sensitivity only; the assumption travels with the number.
ASSUMED_DURATION_YEARS = {"DGS5": 4.5, "DGS10": 8.3, "DGS30": 16.5}
YIELD_MIN_PCT, YIELD_MAX_PCT = 1.0, 25.0  # sanity band: catches percent-vs-fraction inversion

LABELS = {
    "GSPC": "S&P 500",
    "NDX": "Nasdaq 100",
    "DJI": "Dow Jones Industrial Average",
    "RUT": "Russell 2000",
    "VIX": "CBOE Volatility Index",
}
LABELS.update(TENOR_LABELS)


# ---------------------------------------------------------------- loading --

def load_prices(data_dir):
    frames = {}
    for sym in ALL_SYMBOLS:
        path = os.path.join(data_dir, f"{sym}.csv")
        df = pd.read_csv(path, parse_dates=["date"])
        df = df.sort_values("date").drop_duplicates("date", keep="last")
        df = df.set_index("date")
        frames[sym] = df
    with open(os.path.join(data_dir, "manifest.json"), encoding="utf-8") as f:
        manifest = json.load(f)
    return frames, manifest


def align(frames):
    equity_idx = frames["GSPC"].index
    for sym in EQUITY_SYMBOLS[1:]:
        equity_idx = equity_idx.intersection(frames[sym].index)
    common_idx = equity_idx.intersection(frames["VIX"].index)
    common_idx = common_idx.sort_values()

    dropped = {}
    for sym in ALL_SYMBOLS:
        extra = frames[sym].index.difference(common_idx)
        if len(extra):
            dropped[sym] = sorted(d.date().isoformat() for d in extra)

    aligned = {sym: frames[sym].loc[common_idx].copy() for sym in ALL_SYMBOLS}

    window = {
        "start": common_idx.min().date().isoformat(),
        "end": common_idx.max().date().isoformat(),
        "trading_days": len(common_idx),
        "return_obs": len(common_idx) - 1,
        "dropped_dates": dropped,
    }
    return aligned, window


def build_returns(frames):
    close = pd.DataFrame({sym: frames[sym]["adjclose"] for sym in ALL_SYMBOLS})
    log_ret = np.log(close).diff().dropna(how="any")
    simple_ret = close.pct_change().dropna(how="any")
    return close, log_ret, simple_ret


def load_yields(data_dir):
    """Read the FRED constant-maturity par yield CSVs.

    Schema differs from the Yahoo files: `observation_date,<SERIES_ID>`.
    FRED writes "." for a missing observation via its API and an empty
    field in a manual download, so both are treated as NaN.
    """
    cols, provenance = {}, {}
    for tenor in TENORS:
        path = os.path.join(data_dir, f"{tenor}.csv")
        df = pd.read_csv(path, parse_dates=["observation_date"], na_values=[".", "", " "])
        df = df.rename(columns={"observation_date": "date"})
        df = df.sort_values("date").drop_duplicates("date", keep="last").set_index("date")
        series = pd.to_numeric(df[tenor], errors="coerce")
        cols[tenor] = series

        with open(path, "rb") as f:
            digest = hashlib.sha256(f.read()).hexdigest()
        provenance[tenor] = {
            "file": os.path.basename(path),
            "sha256": digest,
            "rows": int(len(series)),
            "raw_date_range": [series.index.min().date().isoformat(),
                               series.index.max().date().isoformat()],
            "blank_dates": [d.date().isoformat() for d in series[series.isna()].index],
        }
    return pd.DataFrame(cols), provenance


def align_rates(yields, eq_index, eq_window):
    """Project yields onto the equity calendar, then drop incomplete days.

    Reindexing onto `eq_index` *before* differencing is what makes the
    paired sample correct: the session after a bond-only holiday gets a
    NaN predecessor, so its yield change (which would otherwise span two
    equity sessions) drops out on its own rather than by a hardcoded date
    list. Nothing is ever forward-filled — a bond-market closure is a real
    absence, and filling it would manufacture zero-change days that bias
    yield volatility down and drag correlations toward zero.
    """
    on_eq = yields.reindex(eq_index)
    complete = on_eq.dropna(how="any")
    any_data = on_eq.dropna(how="all")

    raw_index = yields.index
    missing_rows = [d for d in eq_index if d not in raw_index]
    blank_rows = [d for d in eq_index if d in raw_index and d not in complete.index]

    window = {
        "id": "rates",
        "start": complete.index.min().date().isoformat(),
        "end": complete.index.max().date().isoformat(),
        "trading_days": len(complete),
        "equity_days_without_yield_row": [d.date().isoformat() for d in missing_rows],
        "equity_days_with_blank_yield": [d.date().isoformat() for d in blank_rows],
        "vs_equity_window": {
            "equity_trading_days": eq_window["trading_days"],
            "shortfall": eq_window["trading_days"] - len(complete),
        },
    }
    return complete, any_data, window


def yield_changes_bp(yields, eq_index):
    """Daily yield changes in basis points on the equity calendar.

    Straddle observations (the session after a bond-only closure) become
    NaN here by construction and are dropped, keeping one equity session
    as the unit of observation on both legs.
    """
    return (yields.reindex(eq_index).diff() * 100.0).dropna(how="any")


# ------------------------------------------------------------- indicators --

def annualized_vol(log_ret, periods=TRADING_DAYS):
    return float(log_ret.std(ddof=1) * math.sqrt(periods))


def rolling_annualized_vol(log_ret, window, periods=TRADING_DAYS):
    return log_ret.rolling(window).std(ddof=1) * math.sqrt(periods)


def cagr(close):
    n_days = (close.index[-1] - close.index[0]).days
    if n_days <= 0:
        return float("nan")
    total = close.iloc[-1] / close.iloc[0]
    return float(total ** (365.25 / n_days) - 1)


def sma(close, window):
    return close.rolling(window).mean()


def drawdown_series(close):
    running_max = close.cummax()
    return close / running_max - 1.0


def drawdown_episodes(close, threshold=0.03):
    dd = drawdown_series(close)
    running_max = close.cummax()
    episodes = []
    in_dd = False
    peak_date = peak_val = trough_date = trough_val = None
    for date, (c, m, d) in zip(close.index, zip(close, running_max, dd)):
        if c >= m:
            # at a new high: close out any open episode first
            if in_dd:
                depth = trough_val / peak_val - 1.0
                if abs(depth) >= threshold:
                    episodes.append({
                        "peak_date": peak_date.date().isoformat(),
                        "trough_date": trough_date.date().isoformat(),
                        "recovery_date": date.date().isoformat(),
                        "depth": round(depth, 4),
                        "days_to_trough": int((trough_date - peak_date).days),
                        "days_to_recover": int((date - trough_date).days),
                        "status": "recovered",
                    })
                in_dd = False
            peak_date, peak_val = date, c
            trough_date, trough_val = date, c
        else:
            in_dd = True
            if c < trough_val:
                trough_date, trough_val = date, c
    if in_dd:
        depth = trough_val / peak_val - 1.0
        if abs(depth) >= threshold:
            episodes.append({
                "peak_date": peak_date.date().isoformat(),
                "trough_date": trough_date.date().isoformat(),
                "recovery_date": None,
                "depth": round(depth, 4),
                "days_to_trough": int((trough_date - peak_date).days),
                "days_to_recover": None,
                "status": "ongoing",
            })
    return episodes


def streaks(simple_ret):
    sign = np.sign(simple_ret.values)
    best_up = cur_up = best_down = cur_down = 0
    up_days = down_days = 0
    up_end = down_end = None
    dates = simple_ret.index
    for i, s in enumerate(sign):
        if s > 0:
            cur_up += 1
            cur_down = 0
            up_days += 1
            if cur_up > best_up:
                best_up = cur_up
                up_end = dates[i]
        elif s < 0:
            cur_down += 1
            cur_up = 0
            down_days += 1
            if cur_down > best_down:
                best_down = cur_down
                down_end = dates[i]
        else:
            cur_up = cur_down = 0
    return {
        "up_days": int(up_days),
        "down_days": int(down_days),
        "flat_days": int(len(sign) - up_days - down_days),
        "longest_up_streak": int(best_up),
        "longest_up_streak_end": up_end.date().isoformat() if up_end is not None else None,
        "longest_down_streak": int(best_down),
        "longest_down_streak_end": down_end.date().isoformat() if down_end is not None else None,
    }


def monthly_returns(close):
    df = close.to_frame("close")
    df["month"] = df.index.to_period("M")
    rows = []
    months = df["month"].unique()
    prev_last_close = None
    for m in months:
        sub = df[df["month"] == m]
        n_days = len(sub)
        expected_days = m.days_in_month
        is_partial = n_days < _trading_days_in_month_estimate(expected_days)
        if prev_last_close is None:
            prev_last_close = sub["close"].iloc[-1]
            continue
        month_ret = sub["close"].iloc[-1] / prev_last_close - 1.0
        rows.append({
            "month": str(m),
            "return": round(float(month_ret), 4),
            "n_days": int(n_days),
            "partial": bool(is_partial),
        })
        prev_last_close = sub["close"].iloc[-1]
    return rows


def _trading_days_in_month_estimate(calendar_days):
    # ~69.4% of calendar days are trading days on a typical US calendar month
    return max(1, round(calendar_days * 0.60))


def moments(x):
    n = len(x)
    mean = float(np.mean(x))
    std = float(np.std(x, ddof=1))
    if std == 0 or n < 4:
        return {"n": n, "mean": mean, "std": std, "skew": 0.0, "kurtosis_excess": 0.0,
                "jarque_bera": 0.0, "jb_critical_5pct": JB_CRITICAL_5PCT, "normal_at_5pct": True}
    g1 = float(np.mean(((x - mean) / std) ** 3))
    g2 = float(np.mean(((x - mean) / std) ** 4) - 3.0)
    G1 = math.sqrt(n * (n - 1)) / (n - 2) * g1
    G2 = ((n + 1) * g2 + 6) * (n - 1) / ((n - 2) * (n - 3))
    jb = n / 6.0 * (G1 ** 2 + (G2 ** 2) / 4.0)
    return {
        "n": n, "mean": mean, "std": std,
        "skew": round(G1, 4), "kurtosis_excess": round(G2, 4),
        "jarque_bera": round(float(jb), 4),
        "jb_critical_5pct": JB_CRITICAL_5PCT,
        "normal_at_5pct": bool(jb <= JB_CRITICAL_5PCT),
    }


def histogram(x, bins=40):
    counts, edges = np.histogram(x, bins=bins)
    mean, std = float(np.mean(x)), float(np.std(x, ddof=1))
    centers = (edges[:-1] + edges[1:]) / 2
    bin_width = edges[1] - edges[0]
    n = len(x)
    normal_density = (1.0 / (std * math.sqrt(2 * math.pi))) * np.exp(-0.5 * ((centers - mean) / std) ** 2)
    normal_counts = normal_density * bin_width * n
    return {
        "edges": [round(float(e), 6) for e in edges],
        "counts": [int(c) for c in counts],
        "normal_overlay": [round(float(c), 3) for c in normal_counts],
    }


def tail_counts(x):
    n = len(x)
    std = float(np.std(x, ddof=1))
    abs_x = np.abs(x)
    gauss_2sig = 2 * (1 - _norm_cdf(2)) * n
    gauss_3sig = 2 * (1 - _norm_cdf(3)) * n
    return {
        "pct_over_1pct": round(float((abs_x > 0.01).mean() * 100), 2),
        "pct_over_2pct": round(float((abs_x > 0.02).mean() * 100), 2),
        "count_2sigma": int((abs_x > 2 * std).sum()),
        "count_2sigma_gaussian_expected": round(float(gauss_2sig), 2),
        "count_3sigma": int((abs_x > 3 * std).sum()),
        "count_3sigma_gaussian_expected": round(float(gauss_3sig), 2),
    }


def _norm_cdf(z):
    return 0.5 * (1 + math.erf(z / math.sqrt(2)))


def atr_percent(high, low, close, window=14):
    prev_close = close.shift(1)
    tr = pd.concat([
        high - low,
        (high - prev_close).abs(),
        (low - prev_close).abs(),
    ], axis=1).max(axis=1)
    atr = tr.ewm(alpha=1 / window, adjust=False, min_periods=window).mean()
    return atr / close * 100


def downside_deviation(simple_ret, mar=0.0, periods=TRADING_DAYS):
    downside = np.minimum(simple_ret - mar, 0.0)
    return float(np.sqrt(np.mean(downside ** 2)) * math.sqrt(periods))


def sharpe(simple_ret, rf_annual=RISK_FREE_ANNUAL, periods=TRADING_DAYS):
    mean_ann = float(simple_ret.mean()) * periods
    vol_ann = float(simple_ret.std(ddof=1)) * math.sqrt(periods)
    if vol_ann == 0:
        return float("nan")
    return (mean_ann - rf_annual) / vol_ann


def sortino(simple_ret, rf_annual=RISK_FREE_ANNUAL, mar=0.0, periods=TRADING_DAYS):
    mean_ann = float(simple_ret.mean()) * periods
    dd_ann = downside_deviation(simple_ret, mar=mar, periods=periods)
    if dd_ann == 0:
        return float("nan")
    return (mean_ann - rf_annual) / dd_ann


def beta_r2(peer_log_ret, base_log_ret):
    cov = float(np.cov(peer_log_ret, base_log_ret, ddof=1)[0, 1])
    var_base = float(np.var(base_log_ret, ddof=1))
    beta = cov / var_base
    corr = float(np.corrcoef(peer_log_ret, base_log_ret)[0, 1])
    return beta, corr ** 2


def regime_counts(vix, edges, labels):
    counts = {}
    for lo, hi, label in zip(edges[:-1], edges[1:], labels):
        counts[label] = int(((vix >= lo) & (vix < hi)).sum())
    return counts


# --------------------------------------------------------------- sections --

def trend_section(frames, close, simple_ret, window):
    gspc = close["GSPC"]
    rebased = (close / close.iloc[0] * 100.0)

    sma50 = sma(gspc, 50)
    sma200 = sma(gspc, 200)
    sma200_first_valid = sma200.first_valid_index()

    running_high = gspc.cummax()
    running_low = gspc.cummin()
    high_52w = float(gspc.max())
    high_52w_date = gspc.idxmax().date().isoformat()
    low_52w = float(gspc.min())
    low_52w_date = gspc.idxmin().date().isoformat()

    best = simple_ret["GSPC"].nlargest(5)
    worst = simple_ret["GSPC"].nsmallest(5)

    scoreboard = {}
    for sym in EQUITY_SYMBOLS:
        c = close[sym]
        r = simple_ret[sym]
        scoreboard[sym] = {
            "label": LABELS[sym],
            "total_return": round(float(c.iloc[-1] / c.iloc[0] - 1.0), 4),
            "cagr": round(cagr(c), 4),
        }

    return {
        "rebased": {sym: [round(float(v), 4) for v in rebased[sym]] for sym in EQUITY_SYMBOLS},
        "dates": [d.date().isoformat() for d in close.index],
        "gspc_close": [round(float(v), 4) for v in gspc],
        "sma50": [None if pd.isna(v) else round(float(v), 4) for v in sma50],
        "sma200": [None if pd.isna(v) else round(float(v), 4) for v in sma200],
        "sma200_first_valid_date": sma200_first_valid.date().isoformat() if sma200_first_valid is not None else None,
        "pct_days_above_sma50": round(float((gspc > sma50).sum() / sma50.notna().sum() * 100), 1),
        "pct_days_above_sma200": round(float((gspc > sma200).sum() / sma200.notna().sum() * 100), 1),
        "n_days_sma50": int(sma50.notna().sum()),
        "n_days_sma200": int(sma200.notna().sum()),
        "high_52w": round(high_52w, 2),
        "high_52w_date": high_52w_date,
        "low_52w": round(low_52w, 2),
        "low_52w_date": low_52w_date,
        "pct_from_52w_high": round(float(gspc.iloc[-1] / high_52w - 1.0) * 100, 2),
        "pct_from_52w_low": round(float(gspc.iloc[-1] / low_52w - 1.0) * 100, 2),
        "monthly_returns": monthly_returns(gspc),
        "best_days": [{"date": d.date().isoformat(), "return": round(float(v), 4)} for d, v in best.items()],
        "worst_days": [{"date": d.date().isoformat(), "return": round(float(v), 4)} for d, v in worst.items()],
        "streaks": streaks(simple_ret["GSPC"]),
        "scoreboard": scoreboard,
    }


def drawdown_section(close):
    gspc = close["GSPC"]
    dd = drawdown_series(gspc)
    trough_idx = dd.idxmin()
    max_dd = float(dd.min())
    peak_val = gspc.loc[:trough_idx].max()
    peak_date = gspc.loc[:trough_idx].idxmax()

    recovery_date = None
    after = gspc.loc[trough_idx:].iloc[1:]  # strictly after the trough
    recovered = after[after >= peak_val]
    if len(recovered):
        recovery_date = recovered.index[0].date().isoformat()

    episodes = drawdown_episodes(gspc, threshold=0.03)
    days_underwater = int((dd < -0.001).sum())

    return {
        "series": [round(float(v), 4) for v in dd],
        "max_drawdown": round(max_dd, 4),
        "peak_date": peak_date.date().isoformat(),
        "trough_date": trough_idx.date().isoformat(),
        "recovery_date": recovery_date,
        "current_drawdown": round(float(dd.iloc[-1]), 4),
        "days_underwater": days_underwater,
        "episodes": episodes,
    }


def volatility_section(frames, close, log_ret, simple_ret):
    gspc_log = log_ret["GSPC"]
    gspc_simple = simple_ret["GSPC"]
    vix = close["VIX"].loc[log_ret.index]

    rv21 = rolling_annualized_vol(gspc_log, 21) * 100
    rv63 = rolling_annualized_vol(gspc_log, 63) * 100
    vix_spread = vix - rv21

    hist = histogram(gspc_log.values, bins=40)
    mom = moments(gspc_log.values)
    tails = tail_counts(gspc_log.values)

    gspc_df = frames["GSPC"]
    atr_pct = atr_percent(gspc_df["high"], gspc_df["low"], gspc_df["adjclose"])

    regime_labels = ["low (<15)", "moderate (15-20)", "elevated (20-30)", "high (>30)"]
    regime_edges = [0, 15, 20, 30, 1000]

    return {
        "ann_vol_full": round(annualized_vol(gspc_log) * 100, 2),
        "rolling_vol_21d": [None if pd.isna(v) else round(float(v), 3) for v in rv21],
        "rolling_vol_63d": [None if pd.isna(v) else round(float(v), 3) for v in rv63],
        "vix_minus_trailing_rv21": [None if pd.isna(v) else round(float(v), 3) for v in vix_spread],
        "vix_minus_trailing_rv21_avg": round(float(vix_spread.dropna().mean()), 3),
        "vix_min": round(float(vix.min()), 2),
        "vix_max": round(float(vix.max()), 2),
        "vix_max_date": vix.idxmax().date().isoformat(),
        "vix_mean": round(float(vix.mean()), 2),
        "vix_current": round(float(vix.iloc[-1]), 2),
        "vix_regime_days": regime_counts(vix, regime_edges, regime_labels),
        "downside_deviation": round(downside_deviation(gspc_simple) * 100, 2),
        "histogram": hist,
        "moments": mom,
        "tail_counts": tails,
        "atr_pct_current": round(float(atr_pct.dropna().iloc[-1]), 3) if atr_pct.notna().any() else None,
        "atr_pct_series_n": int(atr_pct.notna().sum()),
    }


def cross_index_section(log_ret, simple_ret):
    corr = log_ret.corr()
    corr_matrix = {a: {b: round(float(corr.loc[a, b]), 3) for b in ALL_SYMBOLS} for a in ALL_SYMBOLS}

    betas = {}
    for sym in EQUITY_SYMBOLS[1:]:
        b, r2 = beta_r2(log_ret[sym].values, log_ret["GSPC"].values)
        betas[sym] = {"beta": round(b, 3), "r_squared": round(r2, 3)}

    scoreboard = {}
    for sym in EQUITY_SYMBOLS:
        r = simple_ret[sym]
        scoreboard[sym] = {
            "sharpe": round(sharpe(r), 3),
            "sortino": round(sortino(r), 3),
            "ann_vol": round(annualized_vol(log_ret[sym]) * 100, 2),
            "best_day": round(float(r.max()), 4),
            "worst_day": round(float(r.min()), 4),
            "corr_to_gspc": round(float(corr.loc[sym, "GSPC"]), 3),
        }

    return {
        "correlation_matrix": corr_matrix,
        "beta_r2_vs_gspc": betas,
        "scoreboard": scoreboard,
        "risk_free_annual": RISK_FREE_ANNUAL,
    }


def rates_section(rates, changes, window, provenance):
    dates = [d.date().isoformat() for d in rates.index]
    # Stated here, not in align_rates: the usable change count is the paired
    # sample (245), which is smaller than trading_days-1 because straddle
    # sessions drop out. Reporting the naive difference would overstate it.
    window = dict(window, change_obs=int(len(changes)))

    level_summary = {}
    for tenor in TENORS:
        s = rates[tenor]
        level_summary[tenor] = {
            "label": TENOR_LABELS[tenor],
            "start": round(float(s.iloc[0]), 2),
            "end": round(float(s.iloc[-1]), 2),
            "change_bp": round(float(s.iloc[-1] - s.iloc[0]) * 100, 1),
            "min": round(float(s.min()), 2),
            "min_date": s.idxmin().date().isoformat(),
            "max": round(float(s.max()), 2),
            "max_date": s.idxmax().date().isoformat(),
            "mean": round(float(s.mean()), 2),
        }

    spreads, spread_summary = {}, {}
    for key, long_leg, short_leg in SPREADS:
        sp = (rates[long_leg] - rates[short_leg]) * 100.0  # basis points
        spreads[key] = [round(float(v), 1) for v in sp]
        spread_summary[key] = {
            "label": SPREAD_LABELS[key],
            "start_bp": round(float(sp.iloc[0]), 1),
            "end_bp": round(float(sp.iloc[-1]), 1),
            "change_bp": round(float(sp.iloc[-1] - sp.iloc[0]), 1),
            "min_bp": round(float(sp.min()), 1),
            "min_date": sp.idxmin().date().isoformat(),
            "max_bp": round(float(sp.max()), 1),
            "max_date": sp.idxmax().date().isoformat(),
            "days_inverted": int((sp < 0).sum()),
            "ever_inverted": bool((sp < 0).any()),
        }

    change_stats = {}
    for tenor in TENORS:
        d = changes[tenor]
        change_stats[tenor] = {
            "label": TENOR_LABELS[tenor],
            "n": int(len(d)),
            "mean_bp": round(float(d.mean()), 2),
            "sd_bp": round(float(d.std(ddof=1)), 2),
            "annualized_vol_bp": round(float(d.std(ddof=1) * math.sqrt(TRADING_DAYS)), 1),
            "max_up_bp": round(float(d.max()), 1),
            "max_up_date": d.idxmax().date().isoformat(),
            "max_down_bp": round(float(d.min()), 1),
            "max_down_date": d.idxmin().date().isoformat(),
            "days_over_10bp": int((d.abs() >= BIG_MOVE_BP).sum()),
        }

    ch_corr = changes.corr()
    change_corr = {a: {b: round(float(ch_corr.loc[a, b]), 3) for b in TENORS} for a in TENORS}

    # Curve classification, derived from signs rather than asserted.
    long_chg = level_summary["DGS30"]["change_bp"]
    spread_chg = spread_summary["s10_5"]["change_bp"]
    front_chg = level_summary["DGS5"]["change_bp"]
    curve_narrative = {
        "direction": "bear" if long_chg > 0 else "bull",
        "shape": "flattener" if spread_chg < 0 else "steepener",
        "front_led": bool(abs(front_chg) > abs(long_chg)),
        "front_change_bp": front_chg,
        "long_change_bp": long_chg,
        "spread_change_bp": spread_chg,
    }

    duration_proxy = {}
    for tenor in TENORS:
        d_years = ASSUMED_DURATION_YEARS.get(tenor)
        chg_bp = level_summary[tenor]["change_bp"]
        duration_proxy[tenor] = {
            "assumed_modified_duration_years": d_years,
            "approx_price_return_pct": (
                None if d_years is None else round(-d_years * chg_bp / 100.0, 2)
            ),
            "basis": (
                "First-order (-D x change in yield) only. Ignores convexity, coupon carry, and "
                "roll-down, and is not the return of any bond index."
            ),
        }

    return {
        "window": window,
        "dates": dates,
        "levels": {t: [round(float(v), 2) for v in rates[t]] for t in TENORS},
        "level_summary": level_summary,
        "spreads_bp": spreads,
        "spread_summary": spread_summary,
        "change_dates": [d.date().isoformat() for d in changes.index],
        "changes_bp": {t: [round(float(v), 2) for v in changes[t]] for t in TENORS},
        "change_stats": change_stats,
        "change_corr": change_corr,
        "curve_narrative": curve_narrative,
        "duration_proxy": duration_proxy,
        "histogram_d10": histogram(changes["DGS10"].values, bins=30),
        "provenance": {
            "source": (
                "FRED (Federal Reserve Bank of St. Louis), H.15 Treasury constant-maturity "
                "par yields"
            ),
            "acquired_by": (
                "Manually downloaded by the analyst; not fetched by fetch_data.py, so no "
                "manifest.json entry exists for these series."
            ),
            "units": "percent per annum, constant-maturity (par) yield",
            "not_a_total_return": (
                "These are yields, not the total return of holding a bond."
            ),
            "series": provenance,
        },
    }


def cross_asset_section(log_ret, changes, eq_close):
    """Stock/bond statistics on the paired sample.

    Both legs are first differences: equity log returns against yield
    changes in basis points. Level-vs-level correlation would be
    spurious, so no level series reaches this function.
    """
    paired = log_ret.index.intersection(changes.index)
    eq = log_ret.loc[paired]
    dy = changes.loc[paired]

    corr_matrix = {}
    for sym in ALL_SYMBOLS:
        corr_matrix[sym] = {t: round(float(eq[sym].corr(dy[t])), 3) for t in TENORS}

    sensitivity = {}
    for sym in ALL_SYMBOLS:
        # Equity return in percent regressed on the 10y change in bp.
        beta, r2 = beta_r2((eq[sym] * 100).values, dy["DGS10"].values)
        sensitivity[sym] = {
            "label": LABELS[sym],
            "beta_pct_per_10bp": round(float(beta) * 10, 3),
            "r_squared": round(float(r2), 3),
            "n": int(len(paired)),
        }

    roll = eq["GSPC"].rolling(ROLLING_CORR_WINDOW).corr(dy["DGS10"])
    roll_valid = roll.dropna()
    rolling_corr = {
        "window": ROLLING_CORR_WINDOW,
        "dates": [d.date().isoformat() for d in roll.index],
        "values": [None if pd.isna(v) else round(float(v), 3) for v in roll],
        "min": round(float(roll_valid.min()), 3),
        "min_date": roll_valid.idxmin().date().isoformat(),
        "max": round(float(roll_valid.max()), 3),
        "max_date": roll_valid.idxmax().date().isoformat(),
        "current": round(float(roll_valid.iloc[-1]), 3),
        "mean": round(float(roll_valid.mean()), 3),
        "pct_days_positive": round(float((roll_valid > 0).mean() * 100), 1),
        "n_valid": int(len(roll_valid)),
        "first_valid_date": roll_valid.index[0].date().isoformat(),
    }

    d10 = dy["DGS10"]
    buckets = {
        "rate_up": d10 > 0,
        "rate_down": d10 < 0,
        "rate_flat": d10 == 0,
        "big_move": d10.abs() >= BIG_MOVE_BP,
    }
    conditional = {}
    for sym in ALL_SYMBOLS:
        r = eq[sym]
        conditional[sym] = {}
        for name, mask in buckets.items():
            sel = r[mask]
            conditional[sym][name] = {
                "n": int(len(sel)),
                "mean_return_bp": None if not len(sel) else round(float(sel.mean()) * 10000, 1),
                "hit_rate_pct": None if not len(sel) else round(float((sel > 0).mean() * 100), 1),
            }

    return {
        "window": {
            "id": "cross_asset",
            "parent_window": "rates",
            "start": paired.min().date().isoformat(),
            "end": paired.max().date().isoformat(),
            "paired_obs": int(len(paired)),
            "note": (
                "Sessions following a bond-market-only closure are excluded automatically: "
                "their yield change would span two equity sessions, so one leg would not "
                "match the other's unit of observation."
            ),
        },
        "correlation_matrix": corr_matrix,
        "sensitivity": sensitivity,
        "rolling_corr": rolling_corr,
        "conditional": conditional,
        "bucket_labels": {
            "rate_up": "10y yield rose",
            "rate_down": "10y yield fell",
            "rate_flat": "10y yield unchanged",
            "big_move": f"|10y move| >= {BIG_MOVE_BP:.0f}bp",
        },
    }


def data_quality_section(frames, manifest, window, rate_window=None):
    checks = {}
    for sym in ALL_SYMBOLS:
        df = frames[sym]
        checks[sym] = {
            "adjclose_equals_close": bool((df["close"] == df["adjclose"]).all()),
            "zero_volume_days": int((df["volume"] == 0).sum()),
        }
    out = {
        "dropped_dates": window["dropped_dates"],
        "checks": checks,
        "fetched_at_utc": manifest.get("fetched_at_utc"),
        "volume_note": (
            "Volume excluded from analysis: RUT's reported volume is ~99% identical to "
            "GSPC's (a Yahoo composite-index artifact, not true constituent volume), "
            "VIX carries zero volume on every day, and the final GSPC session's volume "
            "is provisional/unconsolidated."
        ),
    }
    if rate_window is not None:
        no_row = rate_window["equity_days_without_yield_row"]
        blank = rate_window["equity_days_with_blank_yield"]
        out["rates_provenance_note"] = (
            "Treasury yields were supplied manually from FRED and are not covered by "
            "manifest.json; per-file SHA-256 hashes are recorded under rates.provenance. "
            f"They cover {rate_window['trading_days']} of the "
            f"{rate_window['vs_equity_window']['equity_trading_days']} equity sessions: "
            f"{len(no_row)} session(s) have no published yield ({', '.join(no_row) or 'none'}) "
            f"and {len(blank)} fall on bond-market closures when equities traded "
            f"({', '.join(blank) or 'none'}). Equity metrics are unaffected — they use their "
            "own window."
        )
    return out


# ------------------------------------------------------------------ main --

def jsonable(obj):
    if isinstance(obj, dict):
        return {k: jsonable(v) for k, v in obj.items()}
    if isinstance(obj, (list, tuple)):
        return [jsonable(v) for v in obj]
    if isinstance(obj, (np.floating, float)):
        v = float(obj)
        if math.isnan(v) or math.isinf(v):
            return None
        return v
    if isinstance(obj, (np.integer,)):
        return int(obj)
    if isinstance(obj, np.bool_):
        return bool(obj)
    return obj


def run_checks(frames, window, close, rates=None, any_data=None, rate_window=None, changes=None):
    errors = []
    lens = {sym: len(frames[sym].loc[frames[sym].index.intersection(close.index)]) for sym in EQUITY_SYMBOLS}
    if len(set(lens.values())) != 1:
        errors.append(f"equity indices do not align identically post-alignment: {lens}")
    if window["trading_days"] < 240:
        errors.append(f"aligned window too short: {window['trading_days']} days")
    if close.isna().any().any():
        errors.append("NaNs present in aligned close prices")

    if rates is not None:
        # Containment: rates must never widen or shift the equity window.
        if not rates.index.isin(close.index).all():
            errors.append("rate index is not a subset of the equity index")
        # Units: catches percent-vs-fraction inversion (4.37 vs 0.0437).
        lo, hi = float(rates.min().min()), float(rates.max().max())
        if not (YIELD_MIN_PCT < lo and hi < YIELD_MAX_PCT):
            errors.append(f"yields outside sane band [{YIELD_MIN_PCT}, {YIELD_MAX_PCT}]: min {lo}, max {hi}")
        # No fill: a complete-day frame must equal the any-data frame, proving
        # no tenor was filled in and no partial day survived.
        if rates.isna().any().any():
            errors.append("NaNs present in the aligned rate frame")
        if len(rates) != len(any_data):
            errors.append(
                f"tenors have differing coverage: {len(rates)} complete days vs "
                f"{len(any_data)} days with any data (a single-tenor gap was silently dropped)"
            )
        if not (240 <= rate_window["trading_days"] <= window["trading_days"]):
            errors.append(f"rate window size implausible: {rate_window['trading_days']}")
        if not (rates.index.is_monotonic_increasing and rates.index.is_unique):
            errors.append("rate index is not monotonic and unique")
        # Disclosure completeness: every equity session missing from the rate
        # window must appear in exactly one disclosure list.
        missing = {d.date().isoformat() for d in close.index if d not in rates.index}
        disclosed = set(rate_window["equity_days_without_yield_row"]) | set(
            rate_window["equity_days_with_blank_yield"])
        if missing != disclosed:
            errors.append(f"undisclosed dropped sessions: {sorted(missing ^ disclosed)}")
        if changes is not None and len(changes) > len(rates) - 1:
            errors.append(f"more yield changes ({len(changes)}) than rate days minus one ({len(rates)-1})")

    if errors:
        for e in errors:
            print(f"[CHECK FAILED] {e}")
        raise SystemExit(1)
    print(f"[CHECK OK] {window['trading_days']} trading days, "
          f"{window['start']} -> {window['end']}, no NaNs in aligned closes")
    if rates is not None:
        print(f"[CHECK OK] {rate_window['trading_days']} rate days, {len(changes)} paired obs, "
              f"{rate_window['vs_equity_window']['shortfall']} equity session(s) without complete "
              f"yields (all disclosed)")


EQUITY_FROZEN_KEYS = ["window", "trend", "drawdown", "volatility", "cross_index"]


def _diff_path(a, b, path=""):
    """First differing key path between two JSON-like structures, or None."""
    if type(a) is not type(b) and not (isinstance(a, (int, float)) and isinstance(b, (int, float))):
        return f"{path} (type {type(a).__name__} != {type(b).__name__})"
    if isinstance(a, dict):
        for k in sorted(set(a) | set(b)):
            if k not in a:
                return f"{path}.{k} (missing in baseline)"
            if k not in b:
                return f"{path}.{k} (missing in new)"
            d = _diff_path(a[k], b[k], f"{path}.{k}")
            if d:
                return d
        return None
    if isinstance(a, list):
        if len(a) != len(b):
            return f"{path} (length {len(a)} != {len(b)})"
        for i, (x, y) in enumerate(zip(a, b)):
            d = _diff_path(x, y, f"{path}[{i}]")
            if d:
                return d
        return None
    return None if a == b else f"{path} ({a!r} != {b!r})"


def run_baseline_gate(new_metrics, baseline_path):
    """Assert the equity metrics are byte-identical to a saved baseline.

    This is what proves the rates work was additive: adding a data source
    must never move a previously reported equity figure.
    """
    with open(baseline_path, encoding="utf-8") as f:
        old = json.load(f)
    failures = []
    for key in EQUITY_FROZEN_KEYS:
        if key not in old:
            print(f"[BASELINE SKIP] {key} absent from baseline")
            continue
        d = _diff_path(old[key], new_metrics.get(key), key)
        if d:
            failures.append(d)
    for key, val in old.get("data_quality", {}).items():
        d = _diff_path(val, new_metrics.get("data_quality", {}).get(key), f"data_quality.{key}")
        if d:
            failures.append(d)
    for key, val in old.get("labels", {}).items():
        if new_metrics.get("labels", {}).get(key) != val:
            failures.append(f"labels.{key} changed")
    if failures:
        for f_ in failures:
            print(f"[BASELINE FAILED] {f_}")
        raise SystemExit(1)
    print(f"[BASELINE OK] equity metrics unchanged vs {os.path.basename(baseline_path)} "
          f"({', '.join(EQUITY_FROZEN_KEYS)}, data_quality, labels)")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true", help="run alignment sanity checks and exit nonzero on failure")
    ap.add_argument("--baseline", help="assert equity metrics match a saved metrics.json exactly")
    ap.add_argument("--out", default=os.path.join(DATA_DIR, "metrics.json"))
    args = ap.parse_args()

    frames, manifest = load_prices(DATA_DIR)
    aligned, window = align(frames)
    close = pd.DataFrame({sym: aligned[sym]["adjclose"] for sym in ALL_SYMBOLS})

    yields, provenance = load_yields(DATA_DIR)
    rates, any_data, rate_window = align_rates(yields, close.index, window)
    changes = yield_changes_bp(yields, close.index)

    if args.check:
        run_checks(aligned, window, close, rates, any_data, rate_window, changes)

    _, log_ret, simple_ret = build_returns(aligned)

    metrics = {
        "schema_version": SCHEMA_VERSION,
        "window": window,
        "trend": trend_section(aligned, close[EQUITY_SYMBOLS], simple_ret[EQUITY_SYMBOLS], window),
        "drawdown": drawdown_section(close[EQUITY_SYMBOLS]),
        "volatility": volatility_section(aligned, close, log_ret, simple_ret),
        "cross_index": cross_index_section(log_ret, simple_ret),
        "rates": rates_section(rates, changes, rate_window, provenance),
        "cross_asset": cross_asset_section(log_ret, changes, close),
        "data_quality": data_quality_section(aligned, manifest, window, rate_window),
        "labels": LABELS,
    }

    payload = jsonable(metrics)

    if args.baseline:
        run_baseline_gate(payload, args.baseline)

    with open(args.out, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2, allow_nan=False)

    print(f"metrics written to {args.out}")
    print(f"equity window: {window['start']} -> {window['end']} "
          f"({window['trading_days']} days, {window['return_obs']} return obs)")
    print(f"GSPC total return: {metrics['trend']['scoreboard']['GSPC']['total_return']*100:.2f}%")
    print(f"GSPC ann. vol: {metrics['volatility']['ann_vol_full']:.2f}%")
    print(f"GSPC max drawdown: {metrics['drawdown']['max_drawdown']*100:.2f}% "
          f"(trough {metrics['drawdown']['trough_date']})")

    r, ca = metrics["rates"], metrics["cross_asset"]
    print(f"rates window: {rate_window['start']} -> {rate_window['end']} "
          f"({rate_window['trading_days']} days, {ca['window']['paired_obs']} paired obs)")
    for tenor in TENORS:
        ls = r["level_summary"][tenor]
        print(f"  {tenor:6s} {ls['start']:.2f} -> {ls['end']:.2f} ({ls['change_bp']:+.0f}bp), "
              f"ann. change vol {r['change_stats'][tenor]['annualized_vol_bp']:.0f}bp")
    cn = r["curve_narrative"]
    s105 = r["spread_summary"]["s10_5"]
    print(f"  curve: {cn['direction']} {cn['shape']}, 10y-5y {s105['start_bp']:.0f} -> "
          f"{s105['end_bp']:.0f}bp, ever inverted: {s105['ever_inverted']}")
    print(f"  corr(GSPC, d10y): {ca['correlation_matrix']['GSPC']['DGS10']:+.3f}")


if __name__ == "__main__":
    main()
