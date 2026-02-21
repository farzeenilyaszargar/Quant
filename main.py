import json
import random
import time
from stockFetch import getStockData
from processData import getRatios
from aiAnalysis import get_ai_analysis
from calcEngine import calculate_weighted_score

def main():
    stocks = []
    
    try:
        with open("listOfStocks.json", "r") as f:
            stocks = json.load(f)
    except FileNotFoundError:
        print("listOfStocks.json not found.")
        return

    results = []

    for stock in stocks:
        print(f"--- Processing {stock} ---")
        
        # 1. Fetch
        raw_data = getStockData(stock)
        if not raw_data:
            print(f"Failed to fetch data for {stock}")
            continue
            
        # 2. Process Financials
        processed = getRatios(raw_data)
        if not processed:
            print(f"Failed to process data for {stock}")
            continue
            
        # 3. Get AI Insights
        ai_insights = get_ai_analysis(stock)
        
        # 4. Integrate scores
        moat_and_sat_score = (ai_insights['customer_satisfaction'] + ai_insights['moat']) / 2
        tailwind_score = ai_insights['tailwind']
        management_score = ai_insights['management_quality']
        
        scores = processed['scores']
        scores['moat_score'] = moat_and_sat_score
        scores['tailwind_score'] = tailwind_score
        scores['management_score'] = management_score
        
        # 5. Calculate Final Score
        final_score = calculate_weighted_score(scores)
        processed['final_score'] = final_score
        processed['ai_notes'] = ai_insights['notes']
        
        print(f"Final Weighted Score: {final_score}")
        results.append(processed)
        
        # Avoid rate limiting
        time.sleep(random.uniform(1, 3))

    # Save to stockData.json
    with open("stockData.json", "w") as f:
        json.dump(results, f, indent=4)
        
    print(f"\nSuccessfully processed {len(results)} stocks. Results saved to stockData.json")

if __name__ == "__main__":
    main()