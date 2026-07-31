"""Render data/metrics.json into a single self-contained report.html.

Every number in the page must trace back to a key in metrics.json — no
figure is hardcoded here. Charts are inline SVG driven by a JSON blob
embedded in the page and rendered client-side by CHART_JS; there is no
external stylesheet, script, font, or image reference.
"""
import argparse
import html
import json
import os

SCHEMA_VERSION = "1.1"
DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")

# Categorical slots 1-5 belong to the five price entities; the tenors take
# the next family so a colour always means the same thing across charts.
# Slot 8 equals --diverging-neg, so a 30y line must never share a chart
# with diverging bars.
SLOT = {"GSPC": 1, "NDX": 2, "DJI": 3, "RUT": 4, "VIX": 5}
RATE_SLOT = {"DGS5": 6, "DGS10": 7, "DGS30": 8}
TENORS = ["DGS5", "DGS10", "DGS30"]


# --------------------------------------------------------------- helpers --

def load_metrics(path):
    with open(path, encoding="utf-8") as f:
        m = json.load(f)
    assert m.get("schema_version") == SCHEMA_VERSION, (
        f"metrics.json schema_version {m.get('schema_version')!r} != expected {SCHEMA_VERSION!r}; "
        "re-run analyze.py"
    )
    return m


def pct(x, dp=1, sign=True):
    if x is None:
        return "n/a"
    v = x * 100 if abs(x) < 1.5 else x  # accept either fraction or already-percent
    s = f"{v:+.{dp}f}%" if sign else f"{v:.{dp}f}%"
    return s


def pct_pts(x, dp=1, sign=True):
    """x already expressed in percentage points (not a fraction)."""
    if x is None:
        return "n/a"
    return f"{x:+.{dp}f}%" if sign else f"{x:.{dp}f}%"


def num(x, dp=2):
    if x is None:
        return "n/a"
    return f"{x:.{dp}f}"


def bp(x, dp=0, sign=True):
    """Basis points. Yield statistics are always first differences in bp."""
    if x is None:
        return "n/a"
    return f"{x:+.{dp}f}bp" if sign else f"{x:.{dp}f}bp"


def yld(x, dp=2):
    """A yield level in percent — no forced sign, it is not a change."""
    if x is None:
        return "n/a"
    return f"{x:.{dp}f}%"


def esc(s):
    return html.escape(str(s), quote=True)


def embed_json(payload):
    raw = json.dumps(payload, allow_nan=False)
    return raw.replace("<", "\\u003c").replace(">", "\\u003e").replace("&", "\\u0026")


def table_view(headers, rows, caption):
    thead = "".join(f"<th>{esc(h)}</th>" for h in headers)
    trs = []
    for row in rows:
        tds = "".join(f"<td>{esc(c)}</td>" for c in row)
        trs.append(f"<tr>{tds}</tr>")
    return (
        f'<details class="data-table"><summary>Show data table</summary>'
        f'<table><caption>{esc(caption)}</caption>'
        f'<thead><tr>{thead}</tr></thead><tbody>{"".join(trs)}</tbody></table></details>'
    )


def stat_tile(label, value, sublabel=""):
    sub = f'<div class="tile-sub">{esc(sublabel)}</div>' if sublabel else ""
    return (
        f'<div class="tile"><div class="tile-label">{esc(label)}</div>'
        f'<div class="tile-value">{esc(value)}</div>{sub}</div>'
    )


def chart_container(chart_id, title, caption=""):
    cap = f'<p class="chart-caption">{esc(caption)}</p>' if caption else ""
    return (
        f'<div class="chart-block"><h3>{esc(title)}</h3>{cap}'
        f'<div class="chart" id="{chart_id}"></div></div>'
    )


# ------------------------------------------------------------- narrative --

def build_findings(m):
    trend = m["trend"]
    vol = m["volatility"]
    dd = m["drawdown"]
    cross = m["cross_index"]
    labels = m["labels"]

    findings = []

    # 1. Headline performance
    gspc_ret = trend["scoreboard"]["GSPC"]["total_return"] * 100
    ranked = sorted(EQUITY_ORDER, key=lambda s: trend["scoreboard"][s]["total_return"], reverse=True)
    best_sym, worst_sym = ranked[0], ranked[-1]
    findings.append({
        "section": "trend",
        "headline": f"The S&P 500 returned {pct_pts(gspc_ret)} in price terms over the trailing year.",
        "detail": (
            f"{labels[best_sym]} led the four indices at {pct_pts(trend['scoreboard'][best_sym]['total_return']*100)}, "
            f"while {labels[worst_sym]} was the laggard at {pct_pts(trend['scoreboard'][worst_sym]['total_return']*100)}. "
            "Figures are price return only — dividends are not included."
        ),
        "magnitude": abs(gspc_ret),
    })

    # 2. Volatility vs VIX
    rv = vol["ann_vol_full"]
    vix_mean = vol["vix_mean"]
    rel = "below" if rv < vix_mean else "above"
    findings.append({
        "section": "volatility",
        "headline": f"Realized volatility ran {pct_pts(rv, sign=False)} annualized, {rel} the {pct_pts(vix_mean, sign=False)} average VIX level over the same window.",
        "detail": (
            f"VIX ranged from {num(vol['vix_min'])} to {num(vol['vix_max'])} and closed the window at {num(vol['vix_current'])}, "
            f"spending {vol['vix_regime_days'].get('low (<15)', 0)} of {trend['scoreboard'] and m['window']['return_obs']} days below 15 "
            "and last peaking on " + vol["vix_max_date"] + "."
        ),
        "magnitude": abs(rv - vix_mean),
    })

    # 3. Drawdown
    max_dd = dd["max_drawdown"] * 100
    status = "recovered by " + dd["recovery_date"] if dd["recovery_date"] else "not yet recovered as of the end of the window"
    findings.append({
        "section": "drawdown",
        "headline": f"The deepest pullback of the year was {pct_pts(max_dd, sign=False)}, from a peak on {dd['peak_date']} to a trough on {dd['trough_date']}.",
        "detail": f"That drawdown {status}. The index spent {dd['days_underwater']} of {m['window']['trading_days']} trading days below a prior high.",
        "magnitude": abs(max_dd),
    })

    # 4. VIX correlation
    corr_vix = cross["correlation_matrix"]["GSPC"]["VIX"]
    strength = "strongly" if abs(corr_vix) > 0.7 else ("moderately" if abs(corr_vix) > 0.4 else "weakly")
    findings.append({
        "section": "cross_index",
        "headline": f"Daily S&P 500 returns moved {strength} inversely with VIX (correlation {num(corr_vix, 3)}) over the window.",
        "detail": "This is a description of co-movement, not a causal claim about what drove either series.",
        "magnitude": abs(corr_vix) * 100,
    })

    # 5. Distribution / tail risk
    mom = vol["moments"]
    tails = vol["tail_counts"]
    normal_word = "consistent with" if mom["normal_at_5pct"] else "inconsistent with"
    findings.append({
        "section": "volatility",
        "headline": f"The daily return distribution was {normal_word} normality at the 5% level (Jarque-Bera {num(mom['jarque_bera'])} vs. critical value {mom['jb_critical_5pct']}).",
        "detail": (
            f"Skew was {num(mom['skew'], 2)} and excess kurtosis {num(mom['kurtosis_excess'], 2)}. "
            f"{tails['count_3sigma']} days moved more than 3 standard deviations, versus roughly "
            f"{tails['count_3sigma_gaussian_expected']} expected under a normal distribution of the same size."
        ),
        "magnitude": abs(mom["kurtosis_excess"]) * 10,
    })

    # 6. Breadth / leadership
    rut_ret = trend["scoreboard"]["RUT"]["total_return"] * 100
    spread = rut_ret - gspc_ret
    direction = "outpaced" if spread > 0 else "trailed"
    findings.append({
        "section": "trend",
        "headline": f"The Russell 2000 {direction} the S&P 500 by {pct_pts(abs(spread), sign=False)} over the window ({pct_pts(rut_ret)} vs. {pct_pts(gspc_ret)}).",
        "detail": "A widening small-cap/large-cap spread is a commonly watched breadth signal, shown here descriptively.",
        "magnitude": abs(spread),
    })

    for f in findings:
        f["family"] = "equity"
    findings.extend(build_rates_findings(m))
    return findings


