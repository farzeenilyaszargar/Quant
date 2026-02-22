"""
processData.py
--------------
Transforms raw scraped screener.in data into structured financial metrics
and quantitative sub-scores for the scoring engine.
"""

from calcEngine import calculate_dcf


def _clean_float(val: str | None, default: float = 0.0) -> float:
    """Safely converts a string (possibly with currency symbols/commas) to float."""
    if not val:
        return default
    try:
        cleaned = (
            str(val)
            .replace("Rs.", "").replace("Cr.", "")
            .replace(",", "").replace("%", "")
            .strip()
        )
        return float(cleaned) if cleaned else default
    except (ValueError, TypeError):
        return default


def _get_latest_value(records: list[dict], metric_name: str) -> float:
    """Returns the most recent non-empty value for a given metric row name."""
    target = metric_name.lower()
    for row in records:
        if target in row.get("Metric", "").lower():
            values = [v for k, v in row.items() if k != "Metric" and v and v != ""]
            if values:
                return _clean_float(values[-1])
    return 0.0


def _get_avg_value(records: list[dict], metric_name: str, years: int = 3) -> float:
    """Returns the average of the last N years for a given metric row."""
    target = metric_name.lower()
    for row in records:
        if target in row.get("Metric", "").lower():
            values = [
                _clean_float(v)
                for k, v in row.items()
                if k != "Metric" and v and v != ""
            ]
            if values:
                sample = values[-years:]
                return sum(sample) / len(sample)
    return 0.0


def _calculate_cagr(records: list[dict], metric_name: str, years: int = 3) -> float:
    """Calculates CAGR over the last N years for a metric. Returns 0 on failure."""
    aliases = (
        [metric_name, "Revenue", "Income", "Interest"]
        if "Sales" in metric_name
        else [metric_name]
    )
    for name in aliases:
        target = name.lower()
        for row in records:
            if target in row.get("Metric", "").lower():
                values = [
                    _clean_float(v)
                    for k, v in row.items()
                    if k != "Metric" and v and v != ""
                ]
                if len(values) >= years:
                    start, end = values[-years], values[-1]
                    if start > 0 and end > 0:
                        try:
                            result = ((end / start) ** (1 / years) - 1) * 100
                            return float(result.real if isinstance(result, complex) else result)
                        except Exception:
                            pass
                    elif end > start:
                        return 10.0  # Negative-to-positive turnaround bonus
    return 0.0


def _derive_de_from_balance_sheet(bs: list[dict]) -> float:
    """
    Calculates Debt/Equity from balance sheet tables when screener's top panel
    doesn't include it (common for many small/mid caps).
    """
    borrowings = _get_latest_value(bs, "Borrowings")
    equity = _get_latest_value(bs, "Equity Capital")
    reserves = _get_latest_value(bs, "Reserves")
    net_worth = equity + reserves
    if net_worth > 0:
        return round(borrowings / net_worth, 2)
    return 0.0


def getRatios(raw: dict) -> dict | None:
    """
    Processes raw scraped data into a structured stock record with scores.

    Args:
        raw: Output dict from stockFetch.getStockData()

    Returns:
        Structured dict ready for scoring and storage, or None if data insufficient.
    """
    if not raw:
        return None

    ratios = raw.get("ratios", {})
    pnl = raw.get("pnl", [])
    cash_flow = raw.get("cash_flow", [])
    balance_sheet = raw.get("balance_sheet", [])
    shareholding = raw.get("shareholding", [])

    # --- Core Ratios ---
    market_cap = _clean_float(ratios.get("Market Cap"))
    current_price = _clean_float(ratios.get("Current Price"))

    if market_cap == 0 or current_price == 0:
        return None  # Insufficient data to proceed

    roce = _clean_float(ratios.get("ROCE"))
    pe = _clean_float(ratios.get("Stock P/E"))
    book_value = _clean_float(ratios.get("Book Value"))
    pb = round(current_price / book_value, 2) if book_value > 0 else 0.0

    # D/E: try top panel first, fall back to balance sheet derivation
    de = _clean_float(ratios.get("Debt to Equity"))
    if de == 0 and balance_sheet:
        de = _derive_de_from_balance_sheet(balance_sheet)

    # --- Growth Metrics ---
    rev_cagr = _calculate_cagr(pnl, "Sales")
    profit_cagr = _calculate_cagr(pnl, "Net Profit")

    # --- Free Cash Flow ---
    sector = ratios.get("Sector", "Other")
    latest_np = _get_latest_value(pnl, "Net Profit")

    if "Bank" in sector or "Finance" in sector:
        # For financials, net profit is a better proxy than operating cash flow
        fcf = latest_np
    else:
        cfo_avg = _get_avg_value(cash_flow, "Cash from Operating Activity")
        capex_avg = abs(_get_avg_value(cash_flow, "Fixed assets purchased"))
        fcf = cfo_avg - capex_avg
        # If CapEx-heavy and still profitable, use a conservative NP conversion rate
        if fcf <= 0 and latest_np > 0:
            fcf = latest_np * 0.40

    # --- Shareholding ---
    fii = _get_latest_value(shareholding, "FIIs")
    dii = _get_latest_value(shareholding, "DIIs")

    # --- Scoring (0–100) ---
    intrinsic_val = calculate_dcf(
        max(0, fcf),
        growth_rate=float(rev_cagr) / 100 if rev_cagr > 0 else 0.05,
    )
    if isinstance(intrinsic_val, complex):
        intrinsic_val = intrinsic_val.real

    shares = round(market_cap / current_price, 2)

    dcf_score = min(100.0, max(0.0, (intrinsic_val / market_cap) * 25))
    growth_score = min(100.0, max(0.0, (rev_cagr + profit_cagr) * 2))
    roce_score = min(100.0, max(0.0, roce * 2))
    de_score = max(0.0, 100.0 - (de * 50))
    fii_dii_score = min(100.0, fii + dii)
    fii_dii_de_score = (de_score + fii_dii_score) / 2

    return {
        "symbol": raw.get("symbol", "Unknown"),
        "Company Name": raw.get("Company Name", raw.get("symbol", "Unknown")),
        "About": raw.get("About", "N/A"),
        "Sector": sector,
        "Market Cap (Cr)": market_cap,
        "Current Price": current_price,
        "Intrinsic Value (Total Cr)": round(float(intrinsic_val), 2),
        "Shares Outstanding (Cr)": shares,
        "Intrinsic Price Per Share": round(float(intrinsic_val) / shares, 2) if shares > 0 else 0,
        "ROCE (%)": roce,
        "PE": pe,
        "PB": pb,
        "D/E": de,
        "Rev CAGR (%)": round(float(rev_cagr), 2),
        "FCF (Cr)": round(fcf, 2),
        "FII (%)": fii,
        "DII (%)": dii,
        "scores": {
            "dcf_score": round(float(dcf_score), 4),
            "growth_score": round(float(growth_score), 4),
            "roce_score": round(float(roce_score), 4),
            "fii_dii_de_score": round(float(fii_dii_de_score), 4),
        },
    }