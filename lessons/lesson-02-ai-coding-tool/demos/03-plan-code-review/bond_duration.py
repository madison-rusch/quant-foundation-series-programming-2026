"""Macaulay duration demo — companion to bond_price.py."""


def bond_duration(
    face_value: float,
    coupon_rate: float,
    market_rate: float,
    years: int,
    coupons_per_year: int = 1,
) -> float:
    """Return the Macaulay duration of a bond in years.

    Macaulay duration is the present-value-weighted average time (in years) until the
    bond's cash flows are received. Each cash flow's weight is its present value as a
    fraction of the bond's total price.

    Args:
        face_value: The bond's face (par) value in dollars, e.g. 1000.
        coupon_rate: Annual coupon rate as a decimal, e.g. 0.05 for 5%.
        market_rate: Annual market discount rate as a decimal, e.g. 0.06 for 6%.
        years: Years to maturity (integer or float, not months).
        coupons_per_year: Number of coupon payments per year (default 1, annual).

    Returns:
        Macaulay duration in years.
    """
    periods = years * coupons_per_year
    coupon_payment = (face_value * coupon_rate) / coupons_per_year
    period_rate = market_rate / coupons_per_year

    price = 0.0
    weighted_time = 0.0
    for period in range(1, periods + 1):
        cash_flow = coupon_payment
        # Face value is repaid alongside the final coupon.
        if period == periods:
            cash_flow += face_value

        present_value = cash_flow / (1 + period_rate) ** period
        time_in_years = period / coupons_per_year

        price += present_value
        weighted_time += time_in_years * present_value

    # Duration is between 0 and years, and below `years` for any coupon-paying bond.
    return weighted_time / price


if __name__ == "__main__":
    duration = bond_duration(
        face_value=1000,
        coupon_rate=0.05,
        market_rate=0.06,
        years=5,
    )
    print(f"Macaulay duration: {duration:.4f} years")
