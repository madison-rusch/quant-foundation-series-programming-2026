"""Price a bond by discounting its coupons and face value at the market rate."""


def bond_price(
    face_value: float,
    coupon_rate: float,
    market_rate: float,
    years: int,
    coupons_per_year: int = 1,
) -> float:
    """Return the present value (price) of a bond, in dollars.

    Each coupon payment and the face value are discounted back to today at the
    market rate. Supports more than one coupon per year (e.g. semiannual or
    quarterly) via ``coupons_per_year``.

    Args:
        face_value: The bond's face (par) value in dollars, e.g. 1000.
        coupon_rate: Annual coupon rate as a decimal, e.g. 0.05 for 5%.
        market_rate: Annual market discount rate as a decimal, e.g. 0.06 for 6%.
        years: Years to maturity (integer or float, not months).
        coupons_per_year: Number of coupon payments per year as a count
            (default 1 = annual; 2 = semiannual; 4 = quarterly).

    Returns:
        The bond's price in dollars — the present value of all its cash flows.
    """
    periods = years * coupons_per_year
    coupon_payment = (face_value * coupon_rate) / coupons_per_year
    period_rate = market_rate / coupons_per_year

    price = 0.0
    for period in range(1, periods + 1):
        # Discount each coupon back to today by its own number of periods.
        price += coupon_payment / (1 + period_rate) ** period

    # The face value is repaid once, at maturity (the final period).
    price += face_value / (1 + period_rate) ** periods

    # Sanity check: price should be below face_value when coupon_rate < market_rate.
    return price


if __name__ == "__main__":
    price = bond_price(
        face_value=1000,
        coupon_rate=0.05,
        market_rate=0.06,
        years=5,
    )
    print(f"Bond price: {price:,.2f}")
