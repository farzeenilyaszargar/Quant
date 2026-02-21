import json
from calcEngine import calculate_dcf, calculate_weighted_score
from portfolioOptimizer import get_broad_sector

def recalculate():
    print("Recalculating scores with stricter DCF model...")
    try:
        with open("stockData.json", "r") as f:
            stocks = json.load(f)
    except FileNotFoundError:
        print("stockData.json not found.")
        return

    for s in stocks:
        fcf = s.get("FCF (Cr)", 0)
        rev_cagr = s.get("Rev CAGR (%)", 0)
        mcap = s.get("Market Cap (Cr)", 1)
        
        # 1. New Stricter DCF
        intrinsic_val = calculate_dcf(fcf, growth_rate=(float(rev_cagr)/100 if rev_cagr > 0 else 0.05))
        s["Intrinsic Value (Total Cr)"] = round(float(intrinsic_val), 2)
        
        # Calculate intrinsic price per share
        shares = s.get("Shares Outstanding (Cr)", 1)
        if shares > 0:
            s["Intrinsic Price Per Share"] = round(float(intrinsic_val) / shares, 2)
        
        # 2. Update Scores
        # Stricter DCF Score: (Intrinsic / Market Cap) * 25
        dcf_score = min(100, max(0, (float(intrinsic_val) / mcap) * 25))
        s["scores"]["dcf_score"] = float(dcf_score)
        
        # Recalculate Final Score
        s["final_score"] = calculate_weighted_score(s["scores"])
        
        # Ensure Broad Sector is correct
        s["Broad Sector"] = get_broad_sector(s.get("Sector", "Other"))

    # Sort results by final score
    stocks.sort(key=lambda x: x.get('final_score', 0), reverse=True)

    # Re-apply portfolio weights to top 50
    from portfolioOptimizer import allocate_portfolio
    allocations = allocate_portfolio(stocks)
    
    # Reset all weights
    for r in stocks:
        r['portfolio_weight'] = 0
    
    # Assign new weights
    for alloc in allocations:
        match = next((r for r in stocks if r['symbol'] == alloc['symbol']), None)
        if match:
            match['portfolio_weight'] = alloc['final_weight']

    with open("stockData.json", "w") as f:
        json.dump(stocks, f, indent=4)
    
    try:
        with open("website/data/stockData.json", "w") as f:
            json.dump(stocks, f, indent=4)
    except FileNotFoundError:
        pass
    
    print("Optimization and re-scoring complete.")

if __name__ == "__main__":
    recalculate()
