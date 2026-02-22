"""
patch_stockdata.py
-------------------
One-shot patch for existing stockData.json to:
  1. Fill Company Name from NSE official list (fast, no scraping)
  2. Re-scrape D/E + About for stocks with D/E == 0 (targeted scrape)
  3. Recalculate fii_dii_de_score using corrected D/E
  4. Recalculate final_score
  5. Re-run portfolio allocation
  6. Save to both output locations

Usage:
    python patch_stockdata.py              # Names + D/E re-scrape + recalc
    python patch_stockdata.py --names-only # Only fill missing Company Names
"""

import argparse
import csv
import io
import json
import random
import time
from concurrent.futures import ThreadPoolExecutor, as_completed

import requests
from bs4 import BeautifulSoup

from calcEngine import calculate_weighted_score
from portfolioOptimizer import allocate_portfolio, get_broad_sector

DATA_FILE = "stockData.json"
WEBSITE_DATA_FILE = "website/data/stockData.json"
NSE_CSV_URL = "https://archives.nseindia.com/content/equities/EQUITY_L.csv"

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/119.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 Chrome/118.0.0.0 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/119.0.0.0 Safari/537.36",
]


# ── Helpers ─────────────────────────────────────────────────────────────────

def _load() -> list[dict]:
    with open(DATA_FILE) as f:
        return json.load(f)


def _save(data: list[dict]) -> None:
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=4)
    try:
        with open(WEBSITE_DATA_FILE, "w") as f:
            json.dump(data, f, indent=4)
    except FileNotFoundError:
        pass
    print(f"  Saved {len(data)} records.")


def _get_nse_name_map() -> dict[str, str]:
    """Fetches symbol → full company name mapping from NSE's equity list CSV."""
    print("  Fetching NSE name list...")
    res = requests.get(
        NSE_CSV_URL,
        headers={"User-Agent": USER_AGENTS[0]},
        timeout=15,
    )
    res.raise_for_status()
    reader = csv.DictReader(io.StringIO(res.content.decode("utf-8")))
    return {
        row["SYMBOL"].strip(): row["NAME OF COMPANY"].strip()
        for row in reader
        if row.get("SYMBOL")
    }


def _clean_float(val, default=0.0) -> float:
    try:
        return float(str(val).replace(",", "").replace("%", "").strip())
    except (ValueError, TypeError):
        return default


# ── 1. Fill Company Names ────────────────────────────────────────────────────

def fill_company_names(data: list[dict], name_map: dict[str, str]) -> int:
    changed = 0
    for rec in data:
        sym = rec["symbol"]
        current_name = rec.get("Company Name", "")
        # Patch if: missing, same as symbol, or obviously wrong
        if not current_name or current_name == sym:
            if sym in name_map:
                rec["Company Name"] = name_map[sym]
                changed += 1
    return changed


# ── 2. Re-scrape D/E + About for Zero Records ───────────────────────────────

def _scrape_de_and_about(symbol: str) -> tuple[float, str, str]:
    """
    Returns (de_ratio, about_text, company_name) from screener.in.
    Falls back gracefully on any error.
    """
    time.sleep(random.uniform(5, 10))
    url = f"https://www.screener.in/company/{symbol}/consolidated/"
    headers = {"User-Agent": random.choice(USER_AGENTS)}

    try:
        res = requests.get(url, headers=headers, timeout=20)
        if res.status_code != 200:
            return 0.0, "", ""

        soup = BeautifulSoup(res.text, "html.parser")

        # Company name
        name = ""
        try:
            name = soup.find("h1").text.strip()
        except Exception:
            pass

        # About
        about = ""
        try:
            prof = soup.find("div", class_="company-profile")
            if prof:
                raw = prof.text
                for token in ("About", "Key Points", "Read More"):
                    raw = raw.replace(token, "")
                about = raw.strip()
        except Exception:
            pass

        # D/E from balance sheet table
        de = 0.0
        try:
            bs_section = soup.find("section", {"id": "balance-sheet"})
            if bs_section:
                rows = bs_section.find_all("tr")
                borrowings = equity = reserves = 0.0
                for tr in rows:
                    cells = [td.text.strip().replace(",", "") for td in tr.find_all("td")]
                    if not cells:
                        continue
                    label = cells[0].lower()
                    values = [_clean_float(c) for c in cells[1:] if c]
                    if not values:
                        continue
                    last = values[-1]
                    if "borrowings" in label:
                        borrowings = last
                    elif "equity capital" in label:
                        equity = last
                    elif "reserves" in label:
                        reserves = last

                net_worth = equity + reserves
                if net_worth > 0:
                    de = round(borrowings / net_worth, 2)
        except Exception:
            pass

        return de, about, name

    except Exception as e:
        print(f"    [SCRAPE ERROR] {symbol}: {e}")
        return 0.0, "", ""