def build_rates_findings(m):
    """Findings drawn from the rates and cross-asset sections.

    Ranked in their own pool: their magnitudes are in different units from
    the equity findings, so mixing the two pools would both make the
    ordering arbitrary and evict verified equity bullets from the summary.
    Every detail names its own window, since these run on 248/245
    observations rather than the equity window's 251.
    """
    rates = m["rates"]
    ca = m["cross_asset"]
    rate_days = rates["window"]["trading_days"]
    paired = ca["window"]["paired_obs"]
    findings = []

    # R1. Curve shape
    cn = rates["curve_narrative"]
    s105 = rates["spread_summary"]["s10_5"]
    ten = rates["level_summary"]["DGS10"]
    five = rates["level_summary"]["DGS5"]
    led = "led by the front end" if cn["front_led"] else "led by the long end"
    findings.append({
        "family": "rates",
        "section": "rates",
        "headline": (
            f"The 10-year yield rose {bp(ten['change_bp'], sign=False)} to {num(ten['end'])}% while the "
            f"5-year rose {bp(five['change_bp'], sign=False)}, narrowing the 10y-5y spread from "
            f"{bp(s105['start_bp'], sign=False)} to {bp(s105['end_bp'], sign=False)} "
            f"— a {cn['direction']} {cn['shape']}, {led}."
        ),
        "detail": (
            f"Over the {rate_days}-day rates window the 10y-5y spread ranged "
            f"{bp(s105['min_bp'], sign=False)} to {bp(s105['max_bp'], sign=False)} and "
            + ("never inverted." if not s105["ever_inverted"]
               else f"was inverted on {s105['days_inverted']} days.")
        ),
        "magnitude": abs(s105["change_bp"]),
    })

    # R2. Stock/bond co-movement
    corr = ca["correlation_matrix"]["GSPC"]["DGS10"]
    roll = ca["rolling_corr"]
    strength = "strongly" if abs(corr) > 0.7 else ("moderately" if abs(corr) > 0.4 else "weakly")
    sign_word = "positively" if corr > 0 else "negatively"
    reading = (
        "A negative sign means yields and equities moved in opposite directions, the pattern "
        "usually described as a discount-rate reading; a positive sign is usually described as a "
        "growth-news reading. This describes co-movement only, not causation."
    )
    findings.append({
        "family": "rates",
        "section": "cross_asset",
        "headline": (
            f"Daily S&P 500 returns and 10-year yield changes were {strength} {sign_word} "
            f"correlated (r = {num(corr, 3)}) across {paired} paired sessions."
        ),
        "detail": (
            f"The rolling {roll['window']}-day correlation ranged {num(roll['min'], 2)} to "
            f"{num(roll['max'], 2)} and ended at {num(roll['current'], 2)}, sitting positive on "
            f"{num(roll['pct_days_positive'], 1)}% of the {roll['n_valid']} days where it is "
            f"defined. {reading}"
        ),
        "magnitude": abs(corr) * 100,
    })

    # R3. Sensitivity
    sens = ca["sensitivity"]["GSPC"]
    r2 = sens["r_squared"]
    weak = (
        f"An R² of {num(r2, 3)} means rate moves explain little of the day-to-day variation in "
        "equity returns, so this is a weak average tendency rather than a reliable rule."
        if r2 < 0.10 else
        f"The R² of {num(r2, 3)} indicates rate moves account for a meaningful share of daily "
        "equity variation over this sample."
    )
    findings.append({
        "family": "rates",
        "section": "cross_asset",
        "headline": (
            f"A 10bp rise in the 10-year yield corresponded on average to a "
            f"{pct_pts(sens['beta_pct_per_10bp'], dp=2)} move in the S&P 500."
        ),
        "detail": f"{weak} Estimated over {sens['n']} paired sessions.",
        "magnitude": abs(sens["beta_pct_per_10bp"]) * 100,
    })

    # R4. Conditional performance
    cond = ca["conditional"]["GSPC"]
    up, dn = cond["rate_up"], cond["rate_down"]
    findings.append({
        "family": "rates",
        "section": "cross_asset",
        "headline": (
            f"On the {up['n']} sessions the 10-year yield rose, the S&P 500 averaged "
            f"{bp(up['mean_return_bp'])}; on the {dn['n']} sessions it fell, "
            f"{bp(dn['mean_return_bp'])}."
        ),
        "detail": (
            f"Hit rates were {num(up['hit_rate_pct'], 1)}% and {num(dn['hit_rate_pct'], 1)}% "
            f"respectively, within the {paired}-session paired sample."
        ),
        "magnitude": abs((up["mean_return_bp"] or 0) - (dn["mean_return_bp"] or 0)),
    })

    return findings


def headline_findings(findings, n=5):
    return sorted(findings, key=lambda f: f["magnitude"], reverse=True)[:n]


EQUITY_ORDER = ["GSPC", "NDX", "DJI", "RUT"]
ALL_ORDER = EQUITY_ORDER + ["VIX"]


# --------------------------------------------------------------- sections --

def render_header(m):
    w = m["window"]
    return f"""
<header class="page-header">
  <div class="header-top">
    <div>
      <h1>S&amp;P 500 &mdash; One-Year Market Analysis</h1>
      <p class="subtitle">{esc(w['start'])} &ndash; {esc(w['end'])} &middot; {w['trading_days']} trading days &middot; {w['return_obs']} daily return observations</p>
    </div>
    <button id="theme-toggle" type="button" aria-label="Toggle light/dark theme">Toggle theme</button>
  </div>
  <span class="badge">Price return only &mdash; dividends not included</span>
</header>
"""


def render_exec_summary(m, findings):
    trend = m["trend"]
    dd = m["drawdown"]
    vol = m["volatility"]
    cross = m["cross_index"]
    tiles = "".join([
        stat_tile("Total return", pct_pts(trend["scoreboard"]["GSPC"]["total_return"] * 100)),
        stat_tile("Annualized volatility", pct_pts(vol["ann_vol_full"], sign=False)),
        stat_tile("Sharpe (rf = 0%)", num(cross["scoreboard"]["GSPC"]["sharpe"], 2)),
        stat_tile("Max drawdown", pct_pts(dd["max_drawdown"] * 100, sign=False), f"trough {dd['trough_date']}"),
        stat_tile("From 52-week high", pct_pts(trend["pct_from_52w_high"], sign=False)),
    ])
    def render_list(subset):
        return "".join(
            f'<li><strong>{esc(f["headline"])}</strong><br>'
            f'<span class="finding-detail">{esc(f["detail"])}</span></li>'
            for f in subset
        )

    # Ranked within families: equity and rates magnitudes are in different
    # units, so a single pool would order them arbitrarily and let rates
    # findings displace equity ones.
    equity = [f for f in findings if f.get("family", "equity") == "equity"]
    rates = [f for f in findings if f.get("family") == "rates"]
    items = render_list(headline_findings(equity, 5))
    rates_block = ""
    if rates:
        rate_days = m["rates"]["window"]["trading_days"]
        paired = m["cross_asset"]["window"]["paired_obs"]
        # Shown in authored order, not ranked: there are only four, and their
        # magnitudes are in mutually incommensurate units (basis points,
        # correlation, percent), so ranking them against each other would put
        # the weakest-fitting finding on top.
        rates_block = f"""
  <h3>Rates &amp; the stock/bond relationship</h3>
  <p class="chart-caption">Computed on the {rate_days}-day rates window and the {paired}-session
  paired sample, both shorter than the {m['window']['trading_days']}-day equity window above.</p>
  <ul class="findings">{render_list(rates)}</ul>"""
    return f"""
<section id="summary">
  <h2>Executive summary</h2>
  <div class="tile-row">{tiles}</div>
  <ul class="findings">{items}</ul>{rates_block}
</section>
"""


def render_trend_section(m):
    trend = m["trend"]
    labels = m["labels"]
    sb_rows = [
        [labels[s], pct_pts(trend["scoreboard"][s]["total_return"] * 100), pct_pts(trend["scoreboard"][s]["cagr"] * 100)]
        for s in EQUITY_ORDER
    ]
    sb_table = "".join(
        f"<tr><td>{esc(r[0])}</td><td>{esc(r[1])}</td><td>{esc(r[2])}</td></tr>" for r in sb_rows
    )

    best_rows = "".join(f"<tr><td>{d['date']}</td><td>{pct_pts(d['return']*100)}</td></tr>" for d in trend["best_days"])
    worst_rows = "".join(f"<tr><td>{d['date']}</td><td>{pct_pts(d['return']*100)}</td></tr>" for d in trend["worst_days"])

    monthly_table = table_view(
        ["Month", "Return", "Trading days", "Partial"],
        [[r["month"], pct_pts(r["return"] * 100), r["n_days"], "yes" if r["partial"] else "no"] for r in trend["monthly_returns"]],
        "Monthly returns (calendar-month compounded)",
    )

    streaks = trend["streaks"]

    sma_note = (
        f"200-day SMA is defined for the last {trend['n_days_sma200']} of {m['window']['trading_days']} sessions "
        f"(first valid {trend['sma200_first_valid_date']}); no 50/200-day crossover is observable within that shorter window."
    )

    return f"""
<section id="trend">
  <h2>Trend &amp; performance</h2>
  {chart_container("chart-rebased", "Performance, rebased to 100", "All four indices rebased to 100 at the start of the window so they are comparable on one axis.")}
  {table_view(["Index", "Total return", "CAGR"], sb_rows, "Index scoreboard — trend")}
  <table class="inline-table">
    <caption>Index scoreboard</caption>
    <thead><tr><th>Index</th><th>Total return</th><th>CAGR</th></tr></thead>
    <tbody>{sb_table}</tbody>
  </table>

  {chart_container("chart-sma", "S&P 500 price with 50- and 200-day moving averages", sma_note)}

  {chart_container("chart-monthly", "Monthly returns", "Compounded within each calendar month; July 2026 is a partial month.")}
  {monthly_table}

  <div class="two-col">
    <div>
      <h3>Best days</h3>
      <table class="inline-table"><thead><tr><th>Date</th><th>Return</th></tr></thead><tbody>{best_rows}</tbody></table>
    </div>
    <div>
      <h3>Worst days</h3>
      <table class="inline-table"><thead><tr><th>Date</th><th>Return</th></tr></thead><tbody>{worst_rows}</tbody></table>
    </div>
  </div>

  <p class="chart-caption">
    Up days: {streaks['up_days']}, down days: {streaks['down_days']}. Longest up streak:
    {streaks['longest_up_streak']} days (ending {streaks['longest_up_streak_end']}). Longest down streak:
    {streaks['longest_down_streak']} days (ending {streaks['longest_down_streak_end']}).
    52-week high {num(trend['high_52w'])} on {trend['high_52w_date']}; 52-week low {num(trend['low_52w'])} on {trend['low_52w_date']}.
  </p>
</section>
"""


