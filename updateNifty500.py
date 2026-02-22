"""
updateNifty500.py  (deprecated shim)
--------------------------------------
Use updateStockList.py --nifty500 instead.
This file is kept for backwards compatibility.
"""

from updateStockList import fetch_nifty500, save

if __name__ == "__main__":
    print("Downloading Nifty 500 list...")
    symbols = fetch_nifty500()
    save(symbols)
    save(symbols, "nifty500Stocks.json")
    print("Done.")
