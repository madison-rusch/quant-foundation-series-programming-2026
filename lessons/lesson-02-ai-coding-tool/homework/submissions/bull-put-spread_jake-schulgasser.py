"""Risk/reward analyzer for a bull put spread (short a higher-strike put,
long a lower-strike put — a net-credit, defined-risk bullish position).

Conventions:
    - money regime: float64 analytics. These are trade-planning quantities, not
      settlement amounts. Use decimal.Decimal at the cash boundary if you need
      exact ledger rounding. Rounding here happens only at display.
    - per share vs position: strikes, premiums and breakeven are PER SHARE.
      P&L, max profit, max loss and collateral are POSITION level, i.e. scaled
      by (contracts * multiplier). Every label says which.
    - "lot size" is the number of CONTRACTS; --multiplier is shares per
      contract (100 for standard US equity options). They are different things.
    - P&L is AT EXPIRY, intrinsic value only. The credit is not discounted and
      no pre-expiry time value is modelled.
    - premiums are marked at the bid/ask MID by default; the natural (worst
      case) fill is reported alongside so assumed edge is visible.
    - implied vol (--iv) is DIAGNOSTIC ONLY. It is never used to price the
      legs; it only powers the optional probability block.

Example:
    python bull_put_spread.py --spot 100 --short-strike 95 --long-strike 90 \\
        --short-bid 1.90 --short-ask 2.10 --long-bid 0.40 --long-ask 0.60 \\
        --expiry 2026-09-18 --contracts 3 --iv 0.28
"""

from __future__ import annotations

import argparse
import math
from dataclasses import dataclass
from datetime import date
from pathlib import Path

import numpy as np

DAYS_PER_YEAR = 365.0  # calendar-day basis for DTE and annualization
WIDE_QUOTE_FRAC = 0.10  # bid-ask > 10% of mid is a "you won't fill at mid" flag
THIN_CREDIT_FRAC = 0.05  # credit < 5% of width is a poor risk/reward flag
NEAR_EXPIRY_DAYS = 7  # DTE at/below which the far-OTM lottery check fires
FAR_OTM_FRAC = 0.08  # short strike > 8% OTM counts as "far"
GAMMA_RISK_DAYS = 2  # DTE at/below which expiry-only modelling is least useful
MIN_DTE_FOR_ANNUALIZING = 5  # below this, annualized return-on-risk is noise
SLIPPAGE_WARN_FRAC = 0.25  # bid-ask eating >25% of max profit is a flag
GRID_POINTS = 41  # payoff table resolution before pinned strikes are added


# --------------------------------------------------------------------------
# Inputs
# --------------------------------------------------------------------------


@dataclass(frozen=True)
class LegQuote:
    """One option leg's market, per share.

    Either a two-sided quote (``bid``/``ask``) or a single known ``price``.
    ``mid`` is the mark used for headline metrics; ``bid``/``ask`` drive the
    fill-band and liquidity diagnostics.
    """

    name: str
    bid: float
    ask: float
    is_two_sided: bool

    @classmethod
    def from_args(
        cls,
        *,
        name: str,
        bid: float | None,
        ask: float | None,
        price: float | None,
    ) -> LegQuote:
        """Build a leg from CLI args, enforcing the either/or input rule."""
        has_quote = bid is not None or ask is not None
        if price is not None and has_quote:
            raise ValueError(
                f"{name} leg: give either --{name}-bid/--{name}-ask or "
                f"--{name}-price, not both"
            )
        if price is not None:
            if not math.isfinite(price):
                raise ValueError(f"{name} leg: price must be a finite number")
            if price <= 0:
                raise ValueError(f"{name} leg: price must be > 0, got {price}")
            return cls(name=name, bid=price, ask=price, is_two_sided=False)

        if bid is None or ask is None:
            raise ValueError(
                f"{name} leg: supply both --{name}-bid and --{name}-ask "
                f"(or a single --{name}-price)"
            )
        if not (math.isfinite(bid) and math.isfinite(ask)):
            raise ValueError(f"{name} leg: bid/ask must be finite numbers")
        if bid < 0:
            raise ValueError(f"{name} leg: bid must be >= 0, got {bid}")
        if ask <= 0:
            raise ValueError(f"{name} leg: ask must be > 0, got {ask}")
        if bid > ask:
            raise ValueError(
                f"{name} leg: crossed quote, bid {bid} > ask {ask}; the data is wrong"
            )
        return cls(name=name, bid=float(bid), ask=float(ask), is_two_sided=True)

    @property
    def mid(self) -> float:
        """Mid price per share."""
        return 0.5 * (self.bid + self.ask)

    @property
    def spread_frac(self) -> float:
        """Bid-ask width as a fraction of mid (0.0 for a single known price)."""
        return (self.ask - self.bid) / self.mid if self.mid > 0 else math.inf

