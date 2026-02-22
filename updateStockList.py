"""
updateStockList.py
-------------------
Downloads and saves the NSE equity list or the Nifty 500 index constituents.

Usage:
    python updateStockList.py           # Full NSE list → listOfStocks.json
    python updateStockList.py --nifty500  # Nifty 500 only → listOfStocks.json
"""

import argparse
import csv
import io
import json
import sys

import requests

NSE_ALL_URL = "https://archives.nseindia.com/content/equities/EQUITY_L.csv"
NIFTY500_URL = "https://archives.nseindia.com/content/indices/ind_nifty500list.csv"

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36"
    )
}


def _fetch_csv(url: str) -> str:
    res = requests.get(url, headers=HEADERS, timeout=15)
    if res.status_code != 200:
        raise ConnectionError(f"HTTP {res.status_code} fetching {url}")
    return res.content.decode("utf-8")


def fetch_all_nse() -> list[str]:
    """Returns all NSE EQ/BE series equity symbols."""
    content = _fetch_csv(NSE_ALL_URL)
    reader = csv.DictReader(io.StringIO(content))
    symbols = []
    for row in reader:
        symbol = row.get("SYMBOL", "").strip()
        series = (row.get(" SERIES") or row.get("SERIES") or "").strip()
        if symbol and series in ("EQ", "BE"):
            symbols.append(symbol)
    return sorted(symbols)


def fetch_nifty500() -> list[str]:
    """Returns Nifty 500 constituent symbols."""
    content = _fetch_csv(NIFTY500_URL)
    reader = csv.DictReader(io.StringIO(content))
    symbols = [row.get("Symbol", "").strip() for row in reader]
    return sorted(s for s in symbols if s)


def save(symbols: list[str], path: str = "listOfStocks.json") -> None:
    with open(path, "w") as f:
        json.dump(symbols, f, indent=4)
    print(f"  Saved {len(symbols)} symbols to {path}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Update NSE stock list.")
    parser.add_argument(
        "--nifty500",
        action="store_true",
        help="Download Nifty 500 only (default: full NSE list)",
    )
    args = parser.parse_args()

    try:
        if args.nifty500:
            print("Downloading Nifty 500 list...")
            symbols = fetch_nifty500()
            save(symbols)
            save(symbols, "nifty500Stocks.json")
        else:
            print("Downloading full NSE equity list...")
            symbols = fetch_all_nse()
            save(symbols)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
