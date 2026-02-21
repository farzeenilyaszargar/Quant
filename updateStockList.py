import requests
import csv
import json
import io

def update_nse_stocks():
    url = "https://archives.nseindia.com/content/equities/EQUITY_L.csv"
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    
    print("Downloading NSE stock list...")
    response = requests.get(url, headers=headers)
    
    if response.status_code != 200:
        print(f"Failed to download. Status code: {response.status_code}")
        return

    # Decode content
    content = response.content.decode('utf-8')
    csv_reader = csv.DictReader(io.StringIO(content))
    
    symbols = []
    for row in csv_reader:
        symbol = row.get('SYMBOL', '').strip()
        series = row.get(' SERIES', '').strip() or row.get('SERIES', '').strip()
        
        # We focus on Equity (EQ) and BE series primarily
        if symbol and series in ['EQ', 'BE']:
            symbols.append(symbol)
    
    # Sort symbols
    symbols.sort()
    
    print(f"Found {len(symbols)} stocks. Saving to listOfStocks.json...")
    
    with open("listOfStocks.json", "w") as f:
        json.dump(symbols, f, indent=4)
    
    print("Update complete!")

if __name__ == "__main__":
    update_nse_stocks()
