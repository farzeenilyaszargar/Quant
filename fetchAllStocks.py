import asyncio
import json
import csv
import io
from playwright.async_api import async_playwright

async def fetch_all_nse_stocks():
    print("Fetching full NSE stock list via Playwright...")
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36")
        page = await context.new_page()
        
        # URL for the full list of equities
        url = "https://www.nseindia.com/api/equity-stockIndices?index=SECURITIES%20IN%20F%26O"
        # Since API might be protected, we visit the page first to get cookies
        await page.goto("https://www.nseindia.com/market-data/live-equity-market")
        
        # Alternatively, use the CSV download link which is usually more stable if cookies are present
        csv_url = "https://archives.nseindia.com/content/equities/EQUITY_L.csv"
        
        print("Downloading full equity list...")
        # NSE often blocks direct requests, so we use playwright to fetch
        response = await page.evaluate(f"""
            fetch('{csv_url}').then(res => res.text())
        """)
        
        await browser.close()
        
        if not response or "SYMBOL" not in response:
            print("Failed to fetch equity list.")
            return

        csv_reader = csv.DictReader(io.StringIO(response))
        symbols = []
        for row in csv_reader:
            symbol = row.get('SYMBOL', '').strip()
            series = row.get(' SERIES', '').strip()
            # We want main board equities (usually series EQ)
            if symbol and (series == 'EQ' or series == ''):
                symbols.append(symbol)
        
        symbols.sort()
        print(f"Found {len(symbols)} stocks. Saving...")
        
        with open("allStocks.json", "w") as f:
            json.dump(symbols, f, indent=4)
        
        with open("listOfStocks.json", "w") as f:
            json.dump(symbols, f, indent=4)
            
        print("Success! Created allStocks.json and updated listOfStocks.json.")

if __name__ == "__main__":
    asyncio.run(fetch_all_nse_stocks())