# The following class confirms valid inputs for a bull put spread. This is important because it ensures that the calculations will be feasible and enactable for a bull put spread
@dataclass(frozen=True)
class SpreadInputs:
    """A fully specified bull put spread. Validated on construction."""

    spot: float
    short_strike: float
    long_strike: float
    short_leg: LegQuote
    long_leg: LegQuote
    expiry: date
    valuation_date: date
    contracts: int = 1
    multiplier: int = 100
    fees: float = 0.0

    def __post_init__(self) -> None:
        for label, value in (
            ("spot", self.spot),
            ("short_strike", self.short_strike),
            ("long_strike", self.long_strike),
        ):
            if not math.isfinite(value):
                raise ValueError(f"{label} must be a finite number, got {value}")
            if value <= 0:
                raise ValueError(f"{label} must be > 0, got {value}")
        if self.short_strike <= self.long_strike:
            raise ValueError(
                f"short_strike ({self.short_strike}) must be above long_strike "
                f"({self.long_strike}); a bull put spread sells the higher strike"
            )
        if self.contracts < 1:
            raise ValueError(f"contracts must be >= 1, got {self.contracts}")
        if self.multiplier < 1:
            raise ValueError(f"multiplier must be >= 1, got {self.multiplier}")
        if not math.isfinite(self.fees) or self.fees < 0:
            raise ValueError(f"fees must be a finite number >= 0, got {self.fees}")
        if self.expiry < self.valuation_date:
            raise ValueError(
                f"expiry {self.expiry} is before valuation date {self.valuation_date}"
            )
        if self.net_credit <= 0:
            raise ValueError(
                f"net credit at mid is {self.net_credit:+.4f} per share -- this is a "
                f"debit spread, not a bull put spread. Check that the short leg is "
                f"the higher strike and that the quotes are not stale."
            )
        if self.net_credit * self.position_size <= self.fees:
            raise ValueError(
                f"fees ({self.fees:.2f}) meet or exceed the entire credit "
                f"({self.net_credit * self.position_size:.2f}); the trade cannot "
                f"make money under any outcome"
            )

    @property
    def position_size(self) -> int:
        """Shares controlled: contracts * multiplier."""
        return self.contracts * self.multiplier

    @property
    def width(self) -> float:
        """Strike width, per share."""
        return self.short_strike - self.long_strike

    @property
    def net_credit(self) -> float:
        """Credit received per share, marked at the mid."""
        return self.short_leg.mid - self.long_leg.mid

    @property
    def credit_at_natural(self) -> float:
        """Credit per share on a worst-case fill: hit the bid, lift the ask."""
        return self.short_leg.bid - self.long_leg.ask

    @property
    def credit_at_best(self) -> float:
        """Credit per share on an unrealistically good fill. Upper bound only."""
        return self.short_leg.ask - self.long_leg.bid

    @property
    def days_to_expiry(self) -> int:
        """Calendar days from valuation date to expiry."""
        return (self.expiry - self.valuation_date).days

    @property
    def years_to_expiry(self) -> float:
        """Calendar-day year fraction to expiry."""
        return self.days_to_expiry / DAYS_PER_YEAR


# --------------------------------------------------------------------------
# Metrics
# --------------------------------------------------------------------------


def expiry_pnl(
    spot_at_expiry: np.ndarray | float,
    inputs: SpreadInputs,
    *,
    credit: float | None = None,
) -> np.ndarray | float:
    """Position P&L at expiry, vectorized over terminal spot.

    Args:
        spot_at_expiry: underlying price(s) at expiry.
        inputs: the spread.
        credit: credit per share to assume; defaults to the mid. Pass
            ``inputs.credit_at_natural`` to see the worst-case fill.

    Returns:
        Position-level P&L in dollars, net of fees. Same shape as the input
        (a float for scalar input).
    """
    net_credit = inputs.net_credit if credit is None else credit
    s_t = np.asarray(spot_at_expiry, dtype=np.float64)
    if np.isnan(s_t).any():
        raise ValueError("expiry_pnl received NaN in spot_at_expiry")

    short_payout = np.maximum(inputs.short_strike - s_t, 0.0)
    long_payout = np.maximum(inputs.long_strike - s_t, 0.0)
    pnl = (net_credit - short_payout + long_payout) * inputs.position_size - inputs.fees
    return float(pnl) if pnl.ndim == 0 else pnl