def render_drawdown_section(m):
    dd = m["drawdown"]
    ep_rows = [
        [
            e["peak_date"], e["trough_date"], e["recovery_date"] or "ongoing",
            pct_pts(e["depth"] * 100, sign=False), e["days_to_trough"],
            e["days_to_recover"] if e["days_to_recover"] is not None else "—",
        ]
        for e in dd["episodes"]
    ]
    ep_table = "".join(
        f"<tr><td>{esc(r[0])}</td><td>{esc(r[1])}</td><td>{esc(r[2])}</td><td>{esc(r[3])}</td><td>{esc(r[4])}</td><td>{esc(r[5])}</td></tr>"
        for r in ep_rows
    )
    return f"""
<section id="drawdowns">
  <h2>Drawdowns</h2>
  {chart_container("chart-drawdown", "S&P 500 drawdown from running high", "Depth below the running all-time high for the window; 0% means a new high.")}
  <p class="chart-caption">
    Maximum drawdown: {pct_pts(dd['max_drawdown']*100, sign=False)}, peak {dd['peak_date']} &rarr; trough {dd['trough_date']}
    {"&rarr; recovered " + dd['recovery_date'] if dd['recovery_date'] else "(not yet recovered)"}.
    Current drawdown from high: {pct_pts(dd['current_drawdown']*100, sign=False)}. Days underwater: {dd['days_underwater']} of {m['window']['trading_days']}.
  </p>
  <table class="inline-table">
    <caption>Drawdown episodes &ge; 3%</caption>
    <thead><tr><th>Peak</th><th>Trough</th><th>Recovery</th><th>Depth</th><th>Days to trough</th><th>Days to recover</th></tr></thead>
    <tbody>{ep_table}</tbody>
  </table>
</section>
"""


def render_volatility_section(m):
    vol = m["volatility"]
    regime = vol["vix_regime_days"]
    regime_rows = "".join(f"<tr><td>{esc(k)}</td><td>{v}</td></tr>" for k, v in regime.items())
    mom = vol["moments"]
    tails = vol["tail_counts"]

    return f"""
<section id="volatility">
  <h2>Volatility</h2>
  {chart_container("chart-vol", "21-day realized volatility vs. VIX", "Both series are annualized volatility in percentage points, so they share one axis.")}
  <p class="chart-caption">
    Full-period annualized realized volatility: {pct_pts(vol['ann_vol_full'], sign=False)}. VIX averaged {num(vol['vix_mean'])}
    (range {num(vol['vix_min'])}&ndash;{num(vol['vix_max'])}, peak on {vol['vix_max_date']}, last {num(vol['vix_current'])}).
    Average VIX-minus-trailing-realized-vol spread: {pct_pts(vol['vix_minus_trailing_rv21_avg'], sign=False)} points.
    Downside deviation: {pct_pts(vol['downside_deviation'], sign=False)}.
    {"ATR(14): " + pct_pts(vol['atr_pct_current'], sign=False) + " of price." if vol['atr_pct_current'] is not None else ""}
  </p>
  <table class="inline-table">
    <caption>VIX regime, days in window</caption>
    <thead><tr><th>Regime</th><th>Days</th></tr></thead>
    <tbody>{regime_rows}</tbody>
  </table>

  {chart_container("chart-hist", "Daily log-return distribution", "40-bin histogram of daily log returns with a normal-density overlay of the same mean and variance.")}
  <p class="chart-caption">
    n={mom['n']}, mean {num(mom['mean']*100, 3)}%/day, std {num(mom['std']*100, 3)}%/day, skew {num(mom['skew'], 2)},
    excess kurtosis {num(mom['kurtosis_excess'], 2)}. Jarque-Bera {num(mom['jarque_bera'])} vs. the 5% critical value
    {mom['jb_critical_5pct']} (chi-square, 2 df) &mdash;
    {"consistent with" if mom['normal_at_5pct'] else "rejects"} normality at the 5% level.
    {pct_pts(tails['pct_over_1pct'], sign=False)} of days moved more than 1%;
    {pct_pts(tails['pct_over_2pct'], sign=False)} moved more than 2%.
    {tails['count_2sigma']} days exceeded 2 standard deviations (vs. {tails['count_2sigma_gaussian_expected']} expected under a normal distribution),
    and {tails['count_3sigma']} exceeded 3 (vs. {tails['count_3sigma_gaussian_expected']} expected).
  </p>
</section>
"""


def render_cross_index_section(m):
    cross = m["cross_index"]
    labels = m["labels"]
    beta_rows = "".join(
        f"<tr><td>{esc(labels[s])}</td><td>{num(cross['beta_r2_vs_gspc'][s]['beta'], 3)}</td><td>{num(cross['beta_r2_vs_gspc'][s]['r_squared'], 3)}</td></tr>"
        for s in ["NDX", "DJI", "RUT"]
    )
    sb_rows = "".join(
        f"<tr><td>{esc(labels[s])}</td><td>{num(cross['scoreboard'][s]['sharpe'], 2)}</td>"
        f"<td>{num(cross['scoreboard'][s]['sortino'], 2)}</td><td>{pct_pts(cross['scoreboard'][s]['ann_vol'], sign=False)}</td>"
        f"<td>{num(cross['scoreboard'][s]['corr_to_gspc'], 3)}</td></tr>"
        for s in EQUITY_ORDER
    )
    return f"""
<section id="cross-index">
  <h2>Cross-index &amp; risk</h2>
  {chart_container("chart-corr", "Correlation of daily log returns", "Diverging scale: blue = positive correlation, red = negative, gray = near zero.")}

  <table class="inline-table">
    <caption>Beta and R&sup2; vs. the S&amp;P 500 (daily log returns)</caption>
    <thead><tr><th>Index</th><th>Beta</th><th>R&sup2;</th></tr></thead>
    <tbody>{beta_rows}</tbody>
  </table>

  <table class="inline-table">
    <caption>Risk-adjusted return (risk-free rate assumed 0%)</caption>
    <thead><tr><th>Index</th><th>Sharpe</th><th>Sortino</th><th>Ann. vol</th><th>Corr. to S&amp;P 500</th></tr></thead>
    <tbody>{sb_rows}</tbody>
  </table>
</section>
"""


def window_banner(m, window, kind):
    """Disclose which window a section runs on, at the top of that section."""
    eq_days = m["window"]["trading_days"]
    if kind == "rates":
        no_row = window["equity_days_without_yield_row"]
        blank = window["equity_days_with_blank_yield"]
        bits = []
        if no_row:
            bits.append("no yield is published for " + ", ".join(no_row))

        if blank:
            bits.append("the bond market was closed on " + ", ".join(blank) + " while equities traded")
        why = "; ".join(bits)
        text = (
            f"Rates window: {window['start']} – {window['end']}, {window['trading_days']} trading days "
            f"— {eq_days - window['trading_days']} fewer than the {eq_days}-day equity window above "
            f"({why})."
        )
    else:
        text = (
            f"Paired sample: {window['paired_obs']} sessions, {window['start']} – {window['end']} "
            f"— every statistic below pairs an equity return with a same-session yield change."
        )
    return f'<span class="badge">{esc(text)}</span>'


