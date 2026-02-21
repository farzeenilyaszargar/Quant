import json
import time
from stockFetch import fetch_page
from portfolioOptimizer import get_broad_sector
from bs4 import BeautifulSoup

def update_sectors():
    print("Updating sectors for existing stocks...")
    try:
        with open("stockData.json", "r") as f:
            data = json.load(f)
    except FileNotFoundError:
        print("stockData.json not found.")
        return

    for stock in data:
        symbol = stock['symbol']
        print(f"Fetching sector for {symbol}...")
        try:
            soup = fetch_page(symbol)
            sector = "Other"
            
            # Target peers section first
            peers = soup.find("section", {"id": "peers"})
            if peers:
                links = peers.find_all("a", href=lambda x: x and "/market/" in x)
                if links:
                    sector = links[0].text.strip()
            
            # Fallback to breadcrumb
            if sector == "Other":
                breadcrumb = soup.find("p", class_="breadcrumb")
                if breadcrumb:
                    links = breadcrumb.find_all("a")
                    if len(links) >= 2:
                        sector = links[1].text.strip()
            
            stock["Sector"] = sector
            stock["Broad Sector"] = get_broad_sector(sector)
            if "Industry" in stock:
                del stock["Industry"]
            print(f"  Result: {sector} -> {stock['Broad Sector']}")
            
            # Save intermediate results
            with open("stockData.json", "w") as f:
                json.dump(data, f, indent=4)
            try:
                with open("website/data/stockData.json", "w") as f:
                    json.dump(data, f, indent=4)
            except: pass
            
        except Exception as e:
            print(f"  Error for {symbol}: {e}")
        
        # Respect rate limits
        time.sleep(2)

if __name__ == "__main__":
    update_sectors()