def spread_metrics(inputs: SpreadInputs) -> dict[str, float]:
    """All scalar risk/reward metrics, at the mid and at the natural fill.

    Money values are position level; ``breakeven`` and ``*_per_share`` are per
    share. ``annualized_return_on_risk`` is NaN when DTE is too small for the
    figure to mean anything (see MIN_DTE_FOR_ANNUALIZING).
    """
    size = inputs.position_size
    credit = inputs.net_credit
    natural = inputs.credit_at_natural

    max_profit = credit * size - inputs.fees
    max_loss = (inputs.width - credit) * size + inputs.fees
    collateral = inputs.width * size

    max_profit_natural = natural * size - inputs.fees
    max_loss_natural = (inputs.width - natural) * size + inputs.fees

    return_on_risk = max_profit / max_loss
    dte = inputs.days_to_expiry
    annualized = (
        return_on_risk * DAYS_PER_YEAR / dte
        if dte >= MIN_DTE_FOR_ANNUALIZING
        else math.nan
    )

    return {
        "net_credit_per_share": credit,
        "credit_natural_per_share": natural,
        "credit_best_per_share": inputs.credit_at_best,
        "width_per_share": inputs.width,
        "breakeven": inputs.short_strike - credit,
        "breakeven_natural": inputs.short_strike - natural,
        "max_profit": max_profit,
        "max_loss": max_loss,
        "max_profit_natural": max_profit_natural,
        "max_loss_natural": max_loss_natural,
        "slippage_cost": (credit - natural) * size,
        "collateral": collateral,
        "credit_to_width": credit / inputs.width,
        "return_on_risk": return_on_risk,
        "return_on_collateral": max_profit / collateral,
        "annualized_return_on_risk": annualized,
        "days_to_expiry": float(dte),
    }


def move_to_levels(inputs: SpreadInputs, metrics: dict[str, float]) -> dict[str, object]:
    """How far spot must move to reach breakeven, max profit and max loss.

    Distances are signed from the current spot: positive means the stock must
    RISE, negative means it may FALL that far before reaching the level.
    """

    def leg(level: float) -> dict[str, float | str]:
        move = level - inputs.spot
        return {
            "level": level,
            "move": move,
            "move_pct": move / inputs.spot,
            "direction": "rise" if move > 0 else ("fall" if move < 0 else "no move"),
        }

    breakeven = metrics["breakeven"]
    dte = inputs.days_to_expiry

    if inputs.spot >= inputs.short_strike:
        regime = "both legs OTM"
        narrative = (
            f"Both legs are out of the money. Max profit is realized if the stock "
            f"simply does not fall below {inputs.short_strike:.2f} -- no upward move "
            f"is required. It can fall {inputs.spot - breakeven:.2f} "
            f"({(inputs.spot - breakeven) / inputs.spot:.2%}) before you lose money, "
            f"and {inputs.spot - inputs.long_strike:.2f} "
            f"({(inputs.spot - inputs.long_strike) / inputs.spot:.2%}) before max loss."
        )
    elif inputs.spot > inputs.long_strike:
        already = "already profitable" if inputs.spot > breakeven else "below breakeven"
        to_be = (
            f"It is {already} at the current spot"
            if inputs.spot > breakeven
            else f"It must rise {breakeven - inputs.spot:.2f} "
            f"({(breakeven - inputs.spot) / inputs.spot:.2%}) just to break even"
        )
        regime = "short put ITM at entry"
        narrative = (
            f"The short put is already in the money. The stock must RISE "
            f"{inputs.short_strike - inputs.spot:.2f} "
            f"({(inputs.short_strike - inputs.spot) / inputs.spot:.2%}) to reach max "
            f"profit. {to_be}."
        )
    else:
        regime = "both legs ITM"
        narrative = (
            f"Both legs are in the money -- this position sits at MAX LOSS if the "
            f"stock does not move. It must rise {breakeven - inputs.spot:.2f} "
            f"({(breakeven - inputs.spot) / inputs.spot:.2%}) to break even and "
            f"{inputs.short_strike - inputs.spot:.2f} "
            f"({(inputs.short_strike - inputs.spot) / inputs.spot:.2%}) to reach "
            f"max profit -- the largest move this structure can require."
        )

    # Linear reference only: the per-day move that would carry spot to breakeven
    # in a straight line. Not a forecast, and not a drift assumption.
    pct_to_breakeven = abs(breakeven - inputs.spot) / inputs.spot
    per_day = pct_to_breakeven / dte if dte > 0 else math.nan

    return {
        "regime": regime,
        "narrative": narrative,
        "breakeven": leg(breakeven),
        "max_profit_level": leg(inputs.short_strike),
        "max_loss_level": leg(inputs.long_strike),
        "pct_to_breakeven_per_day": per_day,
    }