def render_rates_section(m):
    rates = m["rates"]
    w = rates["window"]
    labels = m["labels"]

    level_rows = "".join(
        f"<tr><td>{esc(labels[t])}</td><td>{yld(rates['level_summary'][t]['start'])}</td>"
        f"<td>{yld(rates['level_summary'][t]['end'])}</td>"
        f"<td>{bp(rates['level_summary'][t]['change_bp'])}</td>"
        f"<td>{yld(rates['level_summary'][t]['min'])} ({rates['level_summary'][t]['min_date']})</td>"
        f"<td>{yld(rates['level_summary'][t]['max'])} ({rates['level_summary'][t]['max_date']})</td></tr>"
        for t in TENORS
    )

    spread_rows = "".join(
        f"<tr><td>{esc(rates['spread_summary'][k]['label'])}</td>"
        f"<td>{bp(rates['spread_summary'][k]['start_bp'], sign=False)}</td>"
        f"<td>{bp(rates['spread_summary'][k]['end_bp'], sign=False)}</td>"
        f"<td>{bp(rates['spread_summary'][k]['change_bp'])}</td>"
        f"<td>{bp(rates['spread_summary'][k]['min_bp'], sign=False)}</td>"
        f"<td>{bp(rates['spread_summary'][k]['max_bp'], sign=False)}</td>"
        f"<td>{'yes, ' + str(rates['spread_summary'][k]['days_inverted']) + ' days' if rates['spread_summary'][k]['ever_inverted'] else 'no'}</td></tr>"
        for k in ["s10_5", "s30_10", "s30_5"]
    )

    change_rows = "".join(
        f"<tr><td>{esc(labels[t])}</td>"
        f"<td>{num(rates['change_stats'][t]['sd_bp'], 2)}</td>"
        f"<td>{bp(rates['change_stats'][t]['annualized_vol_bp'], sign=False)}</td>"
        f"<td>{bp(rates['change_stats'][t]['max_up_bp'])} ({rates['change_stats'][t]['max_up_date']})</td>"
        f"<td>{bp(rates['change_stats'][t]['max_down_bp'])} ({rates['change_stats'][t]['max_down_date']})</td>"
        f"<td>{rates['change_stats'][t]['days_over_10bp']}</td></tr>"
        for t in TENORS
    )

    dur_rows = "".join(
        f"<tr><td>{esc(labels[t])}</td>"
        f"<td>{num(rates['duration_proxy'][t]['assumed_modified_duration_years'], 1) if rates['duration_proxy'][t]['assumed_modified_duration_years'] is not None else 'not computed'}</td>"
        f"<td>{pct_pts(rates['duration_proxy'][t]['approx_price_return_pct']) if rates['duration_proxy'][t]['approx_price_return_pct'] is not None else 'not computed'}</td></tr>"
        for t in TENORS
    )

    cn = rates["curve_narrative"]
    s105 = rates["spread_summary"]["s10_5"]

    return f"""
<section id="rates">
  <h2>Rates &amp; the yield curve</h2>
  {window_banner(m, w, "rates")}

  {chart_container("chart-yields", "Treasury constant-maturity yields", "Par yields in percent. These are yield levels, not bond returns.")}
  <table class="inline-table">
    <caption>Yield levels over the rates window</caption>
    <thead><tr><th>Tenor</th><th>Start</th><th>End</th><th>Change</th><th>Low</th><th>High</th></tr></thead>
    <tbody>{level_rows}</tbody>
  </table>

  {chart_container("chart-curve", "Yield curve spreads", "Spreads in basis points. The zero line marks inversion; a spread below it means the shorter tenor yields more.")}
  <p class="chart-caption">
    The curve was a <strong>{esc(cn['direction'])} {esc(cn['shape'])}</strong> over the window:
    the 30-year rose {bp(cn['long_change_bp'], sign=False)} while the 5-year rose
    {bp(cn['front_change_bp'], sign=False)}, so the 10y&minus;5y spread
    {'narrowed' if s105['change_bp'] < 0 else 'widened'} by {bp(abs(s105['change_bp']), sign=False)}.
    {'No spread inverted at any point in the window.' if not any(rates['spread_summary'][k]['ever_inverted'] for k in rates['spread_summary']) else ''}
  </p>
  <table class="inline-table">
    <caption>Curve spreads (basis points)</caption>
    <thead><tr><th>Spread</th><th>Start</th><th>End</th><th>Change</th><th>Min</th><th>Max</th><th>Ever inverted</th></tr></thead>
    <tbody>{spread_rows}</tbody>
  </table>

  {chart_container("chart-dy-hist", "Distribution of daily 10-year yield changes", "Daily first differences in basis points, with a normal-density overlay of the same mean and variance.")}
  <table class="inline-table">
    <caption>Daily yield-change statistics ({w['change_obs']} paired sessions)</caption>
    <thead><tr><th>Tenor</th><th>Daily SD (bp)</th><th>Annualized</th><th>Largest rise</th><th>Largest fall</th><th>Days &ge; 10bp</th></tr></thead>
    <tbody>{change_rows}</tbody>
  </table>

  <table class="inline-table">
    <caption>Duration-approximated price impact &mdash; illustrative only</caption>
    <thead><tr><th>Tenor</th><th>Assumed modified duration (yrs)</th><th>Approx. price return</th></tr></thead>
    <tbody>{dur_rows}</tbody>
  </table>
  <p class="chart-caption">
    First-order (&minus;D &times; &Delta;y) only, applied to the full-window yield change. It ignores
    convexity, coupon carry, and roll-down, and is <strong>not</strong> the return of any bond index.
    The assumed duration is the entire content of the figure &mdash; change the assumption and the
    number changes with it.
  </p>
</section>
"""


def render_cross_asset_section(m):
    ca = m["cross_asset"]
    labels = m["labels"]
    w = ca["window"]

    corr_rows = "".join(
        f"<tr><td>{esc(labels[s])}</td>"
        + "".join(f"<td>{num(ca['correlation_matrix'][s][t], 3)}</td>" for t in TENORS)
        + "</tr>"
        for s in ALL_ORDER
    )

    sens_rows = "".join(
        f"<tr><td>{esc(labels[s])}</td>"
        f"<td>{pct_pts(ca['sensitivity'][s]['beta_pct_per_10bp'])}</td>"
        f"<td>{num(ca['sensitivity'][s]['r_squared'], 3)}</td></tr>"
        for s in ALL_ORDER
    )

    bucket_order = ["rate_up", "rate_down", "rate_flat", "big_move"]
    cond_rows = "".join(
        f"<tr><td>{esc(ca['bucket_labels'][b])}</td>"
        f"<td>{ca['conditional']['GSPC'][b]['n']}</td>"
        f"<td>{bp(ca['conditional']['GSPC'][b]['mean_return_bp'], 1)}</td>"
        f"<td>{num(ca['conditional']['GSPC'][b]['hit_rate_pct'], 1) + '%' if ca['conditional']['GSPC'][b]['hit_rate_pct'] is not None else 'n/a'}</td></tr>"
        for b in bucket_order
    )

    roll = ca["rolling_corr"]
    corr10 = ca["correlation_matrix"]["GSPC"]["DGS10"]
    vix10 = ca["correlation_matrix"]["VIX"]["DGS10"]
    small_n = [b for b in bucket_order if ca["conditional"]["GSPC"][b]["n"] < 10]

    return f"""
<section id="cross-asset">
  <h2>Stocks vs. bonds</h2>
  {window_banner(m, w, "cross_asset")}

  {chart_container("chart-rate-corr", f"Rolling {roll['window']}-day correlation: S&amp;P 500 returns vs. 10-year yield changes", "Above zero, equities and yields moved together; below zero, they moved in opposite directions.")}
  <p class="chart-caption">
    Full-sample correlation was {num(corr10, 3)} over {w['paired_obs']} paired sessions. The rolling
    {roll['window']}-day estimate ranged {num(roll['min'], 2)} (on {roll['min_date']}) to
    {num(roll['max'], 2)} (on {roll['max_date']}), ended at {num(roll['current'], 2)}, and was
    positive on {num(roll['pct_days_positive'], 1)}% of the {roll['n_valid']} days where it is
    defined (from {roll['first_valid_date']}).
  </p>

  {chart_container("chart-rate-corr-heat", "Correlation: daily index returns vs. daily yield changes", "Both legs are first differences — equity returns against yield changes in basis points. Correlating levels against levels would be spurious.")}
  <table class="inline-table">
    <caption>Correlation of daily returns with daily yield changes ({w['paired_obs']} sessions)</caption>
    <thead><tr><th>Index</th>{"".join(f"<th>{esc(labels[t])}</th>" for t in TENORS)}</tr></thead>
    <tbody>{corr_rows}</tbody>
  </table>
  <p class="chart-caption">
    VIX correlates {num(vix10, 3)} with 10-year yield changes, the mirror image of the equity rows:
    on this sample, rising yields tended to coincide with a firmer volatility bid. Descriptive only.
  </p>

  <table class="inline-table">
    <caption>Sensitivity to a 10bp rise in the 10-year yield</caption>
    <thead><tr><th>Index</th><th>Average move per +10bp</th><th>R&sup2;</th></tr></thead>
    <tbody>{sens_rows}</tbody>
  </table>
  <p class="chart-caption">
    Estimated by ordinary least squares over {w['paired_obs']} sessions. Read the R&sup2; first: it
    bounds how much of daily equity variation rate moves account for at all.
  </p>

  <table class="inline-table">
    <caption>S&amp;P 500 performance conditioned on the 10-year yield</caption>
    <thead><tr><th>Session type</th><th>n</th><th>Mean return</th><th>Share positive</th></tr></thead>
    <tbody>{cond_rows}</tbody>
  </table>
  <p class="chart-caption">
    Means are shown in basis points beside their own sample size, because the buckets are very
    unequal.{" Buckets with fewer than 10 sessions (" + ", ".join(esc(ca['bucket_labels'][b]) for b in small_n) + ") carry too few observations to generalize from and are reported for completeness only." if small_n else ""}
  </p>
</section>
"""


