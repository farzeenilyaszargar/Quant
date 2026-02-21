import requests
import csv
import json
import io

def update_nifty500_stocks():
    url = "https://archives.nseindia.com/content/indices/ind_nifty500list.csv"
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    
    print("Downloading Nifty 500 stock list...")
    response = requests.get(url, headers=headers)
    
    if response.status_code != 200:
        print(f"Failed to download. Status code: {response.status_code}")
        return

    # Decode content
    content = response.content.decode('utf-8')
    csv_reader = csv.DictReader(io.StringIO(content))
    
    symbols = []
    for row in csv_reader:
        # The CSV has Symbol column
        symbol = row.get('Symbol', '').strip()
        if symbol:
            symbols.append(symbol)
    
    # Sort symbols
    symbols.sort()
    
    print(f"Found {len(symbols)} stocks in Nifty 500. Saving to nifty500Stocks.json...")
    
    with open("nifty500Stocks.json", "w") as f:
        json.dump(symbols, f, indent=4)
    
    # Also update the main listOfStocks.json to focus the scan
    with open("listOfStocks.json", "w") as f:
        json.dump(symbols, f, indent=4)
        
    print("Update complete! Both nifty500Stocks.json and listOfStocks.json are updated.")

if __name__ == "__main__":
    update_nifty500_stocks()
