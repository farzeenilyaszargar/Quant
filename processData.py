from stockFetch import getStockData
from calcEngine import calculate_dcf, calculate_weighted_score

# right now i have all the data of a particular stock in a dictionary. 
# i want to extract particular values from this.
# CFO, CapEx, Revenue, EBIT, D/E, Cash, Cash from Operations, Free Cash Flow, PE, PB, ROE, ROCE, Dividend Yield, EPS

def get_latest_value(records, metric_name):
    for row in records:
        if metric_name.lower() in row.get('Metric', '').lower():
            # Get the last non-empty value
            values = [v for k, v in row.items() if k != 'Metric' and v and v != '']
            if values:
                return float(values[-1].replace('%', '').strip())
    return 0

def calculate_cagr(records, metric_name, years=3):
    # Try the primary metric name, or fallbacks for banks
    possible_names = [metric_name, "Interest", "Revenue", "Income"] if "Sales" in metric_name else [metric_name]
    
    for name in possible_names:
        for row in records:
            if name.lower() in row.get('Metric', '').lower():
                values = []
                for k, v in row.items():
                    if k != 'Metric' and v and v != '':
                        try:
                            clean_v = float(v.replace('%', '').replace(',', '').strip())
                            values.append(clean_v)
                        except: pass
                
                if len(values) >= years:
                    start = values[-years]
                    end = values[-1]
                    if start > 0:
                        return ((end/start)**(1/years) - 1) * 100
    return 0

def getRatios(data):
    if not data:
        return None
    
    ratios = data.get('ratios', {})
    pnl = data.get('pnl', [])
    cf = data.get('cash_flow', [])
    sh = data.get('shareholding', [])
    
    # 1. ROCE and D/E from ratios
    try:
        roce = float(ratios.get('ROCE', '0').replace('%', '').strip())
        de = float(ratios.get('Debt to Equity', '0').strip())
        market_cap = float(ratios.get('Market Cap', '0').replace('Rs.', '').replace('Cr.', '').replace(',', '').strip())
        current_price = float(ratios.get('Current Price', '0').replace('Rs.', '').replace(',', '').strip())
    except Exception as e:
        print(f"Error parsing ratios: {e}")
        return None

    if market_cap == 0:
        market_cap = 1 # avoid div zero

    # 2. Revenue CAGR
    rev_cagr = calculate_cagr(pnl, "Sales")
    profit_cagr = calculate_cagr(pnl, "Net Profit")
    
    # 3. Free Cash Flow (Latest)
    cfo = get_latest_value(cf, "Cash from Operating Activity")
    capex = abs(get_latest_value(cf, "Fixed assets purchased")) 
    fcf = cfo - capex
    
    # 4. Shareholding Activity (DII + FII)
    fii_latest = get_latest_value(sh, "FIIs")
    dii_latest = get_latest_value(sh, "DIIs")
    
    # Logic for Scores (0-100)
    intrinsic_val = calculate_dcf(fcf, growth_rate=(rev_cagr/100 if rev_cagr > 0 else 0.05))
    dcf_score = min(100, max(0, (intrinsic_val / market_cap) * 50)) 
    growth_score = min(100, max(0, (rev_cagr + profit_cagr) * 2)) 
    roce_score = min(100, max(0, roce * 2))
    
    de_score = max(0, 100 - (de * 50))
    fii_dii_score = min(100, (fii_latest + dii_latest))
    fii_dii_de_score = (de_score + fii_dii_score) / 2
    
    processed = {
        "symbol": data.get('symbol', 'Unknown'),
        "Market Cap (Cr)": market_cap,
        "Current Price": current_price,
        "Intrinsic Value (Total Cr)": round(intrinsic_val, 2),
        "Shares Outstanding (Cr)": round(market_cap / current_price, 2) if current_price > 0 else 0,
        "Intrinsic Price Per Share": round(intrinsic_val / (market_cap / current_price), 2) if market_cap > 0 and current_price > 0 else 0,
        "ROCE (%)": roce,
        "D/E": de,
        "Rev CAGR (%)": round(rev_cagr, 2),
        "FCF (Cr)": fcf,
        "FII (%)": fii_latest,
        "DII (%)": dii_latest,
        "scores": {
            "dcf_score": dcf_score,
            "growth_score": growth_score,
            "roce_score": roce_score,
            "fii_dii_de_score": fii_dii_de_score
        }
    }
    
    return processed