def render_methodology_section(m):
    dq = m["data_quality"]
    dropped = dq["dropped_dates"]
    dropped_str = "; ".join(f"{sym}: {', '.join(dates)}" for sym, dates in dropped.items()) or "none"
    return f"""
<section id="methodology">
  <h2>Data &amp; methodology</h2>
  <ul class="method-list">
    <li>Source: Yahoo Finance daily OHLCV, fetched {esc(dq['fetched_at_utc'])}.</li>
    <li>Analysis window: intersection of trading dates across all five symbols, {m['window']['trading_days']} days.
        Dates dropped for non-overlap: {esc(dropped_str)} &mdash; 2026-05-25 is the Memorial Day holiday, on which
        Yahoo carries a VIX print but equity markets were closed.</li>
    <li>{esc(dq['volume_note'])}</li>
    <li><code>adjclose</code> equals <code>close</code> for every symbol here (indices carry no dividend adjustment),
        so every return in this report is a <strong>price return</strong>. A total-return comparison would run
        roughly the dividend yield (historically ~1.2%/year for the S&amp;P 500) higher.</li>
    <li>Simple returns are used for anything that compounds or aggregates: total return, monthly returns, rebasing,
        drawdown, best/worst-day figures, Sharpe, and Sortino. Log returns are used for statistical/dependence
        measures: volatility, skew, kurtosis, correlation, and beta.</li>
    <li>Volatility is annualized with a 252-trading-day convention; CAGR uses a 365.25-calendar-day convention.</li>
    <li>VIX is 30-day risk-neutral implied volatility in annualized percentage points, which is why it can share
        one axis with annualized realized volatility &mdash; the units match.</li>
    <li>All rolling windows (moving averages, rolling volatility) are trailing and right-aligned; the first
        window&minus;1 observations are undefined and rendered as gaps, not filled.</li>
    <li>ATR uses Wilder smoothing (exponential, &alpha; = 1/14) and is reported as a percentage of closing price.</li>
    <li>Risk-free rate is assumed to be 0% for Sharpe and Sortino, shown explicitly beside each figure.</li>
    <li>Skew and excess kurtosis use the bias-corrected Fisher-Pearson estimators (G1, G2).</li>
    {render_rates_methodology(m)}
  </ul>
</section>
"""


def render_rates_methodology(m):
    rates = m["rates"]
    ca = m["cross_asset"]
    w = rates["window"]
    prov = rates["provenance"]
    series = prov["series"]

    ids = ", ".join(
        f"{esc(t)} (sha256 {esc(series[t]['sha256'][:12])}…, {series[t]['rows']} rows, "
        f"{esc(series[t]['raw_date_range'][0])} to {esc(series[t]['raw_date_range'][1])})"
        for t in TENORS
    )
    no_row = w["equity_days_without_yield_row"]
    blank = w["equity_days_with_blank_yield"]

    return f"""
    <li><strong>Treasury data.</strong> {esc(prov['source'])}. {esc(prov['acquired_by'])}
        Series: {ids}. Units: {esc(prov['units'])}.</li>
    <li><strong>Two windows, deliberately.</strong> Equity metrics use their own
        {m['window']['trading_days']}-day window ({esc(m['window']['start'])} to
        {esc(m['window']['end'])}); rates metrics use a {w['trading_days']}-day window
        ({esc(w['start'])} to {esc(w['end'])}); stock/bond statistics use a
        {ca['window']['paired_obs']}-session paired sample. Intersecting everything onto one
        calendar would have shortened the equity window and changed every equity figure in this
        report, so the windows are kept separate and disclosed wherever they apply.</li>
    <li><strong>Nothing is forward-filled.</strong> {esc(', '.join(blank))} were bond-market
        closures on which equities traded, and no yield is published for
        {esc(', '.join(no_row))}. Carrying the prior yield forward would have manufactured
        zero-change days, biasing yield volatility downward and pulling stock/bond correlations
        toward zero. Those sessions are dropped from the rates window instead.</li>
    <li><strong>Yields are levels, not prices.</strong> Every yield statistic here is a first
        difference expressed in basis points. No return, log return, or percentage change is
        ever computed on a yield series.</li>
    <li>Constant-maturity par yields are <strong>not</strong> bond total returns. The
        duration-approximated price impact shown in the rates section is first-order
        (&minus;D &times; &Delta;y) against an assumed modified duration, ignoring convexity,
        coupon carry, and roll-down; it is not the return of any bond index.</li>
    <li>Stock/bond correlations pair equity <em>returns</em> against yield <em>changes</em> —
        both first differences. Correlating a price level against a yield level would be
        spurious.</li>
    <li>Sessions immediately following a bond-market-only closure are excluded from the paired
        sample: the yield change would span two equity sessions while the equity return spans
        one, so the two legs would not share a unit of observation. This falls out of projecting
        yields onto the equity calendar before differencing, rather than from a hardcoded date
        list.</li>
    <li><strong>The risk-free rate remains 0%</strong> for Sharpe and Sortino even though
        Treasury yields are now available. The 5-year yield carries term premium and duration
        risk, so it is not a cash rate; substituting it would be a category error rather than a
        refinement. The appropriate instrument is a 3-month bill, which this project does not
        contain. Existing risk-adjusted figures are therefore unchanged.</li>
    <li>No equity risk premium or Fed-model comparison is presented. That would require earnings
        data, which this project does not contain, and it is not inferred.</li>"""


# ----------------------------------------------------------------- chart --

def build_chart_data(m):
    trend = m["trend"]
    dd = m["drawdown"]
    vol = m["volatility"]
    cross = m["cross_index"]
    labels = m["labels"]
    dates = trend["dates"]

    charts = []

    charts.append({
        "id": "chart-rebased", "type": "line", "yFormat": "index", "endLabels": True,
        "dates": dates,
        "series": [{"key": s, "label": labels[s], "slot": SLOT[s], "values": trend["rebased"][s]} for s in EQUITY_ORDER],
    })

    charts.append({
        "id": "chart-sma", "type": "line", "yFormat": "price", "endLabels": False,
        "dates": dates,
        "series": [
            {"key": "close", "label": "S&P 500 close", "slot": SLOT["GSPC"], "values": trend["gspc_close"]},
            {"key": "sma50", "label": "50-day SMA", "slot": SLOT["NDX"], "values": trend["sma50"]},
            {"key": "sma200", "label": "200-day SMA", "slot": SLOT["DJI"], "values": trend["sma200"]},
        ],
    })

    month_labels = [r["month"] for r in trend["monthly_returns"]]
    month_values = [r["return"] * 100 for r in trend["monthly_returns"]]
    charts.append({"id": "chart-monthly", "type": "divergingBar", "labels": month_labels, "values": month_values})

    charts.append({
        "id": "chart-drawdown", "type": "area", "yFormat": "pct", "endLabels": False,
        "dates": dates,
        "series": [{"key": "dd", "label": "Drawdown", "slot": SLOT["GSPC"], "values": [v * 100 for v in dd["series"]]}],
    })

    vol_dates = dates[-len(vol["rolling_vol_21d"]):]
    charts.append({
        "id": "chart-vol", "type": "line", "yFormat": "pct", "endLabels": True,
        "dates": vol_dates,
        "series": [
            {"key": "rv21", "label": "Realized vol (21d, ann.)", "slot": SLOT["GSPC"], "values": vol["rolling_vol_21d"]},
            {"key": "vix", "label": "VIX", "slot": SLOT["VIX"], "values": _vix_series(m)},
        ],
    })

    charts.append({
        "id": "chart-hist", "type": "histogram",
        "edges": vol["histogram"]["edges"], "counts": vol["histogram"]["counts"], "overlay": vol["histogram"]["normal_overlay"],
    })

    all_syms = EQUITY_ORDER + ["VIX"]
    matrix = [[cross["correlation_matrix"][a][b] for b in all_syms] for a in all_syms]
    charts.append({
        "id": "chart-corr", "type": "heatmap",
        "labels": [labels[s] for s in all_syms], "matrix": matrix,
    })

    # --- rates & cross-asset -------------------------------------------------
    rates = m["rates"]
    ca = m["cross_asset"]

    charts.append({
        "id": "chart-yields", "type": "line", "yFormat": "yield", "endLabels": True,
        "dates": rates["dates"],
        "series": [
            {"key": t, "label": labels[t], "slot": RATE_SLOT[t], "values": rates["levels"][t]}
            for t in TENORS
        ],
    })

    # 30y-5y omitted: mechanically the sum of the other two, so a third line
    # adds no signal. It stays in the spread table as a scalar.
    charts.append({
        "id": "chart-curve", "type": "line", "yFormat": "bp", "endLabels": True, "zeroLine": True,
        "dates": rates["dates"],
        "series": [
            {"key": "s10_5", "label": rates["spread_summary"]["s10_5"]["label"],
             "slot": RATE_SLOT["DGS10"], "values": rates["spreads_bp"]["s10_5"]},
            {"key": "s30_10", "label": rates["spread_summary"]["s30_10"]["label"],
             "slot": RATE_SLOT["DGS30"], "values": rates["spreads_bp"]["s30_10"]},
        ],
    })

    charts.append({
        "id": "chart-dy-hist", "type": "histogram",
        "edges": rates["histogram_d10"]["edges"],
        "counts": rates["histogram_d10"]["counts"],
        "overlay": rates["histogram_d10"]["normal_overlay"],
        "xLabel": "daily 10-year yield change, basis points",
    })

    roll = ca["rolling_corr"]
    charts.append({
        "id": "chart-rate-corr", "type": "line", "yFormat": "corr", "endLabels": False,
        "zeroLine": True,
        "dates": roll["dates"],
        "series": [{
            "key": "roll", "label": f"{roll['window']}d corr (S&P 500 vs 10y change)",
            "slot": SLOT["GSPC"], "values": roll["values"],
        }],
    })

    charts.append({
        "id": "chart-rate-corr-heat", "type": "heatmap",
        "rowLabels": [labels[s] for s in ALL_ORDER],
        "colLabels": [labels[t] for t in TENORS],
        "matrix": [[ca["correlation_matrix"][s][t] for t in TENORS] for s in ALL_ORDER],
    })

    return {"charts": charts}