# --------------------------------------------------------------------------
# Optional probability diagnostics
# --------------------------------------------------------------------------


def _norm_cdf(x: float) -> float:
    """Standard normal CDF via erf — avoids a hard scipy dependency."""
    return 0.5 * (1.0 + math.erf(x / math.sqrt(2.0)))


def probability_metrics(
    inputs: SpreadInputs, metrics: dict[str, float], iv: float
) -> dict[str, float]:
    """Outcome probabilities under a zero-drift lognormal terminal distribution.

    Assumes ``ln(S_T) ~ N(ln(S) - 0.5*iv^2*T, iv^2*T)``, i.e. r = q = 0 and
    E[S_T] = S. This is an approximation for orientation, NOT a forecast: it
    ignores drift, skew, and the fact that a single IV cannot describe both
    strikes of a real skewed surface.

    Args:
        iv: annualized implied vol as a decimal (0.30 == 30%).
    """
    if not math.isfinite(iv) or iv <= 0:
        raise ValueError(f"iv must be a finite number > 0, got {iv}")
    t = inputs.years_to_expiry
    if t <= 0:
        raise ValueError("probability metrics need days_to_expiry > 0")

    sigma_t = iv * math.sqrt(t)
    spot = inputs.spot

    def d2(strike: float) -> float:
        return (math.log(spot / strike) - 0.5 * sigma_t**2) / sigma_t

    def d1(strike: float) -> float:
        return d2(strike) + sigma_t

    def expected_put_payout(strike: float) -> float:
        """E[max(K - S_T, 0)] — Black-Scholes put with r = 0."""
        return strike * _norm_cdf(-d2(strike)) - spot * _norm_cdf(-d1(strike))

    expected_pnl = (
        inputs.net_credit
        - expected_put_payout(inputs.short_strike)
        + expected_put_payout(inputs.long_strike)
    ) * inputs.position_size - inputs.fees

    return {
        "one_sigma_move": spot * sigma_t,
        "one_sigma_move_pct": sigma_t,
        "prob_max_profit": _norm_cdf(d2(inputs.short_strike)),
        "prob_profit": _norm_cdf(d2(metrics["breakeven"])),
        "prob_max_loss": _norm_cdf(-d2(inputs.long_strike)),
        "expected_pnl": expected_pnl,
    }


# --------------------------------------------------------------------------
# Edge-case warnings
# --------------------------------------------------------------------------

# The following function informs the user if the provided bull put spread data would not make sense given the fees or spread width. 
# This is important in a real world trading scenario because these trades may be possible in academia, but would likely fail to be profitable in actuality.

