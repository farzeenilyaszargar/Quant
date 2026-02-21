
def get_broad_sector(sector):
    """Maps granular sectors to broad categories."""
    mapping = {
        "Financial": "Finance",
        "Bank": "Finance",
        "Insurance": "Finance",
        "NBFC": "Finance",
        "IT": "Technology",
        "Software": "Technology",
        "Tech": "Technology",
        "Pharmaceutical": "Healthcare",
        "Healthcare": "Healthcare",
        "Oils & Gas": "Energy",
        "Power": "Energy",
        "Energy": "Energy",
        "Auto": "Consumer",
        "Retail": "Consumer",
        "FMCG": "Consumer",
        "Consumer": "Consumer",
        "Telecom": "Communication",
        "Infrastructure": "Industrial",
        "Industrial": "Industrial",
        "Textile": "Industrial",
        "Chemicals": "Industrial"
    }
    
    combined = str(sector).lower()
    for key, broad in mapping.items():
        if key.lower() in combined:
            return broad
    return "Others"

def allocate_portfolio(stocks_data):
    """
    Optimizes portfolio allocation with strict filtering:
    1. Overvaluation < 15% (Intrinsic Price * 1.15 >= Current Price)
    2. Final Score >= 45 (High Quality)
    3. Limit to Top 50
    """
    if not stocks_data:
        return []

    processed_stocks = []
    for s in stocks_data:
        current_price = s.get('Current Price', 0)
        intrinsic_price = s.get('Intrinsic Price Per Share', 0)
        final_score = s.get('final_score', 0)
        
        # 1. Broad Sector Assignment
        s['Broad Sector'] = get_broad_sector(s.get('Sector', 'Other'))

        # 2. Filtering
        # Case A: Overvalued (Current is 15% more than intrinsic) -> Ignore
        if intrinsic_price > 0 and current_price > (intrinsic_price * 1.15):
            continue
        
        # Case B: Low Score
        if final_score < 45:
            continue
            
        processed_stocks.append(s)

    # 3. Sort by score and take top 50
    processed_stocks.sort(key=lambda x: x['final_score'], reverse=True)
    top_50 = processed_stocks[:50]

    if not top_50:
        return []

    # 4. Calculate Base Weights (Square of score for alpha)
    total_score_sq = sum(s['final_score'] ** 2 for s in top_50)
    
    allocations = []
    for s in top_50:
        weight = (s['final_score'] ** 2) / total_score_sq
        allocations.append({
            "symbol": s['symbol'],
            "final_weight": round(weight, 4),
            "broad_sector": s['Broad Sector']
        })

    return allocations