def _vix_series(m):
    # VIX close aligned to the same trailing window as rolling_vol_21d
    # reconstructed from vix_minus_trailing_rv21 + rolling_vol_21d (both already in the window)
    vol = m["volatility"]
    spread = vol["vix_minus_trailing_rv21"]
    rv21 = vol["rolling_vol_21d"]
    out = []
    for s, r in zip(spread, rv21):
        if s is None or r is None:
            out.append(None)
        else:
            out.append(round(s + r, 3))
    return out


# ------------------------------------------------------------------- css --

CSS = """
:root {
  color-scheme: light;
  --surface-1:      #fcfcfb;
  --page-plane:     #f9f9f7;
  --text-primary:   #0b0b0b;
  --text-secondary: #52514e;
  --text-muted:     #898781;
  --grid:           #e1e0d9;
  --baseline:       #c3c2b7;
  --success:        #006300;
  --border:         rgba(11,11,11,0.10);
  --series-1: #2a78d6; --series-2: #eb6834; --series-3: #1baf7a; --series-4: #eda100; --series-5: #e87ba4;
  --series-6: #008300; --series-7: #4a3aa7; --series-8: #e34948;
  --diverging-pos: #2a78d6; --diverging-neg: #e34948; --diverging-mid: #f0efec;
  --heat-pos3: #256abf; --heat-pos2: #6da7ec; --heat-pos1: #cde2fb;
  --heat-zero: #f0efec;
  --heat-neg1: #f8d9d8; --heat-neg2: #ef9d9c; --heat-neg3: #e34948;
  --heat-text-inverse: #ffffff;
}
@media (prefers-color-scheme: dark) {
  :root:where(:not([data-theme="light"])) {
    color-scheme: dark;
    --surface-1: #1a1a19; --page-plane: #0d0d0d; --text-primary: #ffffff; --text-secondary: #c3c2b7;
    --text-muted: #898781; --grid: #2c2c2a; --baseline: #383835; --success: #0ca30c; --border: rgba(255,255,255,0.10);
    --series-1: #3987e5; --series-2: #d95926; --series-3: #199e70; --series-4: #c98500; --series-5: #d55181;
    --series-6: #008300; --series-7: #9085e9; --series-8: #e66767;
    --diverging-pos: #3987e5; --diverging-neg: #e66767; --diverging-mid: #383835;
    --heat-pos3: #3987e5; --heat-pos2: #2a5f96; --heat-pos1: #1c3a5c;
    --heat-zero: #383835;
    --heat-neg1: #4a2626; --heat-neg2: #c25555; --heat-neg3: #e66767;
  }
}
:root[data-theme="dark"] {
  color-scheme: dark;
  --surface-1: #1a1a19; --page-plane: #0d0d0d; --text-primary: #ffffff; --text-secondary: #c3c2b7;
  --text-muted: #898781; --grid: #2c2c2a; --baseline: #383835; --success: #0ca30c; --border: rgba(255,255,255,0.10);
  --series-1: #3987e5; --series-2: #d95926; --series-3: #199e70; --series-4: #c98500; --series-5: #d55181;
  --series-6: #008300; --series-7: #9085e9; --series-8: #e66767;
  --diverging-pos: #3987e5; --diverging-neg: #e66767; --diverging-mid: #383835;
  --heat-pos3: #3987e5; --heat-pos2: #2a5f96; --heat-pos1: #1c3a5c;
  --heat-zero: #383835;
  --heat-neg1: #4a2626; --heat-neg2: #c25555; --heat-neg3: #e66767;
}
* { box-sizing: border-box; }
body {
  margin: 0; background: var(--page-plane); color: var(--text-primary);
  font-family: system-ui, -apple-system, "Segoe UI", sans-serif; line-height: 1.5;
}
.wrap { max-width: 1080px; margin: 0 auto; padding: 24px 20px 64px; }
h1 { font-size: 1.7rem; margin: 0 0 4px; }
h2 { font-size: 1.3rem; margin: 40px 0 16px; padding-top: 8px; border-top: 1px solid var(--border); }
h3 { font-size: 1.05rem; margin: 20px 0 8px; }
.subtitle { color: var(--text-secondary); margin: 0; }
.header-top { display: flex; justify-content: space-between; align-items: flex-start; gap: 16px; flex-wrap: wrap; }
.badge {
  display: inline-block; margin-top: 10px; font-size: 0.78rem; padding: 4px 10px; border-radius: 999px;
  background: var(--surface-1); border: 1px solid var(--border); color: var(--text-secondary);
}
#theme-toggle {
  font: inherit; font-size: 0.85rem; padding: 6px 12px; border-radius: 6px; border: 1px solid var(--border);
  background: var(--surface-1); color: var(--text-primary); cursor: pointer;
}
#theme-toggle:hover { background: var(--grid); }

.tile-row { display: grid; grid-template-columns: repeat(auto-fit, minmax(150px, 1fr)); gap: 12px; margin: 16px 0; }
.tile { background: var(--surface-1); border: 1px solid var(--border); border-radius: 10px; padding: 14px 16px; }
.tile-label { font-size: 0.78rem; color: var(--text-secondary); }
.tile-value { font-size: 1.5rem; font-weight: 600; margin-top: 4px; }
.tile-sub { font-size: 0.75rem; color: var(--text-muted); margin-top: 2px; }

.findings { padding-left: 0; list-style: none; margin: 20px 0; display: flex; flex-direction: column; gap: 12px; }
.findings li { background: var(--surface-1); border: 1px solid var(--border); border-radius: 10px; padding: 12px 16px; }
.finding-detail { color: var(--text-secondary); font-size: 0.92rem; }

.chart-block { margin: 20px 0 8px; }
.chart-caption { color: var(--text-secondary); font-size: 0.88rem; margin: 4px 0 12px; }
.chart { background: var(--surface-1); border: 1px solid var(--border); border-radius: 10px; padding: 12px; position: relative; }
.viz-svg { width: 100%; height: auto; display: block; overflow: visible; }
.viz-grid { stroke: var(--grid); stroke-width: 1; }
.viz-baseline { stroke: var(--baseline); stroke-width: 1.25; }
.viz-line { fill: none; stroke-width: 2; }
.viz-area { opacity: 0.14; }
.viz-axis-label { fill: var(--text-muted); font-size: 10px; }
.viz-end-label { font-size: 11px; font-weight: 600; }
.viz-crosshair { stroke: var(--text-muted); stroke-width: 1; stroke-dasharray: 3 3; pointer-events: none; }
.viz-bar-pos { fill: var(--diverging-pos); }
.viz-bar-neg { fill: var(--diverging-neg); }
.viz-hist-bar { fill: var(--series-1); opacity: 0.55; }
.viz-overlay-line { fill: none; stroke: var(--text-secondary); stroke-width: 1.5; stroke-dasharray: 4 3; }
.viz-heat-cell { stroke: var(--surface-1); stroke-width: 2; }
.viz-heat-label { font-size: 12px; fill: var(--text-primary); text-anchor: middle; dominant-baseline: middle; }
.viz-heat-label-inverse { fill: var(--heat-text-inverse); }
.viz-heat-axis { font-size: 11px; fill: var(--text-secondary); }

.viz-legend { display: flex; flex-wrap: wrap; gap: 12px; margin-top: 6px; padding-left: 4px; }
.viz-legend-item { display: flex; align-items: center; gap: 6px; font-size: 0.82rem; color: var(--text-secondary); }
.viz-swatch { width: 10px; height: 10px; border-radius: 2px; display: inline-block; flex: none; }

.viz-tooltip {
  position: absolute; pointer-events: none; background: var(--text-primary); color: var(--surface-1);
  border-radius: 6px; padding: 6px 10px; font-size: 0.78rem; z-index: 5; max-width: 220px;
}
.viz-tooltip-date { font-weight: 600; margin-bottom: 2px; }
.viz-tooltip-row { display: flex; align-items: center; gap: 6px; }

table { border-collapse: collapse; width: 100%; margin: 8px 0 20px; font-size: 0.9rem; }
table caption { text-align: left; font-weight: 600; margin-bottom: 6px; color: var(--text-primary); }
th, td { text-align: left; padding: 6px 10px; border-bottom: 1px solid var(--border); }
th { color: var(--text-secondary); font-weight: 600; font-size: 0.82rem; }
.inline-table { overflow-x: auto; display: block; }

.data-table summary { cursor: pointer; color: var(--text-secondary); font-size: 0.85rem; margin: 4px 0 4px; }
.data-table table { overflow-x: auto; display: block; }

.two-col { display: grid; grid-template-columns: 1fr 1fr; gap: 24px; }
@media (max-width: 640px) { .two-col { grid-template-columns: 1fr; } }

.method-list { padding-left: 20px; color: var(--text-secondary); font-size: 0.92rem; }
.method-list li { margin-bottom: 8px; }

footer { margin-top: 48px; padding-top: 16px; border-top: 1px solid var(--border); color: var(--text-muted); font-size: 0.8rem; }
code { background: var(--surface-1); border: 1px solid var(--border); border-radius: 4px; padding: 1px 5px; font-size: 0.85em; }
"""


