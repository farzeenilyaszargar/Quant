"""
portfolioOptimizer.py
----------------------
Sector classification and portfolio allocation engine.

Allocation Logic:
  1. Filter: Drop stocks >15% above DCF intrinsic value OR final_score < 40.
  2. Apply composite allocation score that rewards:
       a. High final_score (capture moat/quality)
       b. DCF undervaluation: stocks trading well below intrinsic get a bonus
       c. Quality premium: high ROCE, low D/E, high FII/DII ownership
  3. Rank by composite alloc_score, take top 150.
  4. Weight = alloc_score² / sum(alloc_score²), so conviction is proportional.
"""

# ── Sector Classification ───────────────────────────────────────────────────

_SECTOR_MAP: dict[str, str] = {
    # Finance
    "Financial": "Finance", "Bank": "Finance", "Insurance": "Finance",
    "NBFC": "Finance", "Lending": "Finance", "Microfinance": "Finance",
    # Technology
    "IT": "Technology", "Software": "Technology", "Tech": "Technology",
    "Electronics": "Technology", "Semiconductor": "Technology",
    # Healthcare
    "Pharmaceutical": "Healthcare", "Healthcare": "Healthcare",
    "Hospital": "Healthcare", "Diagnostic": "Healthcare",
    # Energy
    "Oils & Gas": "Energy", "Power": "Energy", "Energy": "Energy",
    "Renewable": "Energy", "Solar": "Energy",
    # Consumer
    "Auto": "Consumer", "Retail": "Consumer", "FMCG": "Consumer",
    "Consumer": "Consumer", "Durables": "Consumer", "Apparel": "Consumer",
    "Food": "Consumer", "Beverages": "Consumer",
    # Communication
    "Telecom": "Communication", "Media": "Communication",
    # Industrial / Infra
    "Infrastructure": "Industrial", "Industrial": "Industrial",
    "Industrials": "Industrial", "Textile": "Industrial",
    "Chemicals": "Industrial", "Metal": "Industrial", "Steel": "Industrial",
    "Mining": "Industrial", "Construction": "Industrial",
    "Defence": "Industrial", "Engineering": "Industrial",
    "Cement": "Industrial", "Packaging": "Industrial",
    # Real Estate
    "Real Estate": "Real Estate", "Realty": "Real Estate",
}


def get_broad_sector(sector: str) -> str:
    """Maps a granular NSE sector string to one of the broad categories above."""
    s = str(sector).lower()
    for key, broad in _SECTOR_MAP.items():
        if key.lower() in s:
            return broad
    return "Others"


# ── Allocation Score ─────────────────────────────────────────────────────────

def _allocation_score(stock: dict) -> float:
    """
    Composite score used for weighting, beyond just final_score.

    Components:
        base      – final_score (0–100), primary driver
        dcf_bonus – discount to intrinsic value. Trading below DCF = bonus.
        quality   – ROCE and D/E reward for financially strong businesses.
        inst      – FII+DII ownership as a proxy for institutional conviction.

    All components normalised to additive boosts on top of base.
    """
    base = stock.get("final_score", 0)

    # DCF discount bonus (up to +25 pts for deeply undervalued stocks)
    current = stock.get("Current Price", 0)
    intrinsic = stock.get("Intrinsic Price Per Share", 0)
    if intrinsic > 0 and current > 0:
        discount_pct = (intrinsic - current) / intrinsic  # positive = below DCF
        dcf_bonus = max(-10.0, min(25.0, discount_pct * 40))  # scale to ±25
    else:
        dcf_bonus = 0.0

    # Quality premium (up to +15 pts)
    roce = stock.get("ROCE (%)", 0)
    de = stock.get("D/E", 1.0)  # treat unknown as 1x
    roce_pts = min(10.0, roce / 4)        # ROCE 40%+ → +10 pts
    de_pts = max(-5.0, min(5.0, (1 - de) * 5))  # D/E < 1 → +pts, > 1 → -pts
    quality_bonus = roce_pts + de_pts

    # Institutional ownership signal (up to +10 pts)
    fii = stock.get("FII (%)", 0)
    dii = stock.get("DII (%)", 0)
    inst_bonus = min(10.0, (fii + dii) / 5)

    return base + dcf_bonus + quality_bonus + inst_bonus


# ── Portfolio Allocation ─────────────────────────────────────────────────────

MAX_PORTFOLIO = 150  # Target maximum holdings

def allocate_portfolio(stocks_data: list[dict]) -> list[dict]:
    """
    Filters, scores, ranks, and weights stocks for the portfolio.

    Args:
        stocks_data: Full universe of processed stock dicts.

    Returns:
        List of dicts: {symbol, final_weight, broad_sector, alloc_score}
        Weights sum to ~1.0.
    """
    if not stocks_data:
        return []

    # Assign broad sector (idempotent)
    for s in stocks_data:
        s["Broad Sector"] = get_broad_sector(s.get("Sector", "Other"))

    # ── Filter ──────────────────────────────────────────────────────────────
    candidates = []
    for s in stocks_data:
        score = s.get("final_score", 0)
        current = s.get("Current Price", 0)
        intrinsic = s.get("Intrinsic Price Per Share", 0)

        # Quality floor
        if score < 40:
            continue

        # Overvaluation cap: exclude if trading >15% above DCF intrinsic
        if intrinsic > 0 and current > intrinsic * 1.15:
            continue

        candidates.append(s)

    if not candidates:
        return []

    # ── Score & Rank ─────────────────────────────────────────────────────────
    for s in candidates:
        s["_alloc_score"] = _allocation_score(s)

    candidates.sort(key=lambda x: x["_alloc_score"], reverse=True)
    top = candidates[:MAX_PORTFOLIO]

    # ── Weight (score² for conviction-proportional allocation) ───────────────
    total_sq = sum(s["_alloc_score"] ** 2 for s in top)
    if total_sq == 0:
        return []

    result = []
    for s in top:
        weight = (s["_alloc_score"] ** 2) / total_sq
        result.append({
            "symbol": s["symbol"],
            "final_weight": round(weight, 4),
            "broad_sector": s["Broad Sector"],
            "alloc_score": round(s["_alloc_score"], 2),
        })
        # Clean up temp key
        del s["_alloc_score"]

    return result