def fix_zero_de(data: list[dict], name_map: dict[str, str], workers: int = 5) -> int:
    """Re-scrapes D/E for all records with D/E == 0."""
    targets = [r for r in data if r.get("D/E", 0) == 0]
    if not targets:
        print("  No zero D/E records found.")
        return 0

    print(f"  Re-scraping D/E + About for {len(targets)} zero-D/E stocks...")
    index = {r["symbol"]: r for r in data}
    changed = 0

    def worker(rec):
        sym = rec["symbol"]
        de, about, scraped_name = _scrape_de_and_about(sym)
        updates = {}
        if de > 0:
            updates["D/E"] = de
            # Recalculate fii_dii_de_score
            fii = rec.get("FII (%)", 0)
            dii = rec.get("DII (%)", 0)
            de_score = max(0.0, 100.0 - de * 50)
            fii_dii_score = min(100.0, fii + dii)
            updates["scores"] = dict(rec.get("scores", {}))
            updates["scores"]["fii_dii_de_score"] = round((de_score + fii_dii_score) / 2, 4)
        if about and about != "N/A":
            updates["About"] = about
        if scraped_name and scraped_name != sym and rec.get("Company Name", sym) == sym:
            updates["Company Name"] = scraped_name
        # Also try NSE map as fallback for name
        if rec.get("Company Name", sym) == sym and sym in name_map:
            updates["Company Name"] = name_map[sym]
        return sym, updates

    with ThreadPoolExecutor(max_workers=workers) as pool:
        futures = {pool.submit(worker, r): r["symbol"] for r in targets}
        for i, future in enumerate(as_completed(futures)):
            sym, updates = future.result()
            if updates:
                rec = index[sym]
                rec.update(updates)
                if "D/E" in updates:
                    changed += 1
                    print(f"    [{i+1}/{len(targets)}] {sym} → D/E={updates['D/E']}")
                else:
                    print(f"    [{i+1}/{len(targets)}] {sym} → D/E still 0 (debt-free?)")
            else:
                print(f"    [{i+1}/{len(targets)}] {sym} → scrape failed")

    return changed


# ── 3. Recalculate Scores + Rebalance Portfolio ──────────────────────────────

def recalculate_and_rebalance(data: list[dict]) -> list[dict]:
    """Recomputes final_score from existing sub-scores and re-runs allocation."""
    print("  Recalculating scores and rebalancing portfolio...")

    for rec in data:
        scores = rec.get("scores", {})
        rec["final_score"] = calculate_weighted_score(scores)
        rec["Broad Sector"] = get_broad_sector(rec.get("Sector", "Other"))
        rec["portfolio_weight"] = 0.0

    data.sort(key=lambda x: x.get("final_score", 0), reverse=True)

    try:
        allocs = allocate_portfolio(data)
        alloc_map = {a["symbol"]: a["final_weight"] for a in allocs}
        for rec in data:
            rec["portfolio_weight"] = alloc_map.get(rec["symbol"], 0.0)
    except Exception as e:
        print(f"  [WARN] Allocation error: {e}")

    return data


# ── Main ─────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--names-only", action="store_true", help="Only fill missing Company Names")
    args = parser.parse_args()

    data = _load()
    print(f"Loaded {len(data)} records from {DATA_FILE}\n")

    name_map = _get_nse_name_map()

    # Step 1: Fill names
    n = fill_company_names(data, name_map)
    print(f"  Filled Company Name for {n} symbols.\n")

    if not args.names_only:
        # Step 2: Fix D/E
        changed = fix_zero_de(data, name_map, workers=5)
        print(f"\n  Fixed D/E for {changed} records.\n")

        # Step 3: Recalculate scores + rebalance
        data = recalculate_and_rebalance(data)

    _save(data)
    print("\nDone.")


if __name__ == "__main__":
    main()