def collect_warnings(inputs: SpreadInputs, metrics: dict[str, float]) -> list[str]:
    """Structural problems that do not invalidate the math but should stop you.

    Returned as strings so they are testable without capturing stdout.
    """
    warnings: list[str] = []
    dte = inputs.days_to_expiry
    credit = inputs.net_credit

    if metrics["credit_to_width"] < THIN_CREDIT_FRAC:
        warnings.append(
            f"Thin credit: collecting only {metrics['credit_to_width']:.1%} of the "
            f"{inputs.width:.2f}-wide spread -- risking "
            f"${metrics['max_loss']:,.2f} to make ${metrics['max_profit']:,.2f}."
        )

    if dte == 0:
        warnings.append(
            "Expires today: every move below is required immediately, and the "
            "per-day and annualized figures are omitted as meaningless."
        )
    elif dte <= GAMMA_RISK_DAYS:
        warnings.append(
            f"Only {dte} day(s) to expiry: gamma and assignment risk dominate, and "
            f"an expiry-only P&L model is least informative in this regime."
        )

    if inputs.spot > inputs.short_strike:
        otm_frac = (inputs.spot - inputs.short_strike) / inputs.spot
        if dte <= NEAR_EXPIRY_DAYS and otm_frac > FAR_OTM_FRAC:
            equivalent = (
                otm_frac * math.sqrt(DAYS_PER_YEAR / dte) if dte > 0 else math.inf
            )
            warnings.append(
                f"Far OTM into a near expiry: the short strike is {otm_frac:.1%} below "
                f"spot with {dte} day(s) left. Reaching it would take a move "
                f"equivalent to roughly {equivalent:.0%} annualized volatility -- the "
                f"credit is small because the market thinks this is very unlikely, "
                f"and the payoff is correspondingly lopsided."
            )

    for leg in (inputs.short_leg, inputs.long_leg):
        if leg.is_two_sided and leg.spread_frac > WIDE_QUOTE_FRAC:
            warnings.append(
                f"Wide market on the {leg.name} leg: {leg.bid:.2f} / {leg.ask:.2f} is "
                f"{leg.spread_frac:.1%} of mid. You are unlikely to fill at the mid; "
                f"treat the natural-fill column as the realistic case."
            )
        if leg.is_two_sided and leg.bid <= 0:
            warnings.append(
                f"No bid on the {leg.name} leg: you may be unable to close this "
                f"position before expiry."
            )

    if metrics["slippage_cost"] > SLIPPAGE_WARN_FRAC * metrics["max_profit"]:
        warnings.append(
            f"Bid-ask alone costs ${metrics['slippage_cost']:,.2f}, which is "
            f"{metrics['slippage_cost'] / metrics['max_profit']:.0%} of max profit at "
            f"the mid."
        )

    if credit >= inputs.width:
        warnings.append(
            f"Credit ({credit:.2f}) is at or above the spread width "
            f"({inputs.width:.2f}). That implies a riskless profit and is almost "
            f"always a stale or mis-keyed quote."
        )

    short_intrinsic = max(inputs.short_strike - inputs.spot, 0.0)
    if inputs.short_leg.mid < short_intrinsic:
        warnings.append(
            f"Short leg mid ({inputs.short_leg.mid:.2f}) is below its intrinsic value "
            f"({short_intrinsic:.2f}) -- the quote is stale or the spot is wrong."
        )

    if inputs.spot <= inputs.long_strike:
        warnings.append(
            "Both legs are in the money at entry: this position is at max loss right "
            "now and needs a rally just to break even."
        )

    return warnings


# --------------------------------------------------------------------------
# Presentation
# --------------------------------------------------------------------------


def payoff_grid(inputs: SpreadInputs, metrics: dict[str, float]) -> np.ndarray:
    """Terminal spot grid for the payoff table, with the kink points pinned in."""
    low = min(inputs.long_strike, inputs.spot) * 0.9
    high = max(inputs.short_strike, inputs.spot) * 1.1
    pinned = [
        inputs.long_strike,
        metrics["breakeven"],
        inputs.short_strike,
        inputs.spot,
    ]
    return np.unique(
        np.concatenate([np.linspace(low, high, GRID_POINTS), np.array(pinned)])
    )


def _money(value: float) -> str:
    return f"${value:,.2f}"


