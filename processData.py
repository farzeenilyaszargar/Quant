from stockFetch import getStockData
from calcEngine import calculate_dcf, calculate_weighted_score

def clean_float(val_str, default=0.0):
    if not val_str:
        return default
    try:
        # Standardize: remove currency, commas, and handle empty after strip
        clean = val_str.replace('Rs.', '').replace('Cr.', '').replace(',', '').replace('%', '').strip()
        if not clean:
            return default
        return float(clean)
    except:
        return default

def get_latest_value(records, metric_name):
    for row in records:
        if metric_name.lower() in row.get('Metric', '').lower():
            values = [v for k, v in row.items() if k != 'Metric' and v and v != '']
            if values:
                return clean_float(values[-1])
    return 0

def calculate_cagr(records, metric_name, years=3):
    possible_names = [metric_name, "Interest", "Revenue", "Income"] if "Sales" in metric_name else [metric_name]
    
    for name in possible_names:
        for row in records:
            if name.lower() in row.get('Metric', '').lower():
                values = []
                for k, v in row.items():
                    if k != 'Metric' and v and v != '':
                        clean_v = clean_float(v)
                        values.append(clean_v)
                
                if len(values) >= years:
                    start = values[-years]
                    end = values[-1]
                    # CAGR on negative values is complex. Limit to positive start.
                    if start > 0 and end > 0:
                        try:
                            res = ((end/start)**(1/years) - 1) * 100
                            # Ensure we don't return complex numbers
                            if isinstance(res, complex):
                                return res.real
                            return float(res)
                        except: pass
                    elif end > start: # Simple linear growth approximation for negative to positive
                        return 10.0 # Default growth bonus
    return 0

def getRatios(data):
    if not data:
        return None
    
    ratios = data.get('ratios', {})
    pnl = data.get('pnl', [])
    cf = data.get('cash_flow', [])
    sh = data.get('shareholding', [])
    
    # Use clean_float with fallbacks for resilience
    roce = clean_float(ratios.get('ROCE'))
    de = clean_float(ratios.get('Debt to Equity'))
    market_cap = clean_float(ratios.get('Market Cap'))
    current_price = clean_float(ratios.get('Current Price'))

    if market_cap == 0 or current_price == 0:
        # Some stocks might be missing core data; skip them
        return None

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
    intrinsic_val = calculate_dcf(fcf, growth_rate=(float(rev_cagr)/100 if rev_cagr > 0 else 0.05))
    
    # Safety checks for DCF calculation
    if isinstance(intrinsic_val, complex):
        intrinsic_val = intrinsic_val.real
    
    dcf_score = min(100, max(0, (intrinsic_val / market_cap) * 50)) 
    growth_score = min(100, max(0, (float(rev_cagr) + float(profit_cagr)) * 2)) 
    roce_score = min(100, max(0, float(roce) * 2))
    
    de_score = max(0, 100 - (float(de) * 50))
    fii_dii_score = min(100, (float(fii_latest) + float(dii_latest)))
    fii_dii_de_score = (de_score + fii_dii_score) / 2
    
    processed = {
        "symbol": data.get('symbol', 'Unknown'),
        "Sector": ratios.get('Sector', 'Other'),
        "Industry": ratios.get('Industry', 'Other'),
        "Market Cap (Cr)": market_cap,
        "Current Price": current_price,
        "Intrinsic Value (Total Cr)": round(float(intrinsic_val), 2),
        "Shares Outstanding (Cr)": round(market_cap / current_price, 2),
        "Intrinsic Price Per Share": round(float(intrinsic_val) / (market_cap / current_price), 2),
        "ROCE (%)": roce,
        "D/E": de,
        "Rev CAGR (%)": round(float(rev_cagr), 2),
        "FCF (Cr)": fcf,
        "FII (%)": fii_latest,
        "DII (%)": dii_latest,
        "scores": {
            "dcf_score": float(dcf_score),
            "growth_score": float(growth_score),
            "roce_score": float(roce_score),
            "fii_dii_de_score": float(fii_dii_de_score)
        }
    }
    
    return processed