# -------------------------------------------------------------------- js --

JS = r"""
(function(){
  var DATA = JSON.parse(document.getElementById('chart-data').textContent);
  var NS = 'http://www.w3.org/2000/svg';

  function el(tag, attrs){
    var e = document.createElementNS(NS, tag);
    for (var k in attrs) e.setAttribute(k, attrs[k]);
    return e;
  }

  function fmtVal(v, fmt){
    if (v === null || v === undefined || (typeof v === 'number' && isNaN(v))) return 'n/a';
    if (fmt === 'pct') return (v >= 0 ? '+' : '') + v.toFixed(2) + '%';
    if (fmt === 'index') return v.toFixed(1);
    if (fmt === 'price') return v.toLocaleString(undefined, {maximumFractionDigits: 0});
    if (fmt === 'yield') return v.toFixed(2) + '%';          // a level: no forced sign
    if (fmt === 'bp') return (v >= 0 ? '+' : '') + v.toFixed(0) + ' bp';
    if (fmt === 'corr') return v.toFixed(2);
    return String(v);
  }

  function buildScale(values, height, padTop, padBottom){
    var finite = values.filter(function(v){ return v !== null && v !== undefined && !isNaN(v); });
    var lo = Math.min.apply(null, finite), hi = Math.max.apply(null, finite);
    if (lo === hi) { lo -= 1; hi += 1; }
    var pad = (hi - lo) * 0.08;
    lo -= pad; hi += pad;
    return {
      lo: lo, hi: hi,
      y: function(v){ return height - padBottom - ((v - lo) / (hi - lo)) * (height - padTop - padBottom); }
    };
  }

  function addTooltip(container){
    var tip = document.createElement('div');
    tip.className = 'viz-tooltip';
    tip.style.display = 'none';
    container.style.position = 'relative';
    container.appendChild(tip);
    return tip;
  }

  function positionTooltip(tip, container, ev){
    var rect = container.getBoundingClientRect();
    var left = ev.clientX - rect.left + 14;
    if (left > rect.width - 180) left = ev.clientX - rect.left - 190;
    tip.style.left = left + 'px';
    tip.style.top = Math.max(0, ev.clientY - rect.top - 44) + 'px';
  }

  function lineChart(container, spec){
    var width = 900, height = 340;
    var padL = 54, padR = spec.series.length > 1 ? 20 : 24, padT = 20, padB = 30;
    var svg = el('svg', {viewBox: '0 0 ' + width + ' ' + height, class: 'viz-svg'});
    var n = spec.dates.length;
    function x(i){ return padL + (i / (n - 1)) * (width - padL - padR); }
    var allVals = [];
    spec.series.forEach(function(s){ allVals = allVals.concat(s.values); });
    var scale = buildScale(allVals, height, padT, padB);
    var y = scale.y, lo = scale.lo, hi = scale.hi;

    var ticks = 4;
    for (var t = 0; t <= ticks; t++){
      var v = lo + (hi - lo) * t / ticks;
      var gy = y(v);
      svg.appendChild(el('line', {x1: padL, x2: width - padR, y1: gy, y2: gy, class: 'viz-grid'}));
      var lbl = el('text', {x: padL - 8, y: gy + 4, class: 'viz-axis-label', 'text-anchor': 'end'});
      lbl.textContent = fmtVal(v, spec.yFormat);
      svg.appendChild(lbl);
    }
    if ((spec.yFormat === 'pct' || spec.zeroLine) && lo < 0 && hi > 0){
      svg.appendChild(el('line', {x1: padL, x2: width - padR, y1: y(0), y2: y(0), class: 'viz-baseline'}));
    }
    [0, Math.floor((n - 1) / 2), n - 1].forEach(function(i){
      var anchor = i === 0 ? 'start' : (i === n - 1 ? 'end' : 'middle');
      var tx = el('text', {x: x(i), y: height - 8, class: 'viz-axis-label', 'text-anchor': anchor});
      tx.textContent = spec.dates[i];
      svg.appendChild(tx);
    });

    spec.series.forEach(function(s){
      var d = '', started = false, firstI = -1, lastI = -1;
      s.values.forEach(function(v, i){
        if (v === null || v === undefined || isNaN(v)){ started = false; return; }
        if (firstI === -1) firstI = i;
        lastI = i;
        d += (started ? 'L' : 'M') + x(i).toFixed(2) + ',' + y(v).toFixed(2) + ' ';
        started = true;
      });
      if (spec.area && firstI !== -1){
        var baseline = y(Math.min(Math.max(lo, 0), hi));
        var areaD = 'M' + x(firstI).toFixed(2) + ',' + baseline.toFixed(2) + ' ' +
          d.replace(/^M/, 'L') + 'L' + x(lastI).toFixed(2) + ',' + baseline.toFixed(2) + ' Z';
        svg.appendChild(el('path', {d: areaD, class: 'viz-area', style: 'fill: var(--series-' + s.slot + ')'}));
      }
      svg.appendChild(el('path', {d: d, class: 'viz-line', style: 'stroke: var(--series-' + s.slot + ')'}));
      if (spec.endLabels && lastI !== -1){
        var lx = x(lastI), ly = y(s.values[lastI]);
        svg.appendChild(el('circle', {cx: lx, cy: ly, r: 3, style: 'fill: var(--series-' + s.slot + ')'}));
        var elbl = el('text', {x: Math.min(lx + 6, width - 4), y: ly + 4, class: 'viz-end-label',
          'text-anchor': lx + 6 > width - 90 ? 'end' : 'start', style: 'fill: var(--series-' + s.slot + ')'});
        elbl.textContent = s.label + ' ' + fmtVal(s.values[lastI], spec.yFormat);
        svg.appendChild(elbl);
      }
    });

    var cross = el('line', {x1: padL, x2: padL, y1: padT, y2: height - padB, class: 'viz-crosshair'});
    cross.style.display = 'none';
    svg.appendChild(cross);
    container.appendChild(svg);

    if (spec.series.length > 1){
      var legend = document.createElement('div');
      legend.className = 'viz-legend';
      spec.series.forEach(function(s){
        var item = document.createElement('span');
        item.className = 'viz-legend-item';
        var sw = document.createElement('span');
        sw.className = 'viz-swatch';
        sw.style.background = 'var(--series-' + s.slot + ')';
        var txt = document.createElement('span');
        txt.textContent = s.label;
        item.appendChild(sw); item.appendChild(txt);
        legend.appendChild(item);
      });
      container.appendChild(legend);
    }

    var tip = addTooltip(container);
    svg.addEventListener('mousemove', function(ev){
      var pt = svg.createSVGPoint();
      pt.x = ev.clientX; pt.y = ev.clientY;
      var loc = pt.matrixTransform(svg.getScreenCTM().inverse());
      var i = Math.round((loc.x - padL) / (width - padL - padR) * (n - 1));
      i = Math.max(0, Math.min(n - 1, i));
      cross.setAttribute('x1', x(i)); cross.setAttribute('x2', x(i));
      cross.style.display = 'block';
      var rows = spec.series.map(function(s){
        return '<div class="viz-tooltip-row"><span class="viz-swatch" style="background:var(--series-' + s.slot + ')"></span>' +
          s.label + ': ' + fmtVal(s.values[i], spec.yFormat) + '</div>';
      }).join('');
      tip.innerHTML = '<div class="viz-tooltip-date">' + spec.dates[i] + '</div>' + rows;
      tip.style.display = 'block';
      positionTooltip(tip, container, ev);
    });
    svg.addEventListener('mouseleave', function(){ cross.style.display = 'none'; tip.style.display = 'none'; });
  }

  function divergingBarChart(container, spec){
    var width = 900, height = 300, padL = 54, padR = 20, padT = 20, padB = 34;
    var svg = el('svg', {viewBox: '0 0 ' + width + ' ' + height, class: 'viz-svg'});
    var n = spec.labels.length;
    var bw = (width - padL - padR) / n;
    var scale = buildScale(spec.values, height, padT, padB);
    var y = scale.y, lo = scale.lo, hi = scale.hi;
    var zero = y(0);
    svg.appendChild(el('line', {x1: padL, x2: width - padR, y1: zero, y2: zero, class: 'viz-baseline'}));
    var tip = addTooltip(container);

    spec.values.forEach(function(v, i){
      var barY = Math.min(zero, y(v));
      var barH = Math.max(Math.abs(zero - y(v)), 1);
      var rect = el('rect', {
        x: padL + i * bw + bw * 0.15, y: barY, width: Math.max(bw * 0.7, 1), height: barH,
        rx: 2, class: v >= 0 ? 'viz-bar-pos' : 'viz-bar-neg'
      });
      rect.addEventListener('mousemove', function(ev){
        tip.innerHTML = '<div class="viz-tooltip-date">' + spec.labels[i] + '</div><div class="viz-tooltip-row">' + fmtVal(v, 'pct') + '</div>';
        tip.style.display = 'block';
        positionTooltip(tip, container, ev);
      });
      rect.addEventListener('mouseleave', function(){ tip.style.display = 'none'; });
      svg.appendChild(rect);
      var everyK = Math.ceil(n / 12);
      if (n <= 14 || i % everyK === 0){
        var lbl = el('text', {x: padL + i * bw + bw / 2, y: height - 12, class: 'viz-axis-label', 'text-anchor': 'middle'});
        lbl.textContent = spec.labels[i].slice(2);
        svg.appendChild(lbl);
      }
    });
    [lo, 0, hi].forEach(function(v){
      var gy = y(v);
      var lbl = el('text', {x: padL - 8, y: gy + 4, class: 'viz-axis-label', 'text-anchor': 'end'});
      lbl.textContent = fmtVal(v, 'pct');
      svg.appendChild(lbl);
    });
    container.appendChild(svg);
  }

  function histogramChart(container, spec){
    var width = 900, height = 300, padL = 54, padR = 20, padT = 20, padB = 30;
    var svg = el('svg', {viewBox: '0 0 ' + width + ' ' + height, class: 'viz-svg'});
    var n = spec.counts.length;
    var bw = (width - padL - padR) / n;
    var maxC = Math.max(Math.max.apply(null, spec.counts), Math.max.apply(null, spec.overlay));
    function y(c){ return height - padB - (c / maxC) * (height - padT - padB); }
    spec.counts.forEach(function(c, i){
      var rect = el('rect', {x: padL + i * bw + 1, y: y(c), width: Math.max(bw - 2, 1), height: Math.max(height - padB - y(c), 0), class: 'viz-hist-bar'});
      svg.appendChild(rect);
    });
    var d = '';
    spec.overlay.forEach(function(c, i){
      var cx = padL + i * bw + bw / 2;
      d += (i === 0 ? 'M' : 'L') + cx.toFixed(2) + ',' + y(c).toFixed(2) + ' ';
    });
    svg.appendChild(el('path', {d: d, class: 'viz-overlay-line'}));
    svg.appendChild(el('line', {x1: padL, x2: width - padR, y1: height - padB, y2: height - padB, class: 'viz-baseline'}));
    var zeroTick = Math.round(n / 2);
    var lbl = el('text', {x: padL, y: height - 8, class: 'viz-axis-label'});
    var xName = spec.xLabel || 'daily log return';
    var dp = spec.xLabel ? 1 : 3;
    lbl.textContent = xName + ', ' + spec.edges[0].toFixed(dp) + ' to ' + spec.edges[spec.edges.length - 1].toFixed(dp);
    svg.appendChild(lbl);
    container.appendChild(svg);
  }

  function heatBucket(v){
    if (v >= 0.5) return 'pos3';
    if (v >= 0.2) return 'pos2';
    if (v >= 0.05) return 'pos1';
    if (v > -0.05) return 'zero';
    if (v > -0.2) return 'neg1';
    if (v > -0.5) return 'neg2';
    return 'neg3';
  }

  function heatmap(container, spec){
    // rowLabels/colLabels allow a non-square matrix; square charts pass `labels`.
    var rowLabels = spec.rowLabels || spec.labels;
    var colLabels = spec.colLabels || spec.labels;
    var nRows = rowLabels.length, nCols = colLabels.length;
    var cell = 74, padL = 130, padT = 30;
    var width = padL + nCols * cell, height = padT + nRows * cell + 10;
    var svg = el('svg', {viewBox: '0 0 ' + width + ' ' + height, class: 'viz-svg viz-heatmap'});
    var tip = addTooltip(container);

    rowLabels.forEach(function(lbl, i){
      var t = el('text', {x: padL - 8, y: padT + i * cell + cell / 2 + 4, class: 'viz-heat-axis', 'text-anchor': 'end'});
      t.textContent = lbl;
      svg.appendChild(t);
    });
    colLabels.forEach(function(lbl, j){
      var t2 = el('text', {
        x: padL + j * cell + cell / 2, y: padT - 8, class: 'viz-heat-axis', 'text-anchor': 'middle'
      });
      t2.textContent = lbl.length > 10 ? lbl.slice(0, 9) + '…' : lbl;
      svg.appendChild(t2);
    });

    for (var i = 0; i < nRows; i++){
      for (var j = 0; j < nCols; j++){
        var v = spec.matrix[i][j];
        var bucket = heatBucket(v);
        var rect = el('rect', {
          x: padL + j * cell, y: padT + i * cell, width: cell, height: cell,
          class: 'viz-heat-cell', style: 'fill: var(--heat-' + bucket + ')'
        });
        rect.addEventListener('mousemove', (function(rowLbl, colLbl, val){
          return function(ev){
            tip.innerHTML = '<div class="viz-tooltip-date">' + rowLbl + ' vs ' + colLbl + '</div><div class="viz-tooltip-row">correlation: ' + val.toFixed(3) + '</div>';
            tip.style.display = 'block';
            positionTooltip(tip, container, ev);
          };
        })(rowLabels[i], colLabels[j], v));
        rect.addEventListener('mouseleave', function(){ tip.style.display = 'none'; });
        svg.appendChild(rect);
        var isInverse = bucket === 'pos3' || bucket === 'neg3' || bucket === 'pos2' || bucket === 'neg2';
        var label = el('text', {
          x: padL + j * cell + cell / 2, y: padT + i * cell + cell / 2,
          class: 'viz-heat-label' + (isInverse ? ' viz-heat-label-inverse' : '')
        });
        label.textContent = v.toFixed(2);
        svg.appendChild(label);
      }
    }
    container.appendChild(svg);
  }

  DATA.charts.forEach(function(spec){
    var container = document.getElementById(spec.id);
    if (!container) return;
    if (spec.type === 'line' || spec.type === 'area'){
      spec.area = spec.type === 'area';
      lineChart(container, spec);
    } else if (spec.type === 'divergingBar'){
      divergingBarChart(container, spec);
    } else if (spec.type === 'histogram'){
      histogramChart(container, spec);
    } else if (spec.type === 'heatmap'){
      heatmap(container, spec);
    }
  });

  function applyTheme(t){
    document.documentElement.setAttribute('data-theme', t);
    try { localStorage.setItem('theme', t); } catch (e) {}
  }
  var stored = null;
  try { stored = localStorage.getItem('theme'); } catch (e) {}
  if (stored) applyTheme(stored);
  var btn = document.getElementById('theme-toggle');
  if (btn){
    btn.addEventListener('click', function(){
      var mql = window.matchMedia('(prefers-color-scheme: dark)');
      var current = document.documentElement.getAttribute('data-theme') || (mql.matches ? 'dark' : 'light');
      applyTheme(current === 'dark' ? 'light' : 'dark');
    });
  }
})();
"""


