import json
import random
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from stockFetch import getStockData
from processData import getRatios
from aiAnalysis import get_ai_analysis
from calcEngine import calculate_weighted_score
from portfolioOptimizer import allocate_portfolio

# Load existing results to resume
def load_existing():
    try:
        with open("stockData.json", "r") as f:
            return json.load(f)
    except:
        return []

def process_single_stock(stock):
    # Add a random delay to avoid rate limits
    time.sleep(random.uniform(2, 5))
    
    print(f"--- Analyzing {stock} ---")
    try:
        # 1. Fetch with retries handled in stockFetch (usually)
        raw_data = getStockData(stock)
        if not raw_data:
            return None
            
        # 2. Process Financials
        processed = getRatios(raw_data)
        if not processed:
            return None
            
        # 3. Get AI Insights
        ai_insights = get_ai_analysis(stock)
        
        # 4. Integrate scores
        moat_and_sat_score = (ai_insights.get('customer_satisfaction', 50) + ai_insights.get('moat', 50)) / 2
        tailwind_score = ai_insights.get('tailwind', 50)
        management_score = ai_insights.get('management_quality', 50)
        
        scores = processed['scores']
        scores['moat_score'] = moat_and_sat_score
        scores['tailwind_score'] = tailwind_score
        scores['management_score'] = management_score
        
        # 5. Calculate Final Score
        final_score = calculate_weighted_score(scores)
        processed['final_score'] = final_score
        processed['ai_notes'] = ai_insights.get('notes', "Brief analysis performed.")
        
        return processed
    except Exception as e:
        print(f"Error processing {stock}: {e}")
        return None

def main():
    print("Initializing Quant Bot...")
    try:
        with open("listOfStocks.json", "r") as f:
            all_stocks = json.load(f)
    except FileNotFoundError:
        print("listOfStocks.json not found.")
        return

    existing_results = load_existing()
    existing_symbols = {r['symbol'] for r in existing_results}
    
    # Filter out already processed stocks to support resuming
    stocks_to_process = [s for s in all_stocks if s not in existing_symbols]
    
    if not stocks_to_process:
        print("All stocks from list are already processed. To re-run, clear stockData.json.")
        # But we still want to re-calculate portfolio allocation
        results = existing_results
    else:
        print(f"Starting analysis for {len(stocks_to_process)} remaining stocks (Total: {len(all_stocks)})...")
        results = existing_results
        
        # Process one by one with immediate save
        for s in stocks_to_process:
            res = process_single_stock(s)
            if res:
                results.append(res)
                print(f"Success: {s}! Optimizing and saving...")
                
                # Apply allocation logic to the current set of results
                valid_results = [r for r in results if 'final_score' in r]
                allocations = allocate_portfolio(valid_results)
                for r_item in valid_results:
                    match = next((a for a in allocations if a['symbol'] == r_item['symbol']), None)
                    if match:
                        r_item['portfolio_weight'] = match['final_weight']
                
                valid_results.sort(key=lambda x: x.get('final_score', 0), reverse=True)
                save_outputs(valid_results)
            else:
                print(f"Skipped {s} (fetch failed or error).")
                # Even on skip, we might want to wait a bit longer
                time.sleep(random.uniform(10, 20))

    print(f"\nScanning complete or paused. {len(results)} stocks in portfolio.")

def save_outputs(results):
    with open("stockData.json", "w") as f:
        json.dump(results, f, indent=4)
    
    try:
        with open("website/data/stockData.json", "w") as f:
            json.dump(results, f, indent=4)
    except FileNotFoundError:
        pass

if __name__ == "__main__":
    main()