def format_report(
    inputs: SpreadInputs,
    metrics: dict[str, float],
    moves: dict[str, object],
    warnings: list[str],
    probabilities: dict[str, float] | None,
) -> str:
    """Render the full console report. Returns a string; does not print."""
    lines: list[str] = []
    dte = inputs.days_to_expiry

    if warnings:
        lines.append("=" * 78)
        lines.append(f"!! WARNINGS ({len(warnings)})")
        lines.append("=" * 78)
        for note in warnings:
            lines.append(f"  - {note}")
        lines.append("")

    lines.append("=" * 78)
    lines.append("BULL PUT SPREAD")
    lines.append("=" * 78)
    lines.append("")

    lines.append("POSITION")
    lines.append(f"  Underlying spot        {inputs.spot:,.2f}")
    lines.append(
        f"  Short put (sell)       {inputs.short_strike:,.2f} strike   "
        f"{_quote_str(inputs.short_leg)}"
    )
    lines.append(
        f"  Long put (buy)         {inputs.long_strike:,.2f} strike   "
        f"{_quote_str(inputs.long_leg)}"
    )
    lines.append(f"  Spread width           {inputs.width:,.2f} per share")
    lines.append(
        f"  Size                   {inputs.contracts} contract(s) x "
        f"{inputs.multiplier} = {inputs.position_size:,} shares"
    )
    lines.append(f"  Fees                   {_money(inputs.fees)} (position, total)")
    lines.append(
        f"  Expiry                 {inputs.expiry.isoformat()}  "
        f"({dte} calendar day(s) from {inputs.valuation_date.isoformat()})"
    )
    lines.append("")

    lines.append("FILL BAND (per share)")
    lines.append(
        f"  Natural (worst)        {metrics['credit_natural_per_share']:,.2f}   "
        f"sell the bid, pay the ask"
    )
    lines.append(f"  Mid (headline)         {metrics['net_credit_per_share']:,.2f}")
    lines.append(
        f"  Best (unrealistic)     {metrics['credit_best_per_share']:,.2f}"
    )
    lines.append(
        f"  Cost of crossing       {_money(metrics['slippage_cost'])} "
        f"(mid vs natural, position)"
    )
    lines.append("")

    lines.append("RISK / REWARD                     at mid          at natural fill")
    lines.append(
        f"  Max profit             {_money(metrics['max_profit']):>15}  "
        f"{_money(metrics['max_profit_natural']):>15}"
    )
    lines.append(
        f"  Max loss               {_money(-metrics['max_loss']):>15}  "
        f"{_money(-metrics['max_loss_natural']):>15}"
    )
    lines.append(
        f"  Breakeven (per share)  {metrics['breakeven']:>15,.2f}  "
        f"{metrics['breakeven_natural']:>15,.2f}"
    )
    lines.append("")
    lines.append(f"  Collateral required    {_money(metrics['collateral'])}")
    lines.append(
        f"  Credit / width         {metrics['credit_to_width']:.1%} of the spread"
    )
    lines.append(
        f"  Return on risk         {metrics['return_on_risk']:.2%} "
        f"(max profit / max loss)"
    )
    lines.append(
        f"  Return on collateral   {metrics['return_on_collateral']:.2%}"
    )
    if math.isnan(metrics["annualized_return_on_risk"]):
        lines.append(
            f"  Annualized RoR         n/a (only {dte} day(s) to expiry; "
            f"annualizing would be noise)"
        )
    else:
        lines.append(
            f"  Annualized RoR         {metrics['annualized_return_on_risk']:.2%} "
            f"(simple scaling, indicative only)"
        )
    lines.append("")

    lines.append(f"MOVE REQUIRED  [{moves['regime']}]")
    lines.append(f"  {moves['narrative']}")
    lines.append("")
    lines.append(
        f"  {'Level':<26}{'Price':>10}{'Move':>12}{'Move %':>12}  Direction"
    )
    for label, key in (
        ("Breakeven", "breakeven"),
        ("Max profit (short strike)", "max_profit_level"),
        ("Max loss (long strike)", "max_loss_level"),
    ):
        item = moves[key]
        assert isinstance(item, dict)
        lines.append(
            f"  {label:<26}{item['level']:>10,.2f}{item['move']:>+12,.2f}"
            f"{item['move_pct']:>+12.2%}  {item['direction']}"
        )
    per_day = moves["pct_to_breakeven_per_day"]
    assert isinstance(per_day, float)
    if not math.isnan(per_day):
        lines.append("")
        lines.append(
            f"  Straight-line move to breakeven: {per_day:.3%} per day over {dte} "
            f"day(s) (linear reference, not a forecast)."
        )
    lines.append("")

    lines.append("STATISTICAL CONTEXT")
    if probabilities is None:
        lines.append(
            "  Not computed. Probabilities require a volatility input; pass --iv "
            "<annualized decimal, e.g. 0.28> to enable this block. It is used only "
            "here, never to price the legs."
        )
    else:
        lines.append(
            f"  1-sigma move to expiry  {probabilities['one_sigma_move']:,.2f} "
            f"({probabilities['one_sigma_move_pct']:.2%})"
        )
        lines.append(
            f"  P(max profit)           {probabilities['prob_max_profit']:.2%}  "
            f"spot >= {inputs.short_strike:,.2f}"
        )
        lines.append(
            f"  P(any profit)           {probabilities['prob_profit']:.2%}  "
            f"spot >= {metrics['breakeven']:,.2f}"
        )
        lines.append(
            f"  P(max loss)             {probabilities['prob_max_loss']:.2%}  "
            f"spot <= {inputs.long_strike:,.2f}"
        )
        lines.append(
            f"  Expected P&L            {_money(probabilities['expected_pnl'])}"
        )
        lines.append(
            "  Zero-drift lognormal (r = q = 0), single IV across both strikes. "
            "An orientation figure, not a forecast."
        )
    lines.append("")

    lines.append("PAYOFF AT EXPIRY (position, at the mid)")
    lines.append(f"  {'Spot':>10}{'P&L':>16}{'% of max':>12}   Note")
    grid = payoff_grid(inputs, metrics)
    pnl = expiry_pnl(grid, inputs)
    assert isinstance(pnl, np.ndarray)
    for spot_t, value in zip(grid, pnl):
        note = _pin_label(spot_t, inputs, metrics)
        lines.append(
            f"  {spot_t:>10,.2f}{value:>+16,.2f}"
            f"{value / metrics['max_profit']:>12.0%}   {note}"
        )
    lines.append("")

    lines.append("ASSUMPTIONS & RISKS NOT MODELLED")
    lines.append(
        "  - American exercise: the short put can be assigned early, most likely "
        "when it is deep ITM or around an ex-dividend date."
    )
    lines.append(
        f"  - Pin risk: if the underlying settles at exactly "
        f"{inputs.short_strike:,.2f} you will not know your assignment status until "
        f"after the close."
    )
    lines.append(
        "  - P&L is at expiry only. Before expiry the position is marked with time "
        "value and can show a loss well inside the breakeven."
    )
    lines.append("  - The credit is not discounted; interest on collateral is ignored.")
    lines.append(
        "  - Fills are assumed at the marks you supplied. Liquidity and price "
        "movement during execution are not modelled."
    )
    return "\n".join(lines)


