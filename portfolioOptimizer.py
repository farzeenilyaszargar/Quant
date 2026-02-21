import numpy as np

def allocate_portfolio(stocks_data, sector_limits=None):
    """
    Optimizes portfolio allocation based on Quant Score and Sector Constraints.
    stocks_data: List of processed stock dictionaries
    sector_limits: Dict like {'Financial': 0.25, 'IT': 0.20}
    """
    if not stocks_data:
        return []

    if sector_limits is None:
        sector_limits = {
            "Financial Services": 0.25,
            "Information Technology": 0.20,
            "Healthcare": 0.15,
            "Energy": 0.15,
            "Consumer Discretionary": 0.15,
            "Others": 0.10
        }

    # 1. Calculate Base Weights from Final Score
    # We use (final_score^2) to emphasize top picks
    total_score = sum(s['final_score'] ** 2 for s in stocks_data)
    
    allocations = []
    for s in stocks_data:
        base_weight = (s['final_score'] ** 2) / total_score
        allocations.append({
            "symbol": s['symbol'],
            "sector": s.get('Sector', 'Others'),
            "score": s['final_score'],
            "base_weight": base_weight
        })

    # 2. Apply Sector Constraints (Heuristic approach)
    # Group by sector
    sector_groups = {}
    for a in allocations:
        sect = a['sector']
        if sect not in sector_groups:
            sector_groups[sect] = []
        sector_groups[sect].append(a)

    final_allocs = []
    total_assigned_weight = 0

    for sect, group in sector_groups.items():
        limit = sector_limits.get(sect, 0.15) # default 15% for unspecified sectors
        sect_total_base = sum(a['base_weight'] for a in group)
        
        # If total base weight of sector exceeds limit, we scale it down
        scaling_factor = min(1.0, limit / sect_total_base) if sect_total_base > 0 else 0
        
        for a in group:
            a['final_weight'] = round(a['base_weight'] * scaling_factor, 4)
            total_assigned_weight += a['final_weight']

    # 3. Re-normalize to ensure sum is 100%
    if total_assigned_weight > 0:
        for a in allocations:
            a['final_weight'] = round(a['final_weight'] / total_assigned_weight, 4)

    return allocations