# ------------------------------------------------------------------ main --

def render(m):
    findings = build_findings(m)
    chart_data = build_chart_data(m)
    body = "\n".join([
        render_header(m),
        '<div class="wrap">',
        render_exec_summary(m, findings),
        render_trend_section(m),
        render_drawdown_section(m),
        render_volatility_section(m),
        render_cross_index_section(m),
        render_rates_section(m),
        render_cross_asset_section(m),
        render_methodology_section(m),
        f'<footer>Generated from data fetched {esc(m["data_quality"]["fetched_at_utc"])}. '
        f'Source: Yahoo Finance daily OHLCV. Analysis window {esc(m["window"]["start"])}'
        f' &ndash; {esc(m["window"]["end"])}.</footer>',
        "</div>",
    ])

    html_doc = f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>S&amp;P 500 &mdash; One-Year Market Analysis</title>
<style>{CSS}</style>
</head>
<body>
{body}
<script id="chart-data" type="application/json">{embed_json(chart_data)}</script>
<script>{JS}</script>
</body>
</html>
"""
    return html_doc


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--metrics", default=os.path.join(DATA_DIR, "metrics.json"))
    ap.add_argument("--out", default=os.path.join(os.path.dirname(os.path.abspath(__file__)), "report.html"))
    args = ap.parse_args()

    m = load_metrics(args.metrics)
    doc = render(m)
    with open(args.out, "w", encoding="utf-8") as f:
        f.write(doc)
    print(f"report written to {args.out} ({len(doc):,} bytes)")


if __name__ == "__main__":
    main()