def _quote_str(leg: LegQuote) -> str:
    if leg.is_two_sided:
        return f"{leg.bid:.2f} / {leg.ask:.2f}  mid {leg.mid:.2f}"
    return f"filled at {leg.mid:.2f}"


def _pin_label(spot_t: float, inputs: SpreadInputs, metrics: dict[str, float]) -> str:
    labels = []
    if math.isclose(spot_t, inputs.spot, rel_tol=1e-12):
        labels.append("spot today")
    if math.isclose(spot_t, metrics["breakeven"], rel_tol=1e-12):
        labels.append("breakeven")
    if math.isclose(spot_t, inputs.short_strike, rel_tol=1e-12):
        labels.append("short strike / max profit")
    if math.isclose(spot_t, inputs.long_strike, rel_tol=1e-12):
        labels.append("long strike / max loss")
    return ", ".join(labels)

# The followng function uses matplotlib to plot tthe actual diagram of the bull put spread so the user can see the payoffs at different prices at expiry.
# This is an important visualization for the user to understand the risk/reward at different price levels based on their belief of where the price of the
# underlying stock will go leading up to the expiry date.

def plot_payoff(
    inputs: SpreadInputs, metrics: dict[str, float], path: Path
) -> None:
    """Save the expiry payoff diagram as a PNG. Imports matplotlib lazily."""
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    grid = np.linspace(
        min(inputs.long_strike, inputs.spot) * 0.9,
        max(inputs.short_strike, inputs.spot) * 1.1,
        400,
    )
    pnl = np.asarray(expiry_pnl(grid, inputs))

    fig, ax = plt.subplots(figsize=(10, 6))
    ax.plot(grid, pnl, color="#1f77b4", linewidth=2, label="P&L at expiry")
    ax.fill_between(grid, pnl, 0, where=pnl >= 0, color="#2ca02c", alpha=0.18)
    ax.fill_between(grid, pnl, 0, where=pnl < 0, color="#d62728", alpha=0.18)
    ax.axhline(0.0, color="black", linewidth=0.8)

    for level, label, color in (
        (inputs.long_strike, f"long {inputs.long_strike:g}", "#d62728"),
        (metrics["breakeven"], f"breakeven {metrics['breakeven']:.2f}", "#ff7f0e"),
        (inputs.short_strike, f"short {inputs.short_strike:g}", "#2ca02c"),
        (inputs.spot, f"spot {inputs.spot:g}", "#555555"),
    ):
        ax.axvline(level, color=color, linestyle="--", linewidth=1, alpha=0.8)
        ax.annotate(
            label,
            xy=(level, ax.get_ylim()[1]),
            xytext=(2, -12),
            textcoords="offset points",
            rotation=90,
            fontsize=8,
            color=color,
            va="top",
        )

    ax.set_title(
        f"Bull put spread {inputs.long_strike:g}/{inputs.short_strike:g} "
        f"exp {inputs.expiry.isoformat()} x{inputs.contracts}"
    )
    ax.set_xlabel("Underlying price at expiry")
    ax.set_ylabel("Position P&L ($)")
    ax.grid(alpha=0.25)
    ax.legend(loc="upper left")
    fig.tight_layout()
    fig.savefig(path, dpi=140)
    plt.close(fig)


