"""
main.py
--------
Entry point for the Quant Stock Analysis Pipeline.

Workflow per stock:
    1. Fetch financial data from screener.in       (stockFetch)
    2. Process into structured metrics & scores    (processData)
    3. Get AI qualitative scores                   (aiAnalysis)
    4. Compute final composite score               (calcEngine)
    5. Optimise portfolio allocation               (portfolioOptimizer)
    6. Save incrementally to stockData.json

Run:
    python main.py

Resumable: Already-processed symbols are skipped automatically.
To re-run everything, clear stockData.json first.
"""

import json
import random
import threading
import time
from concurrent.futures import ThreadPoolExecutor, as_completed

from aiAnalysis import get_ai_analysis
from calcEngine import calculate_weighted_score
from portfolioOptimizer import allocate_portfolio, get_broad_sector
from processData import getRatios
from stockFetch import getStockData

# ── Configuration ────────────────────────────────────────────────────────────

DATA_FILE = "stockData.json"
WEBSITE_DATA_FILE = "website/data/stockData.json"
STOCK_LIST_FILE = "listOfStocks.json"
MAX_WORKERS = 5

# ── Persistence ─────────────────────────────────────────────────────────────

def _load_existing() -> list[dict]:
    try:
        with open(DATA_FILE) as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return []


def _save(results: list[dict]) -> None:
    """Writes results to stockData.json and the website data mirror."""
    with open(DATA_FILE, "w") as f:
        json.dump(results, f, indent=4)
    try:
        with open(WEBSITE_DATA_FILE, "w") as f:
            json.dump(results, f, indent=4)
    except FileNotFoundError:
        pass  # Website data directory may not exist yet


# ── Per-stock Processing ─────────────────────────────────────────────────────

def _process_stock(symbol: str) -> dict | None:
    """Fetches, processes, and scores a single stock. Returns None on failure."""
    time.sleep(random.uniform(2, 5))  # Polite rate-limit buffer
    print(f"  Analysing {symbol}...")

    try:
        raw = getStockData(symbol)
        if not raw:
            return None

        processed = getRatios(raw)
        if not processed:
            return None

        ai = get_ai_analysis(symbol)

        # Merge AI qualitative scores into the scores dict
        scores = processed["scores"]
        scores["moat_score"] = (ai.get("customer_satisfaction", 50) + ai.get("moat", 50)) / 2
        scores["tailwind_score"] = ai.get("tailwind", 50)
        scores["management_score"] = ai.get("management_quality", 50)

        processed["final_score"] = calculate_weighted_score(scores)
        processed["ai_notes"] = ai.get("notes", "")

        return processed

    except Exception as e:
        print(f"  [ERROR] {symbol}: {e}")
        return None


# ── Portfolio Rebalance ──────────────────────────────────────────────────────

def _rebalance(results: list[dict]) -> list[dict]:
    """Reassigns portfolio weights and broad sectors to all results."""
    valid = [r for r in results if "final_score" in r]

    # Assign broad sector classification
    for r in valid:
        r["Broad Sector"] = get_broad_sector(r.get("Sector", "Other"))

    # Reset weights, then assign from optimizer
    for r in valid:
        r["portfolio_weight"] = 0.0

    try:
        for alloc in allocate_portfolio(valid):
            match = next((r for r in valid if r["symbol"] == alloc["symbol"]), None)
            if match:
                match["portfolio_weight"] = alloc["final_weight"]
    except Exception as e:
        print(f"  [WARN] Portfolio rebalance error: {e}")

    valid.sort(key=lambda x: x.get("final_score", 0), reverse=True)
    return valid


# ── Main ─────────────────────────────────────────────────────────────────────

def main() -> None:
    print("=" * 60)
    print("  Quant Stock Analysis Pipeline")
    print("=" * 60)

    try:
        with open(STOCK_LIST_FILE) as f:
            all_symbols: list[str] = json.load(f)
    except FileNotFoundError:
        print(f"Stock list not found: {STOCK_LIST_FILE}")
        print("Run:  python updateStockList.py")
        return

    existing = _load_existing()
    processed_symbols = {r["symbol"] for r in existing}
    pending = [s for s in all_symbols if s not in processed_symbols]

    if not pending:
        print("All stocks already processed. Re-balancing portfolio...")
        final = _rebalance(existing)
        _save(final)
        print(f"Done. {len(final)} stocks in universe.")
        return

    print(f"Total stocks:     {len(all_symbols)}")
    print(f"Already done:     {len(processed_symbols)}")
    print(f"Remaining:        {len(pending)}")
    print("-" * 60)

    results = list(existing)  # mutable copy
    save_lock = threading.Lock()

    def worker(symbol: str) -> None:
        result = _process_stock(symbol)
        with save_lock:
            if result:
                results.append(result)
                print(f"  ✓ {symbol} | Score: {result.get('final_score')}")
                balanced = _rebalance(results)
                _save(balanced)
                # Reflect rebalanced weights back into results list
                results.clear()
                results.extend(balanced)
            else:
                print(f"  ✗ {symbol} – skipped")
                time.sleep(random.uniform(8, 15))  # Extra backoff on failure

    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as pool:
        futures = {pool.submit(worker, s): s for s in pending}
        for future in as_completed(futures):
            try:
                future.result()
            except Exception as exc:
                print(f"  [THREAD ERROR] {futures[future]}: {exc}")

    print("=" * 60)
    print(f"Pipeline complete. {len(results)} stocks in universe.")


if __name__ == "__main__":
    main()