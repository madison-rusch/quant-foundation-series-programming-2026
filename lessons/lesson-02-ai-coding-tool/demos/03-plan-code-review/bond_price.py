"""Bond pricing demo — output of the Plan/Code/Review walkthrough in PLAN_CODE_REVIEW_DEMO.md."""


def bond_price(
    face_value: float,
    coupon_rate: float,
    market_rate: float,
    years: int,
    coupons_per_year: int = 1,
) -> float:
    """Return the present value (price) of a bond.

    Discounts each coupon payment and the face value at the market rate.

    Args:
        face_value: The bond's face (par) value, e.g. 1000.
        coupon_rate: Annual coupon rate as a decimal, e.g. 0.05 for 5%.
        market_rate: Annual market discount rate as a decimal, e.g. 0.06 for 6%.
        years: Years to maturity.
        coupons_per_year: Number of coupon payments per year (default 1, annual).

    Returns:
        The present value of the bond's cash flows.
    """
    periods = years * coupons_per_year
    coupon_payment = (face_value * coupon_rate) / coupons_per_year
    period_rate = market_rate / coupons_per_year

    price = 0.0
    for period in range(1, periods + 1):
        # Each coupon is discounted back to today at the period rate.
        price += coupon_payment / (1 + period_rate) ** period

    # Face value is only returned once, at the final period.
    price += face_value / (1 + period_rate) ** periods

    return price


if __name__ == "__main__":
    price = bond_price(
        face_value=1000,
        coupon_rate=0.05,
        market_rate=0.06,
        years=5,
    )
    print(f"Bond price: {price:,.2f}")
