"""
calcEngine.py
--------------
Core quantitative engine for DCF valuation and final composite score calculation.

Scoring Weights:
    DCF Score:           30%
    Growth Score:        20%
    ROCE Score:          10%
    Moat/Customer Score: 15%
    FII/DII/DE Score:    5%
    Tailwind Score:      10%
    Management Score:    10%
"""


def calculate_dcf(
    fcf: float,
    growth_rate: float = 0.08,
    terminal_growth: float = 0.015,
    discount_rate: float = 0.18,
    years: int = 10,
) -> float:
    """
    Conservative DCF with step-down growth decay.

    Args:
        fcf:             Free Cash Flow in Cr. Returns 0 if ≤ 0.
        growth_rate:     Initial annual growth rate (capped at 25%).
        terminal_growth: Perpetual growth after projection window.
        discount_rate:   WACC / required rate of return (18% for India).
        years:           Projection horizon.

    Returns:
        Intrinsic enterprise value in Cr.
    """
    if fcf <= 0:
        return 0.0

    working_growth = min(0.25, growth_rate)
    decay_factor = 0.90  # Growth slows by 10% each year

    current_fcf = fcf
    projected_fcf = []
    for _ in range(years):
        current_fcf *= (1 + working_growth)
        projected_fcf.append(current_fcf)
        working_growth *= decay_factor

    discounted = [
        val / (1 + discount_rate) ** (i + 1)
        for i, val in enumerate(projected_fcf)
    ]

    terminal_value = (projected_fcf[-1] * (1 + terminal_growth)) / (
        discount_rate - terminal_growth
    )
    discounted_tv = terminal_value / (1 + discount_rate) ** years

    return sum(discounted) + discounted_tv


def calculate_weighted_score(metrics: dict) -> float:
    """
    Computes the final composite quant score (0–100) from individual sub-scores.

    Args:
        metrics: Dict with keys dcf_score, growth_score, roce_score,
                 moat_score, fii_dii_de_score, tailwind_score, management_score.
    Returns:
        Rounded composite score.
    """
    score = (
        0.30 * metrics.get("dcf_score", 0)
        + 0.20 * metrics.get("growth_score", 0)
        + 0.10 * metrics.get("roce_score", 0)
        + 0.15 * metrics.get("moat_score", 0)
        + 0.05 * metrics.get("fii_dii_de_score", 0)
        + 0.10 * metrics.get("tailwind_score", 0)
        + 0.10 * metrics.get("management_score", 0)
    )
    return round(score, 2)