# --------------------------------------------------------------------------
# CLI
# --------------------------------------------------------------------------


def _parse_date(value: str) -> date:
    try:
        return date.fromisoformat(value)
    except ValueError as exc:
        raise argparse.ArgumentTypeError(
            f"expected a YYYY-MM-DD date, got {value!r}"
        ) from exc


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Analyze a bull put spread: risk, reward, and required move.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument("--spot", type=float, required=True, help="underlying price")
    parser.add_argument(
        "--short-strike", type=float, required=True, help="strike of the put you sell"
    )
    parser.add_argument(
        "--long-strike", type=float, required=True, help="strike of the put you buy"
    )
    parser.add_argument("--short-bid", type=float, help="bid on the short leg")
    parser.add_argument("--short-ask", type=float, help="ask on the short leg")
    parser.add_argument(
        "--short-price", type=float, help="known fill on the short leg (instead of bid/ask)"
    )
    parser.add_argument("--long-bid", type=float, help="bid on the long leg")
    parser.add_argument("--long-ask", type=float, help="ask on the long leg")
    parser.add_argument(
        "--long-price", type=float, help="known fill on the long leg (instead of bid/ask)"
    )
    parser.add_argument(
        "--expiry", type=_parse_date, required=True, help="expiry date, YYYY-MM-DD"
    )
    parser.add_argument(
        "--valuation-date", type=_parse_date, default=None, help="defaults to today"
    )
    parser.add_argument(
        "--contracts", type=int, default=1, help="lot size, number of contracts"
    )
    parser.add_argument(
        "--multiplier", type=int, default=100, help="shares per contract"
    )
    parser.add_argument(
        "--fees", type=float, default=0.0, help="total round-trip fees, position level"
    )
    parser.add_argument(
        "--iv",
        type=float,
        default=None,
        help="annualized implied vol as a decimal, for the probability block only",
    )
    parser.add_argument("--plot", type=Path, default=None, help="save payoff PNG here")
    parser.add_argument(
        "--strict", action="store_true", help="treat any warning as a fatal error"
    )
    return parser.parse_args(argv)


def build_inputs(args: argparse.Namespace) -> SpreadInputs:
    """Assemble validated SpreadInputs from parsed CLI arguments."""
    return SpreadInputs(
        spot=args.spot,
        short_strike=args.short_strike,
        long_strike=args.long_strike,
        short_leg=LegQuote.from_args(
            name="short", bid=args.short_bid, ask=args.short_ask, price=args.short_price
        ),
        long_leg=LegQuote.from_args(
            name="long", bid=args.long_bid, ask=args.long_ask, price=args.long_price
        ),
        expiry=args.expiry,
        valuation_date=args.valuation_date or date.today(),
        contracts=args.contracts,
        multiplier=args.multiplier,
        fees=args.fees,
    )


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    try:
        inputs = build_inputs(args)
    except ValueError as exc:
        print(f"error: {exc}")
        return 2

    metrics = spread_metrics(inputs)
    moves = move_to_levels(inputs, metrics)
    warnings = collect_warnings(inputs, metrics)

    if args.strict and warnings:
        print(f"error: --strict and {len(warnings)} warning(s):")
        for note in warnings:
            print(f"  - {note}")
        return 1

    probabilities = None
    if args.iv is not None:
        if inputs.days_to_expiry <= 0:
            print("note: --iv ignored, the option expires today")
        else:
            probabilities = probability_metrics(inputs, metrics, args.iv)

    print(format_report(inputs, metrics, moves, warnings, probabilities))

    if args.plot is not None:
        plot_payoff(inputs, metrics, args.plot)
        print(f"\npayoff chart written to {args.plot}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
