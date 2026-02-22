"""
stockFetch.py
--------------
Scrapes financial data for Indian equities from screener.in.
Data extracted includes: key ratios, company profile, P&L, balance sheet,
cash flow, and shareholding tables.
"""

import random
import time

import pandas as pd
import requests
from bs4 import BeautifulSoup
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

BASE_URL = "https://www.screener.in/company/{}/consolidated/"

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/119.0",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
]

# Shared session with retry logic
def _build_session() -> requests.Session:
    session = requests.Session()
    retry = Retry(
        total=3,
        backoff_factor=1.5,
        status_forcelist=[429, 500, 502, 503, 504],
    )
    adapter = HTTPAdapter(max_retries=retry)
    session.mount("https://", adapter)
    session.mount("http://", adapter)
    return session

SESSION = _build_session()


def _fetch_page(symbol: str) -> BeautifulSoup:
    """Fetches and parses the screener.in page for a given symbol."""
    url = BASE_URL.format(symbol)
    headers = {
        "User-Agent": random.choice(USER_AGENTS),
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5",
        "DNT": "1",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1",
    }
    # Polite jitter delay to avoid rate limits
    time.sleep(random.uniform(5, 10))
    res = SESSION.get(url, headers=headers, timeout=30)
    if res.status_code != 200:
        raise ConnectionError(f"HTTP {res.status_code} for {symbol}")
    return BeautifulSoup(res.text, "html.parser")


def _parse_ratios(soup: BeautifulSoup) -> dict:
    """Extracts key ratios from the top panel and sector from peer links."""
    ratios = {}
    for item in soup.find_all("li", class_="flex flex-space-between"):
        try:
            key = item.find("span", class_="name").text.strip()
            val = item.find("span", class_="number").text.strip()
            ratios[key] = val
        except AttributeError:
            continue

    # Sector from peers section (most reliable)
    try:
        peers = soup.find("section", {"id": "peers"})
        if peers:
            links = peers.find_all("a", href=lambda x: x and "/market/" in x)
            if links:
                ratios["Sector"] = links[0].text.strip()
    except Exception:
        pass

    # Fallback: breadcrumb
    if "Sector" not in ratios:
        try:
            bc = soup.find("p", class_="breadcrumb")
            if bc:
                links = bc.find_all("a")
                if len(links) >= 2:
                    ratios["Sector"] = links[1].text.strip()
        except Exception:
            pass

    return ratios


def _parse_table(soup: BeautifulSoup, section_id: str) -> list[dict]:
    """Parses a financial table (P&L, Balance Sheet, etc.) into a list of row dicts."""
    section = soup.find("section", {"id": section_id})
    if not section:
        return []
    table = section.find("table")
    if not table:
        return []

    headers = [th.text.strip() for th in table.find_all("th")][1:]
    rows = []
    for tr in table.find_all("tr")[1:]:
        cols = [td.text.strip().replace(",", "") for td in tr.find_all("td")]
        if cols:
            row = {"Metric": cols[0]}
            row.update(dict(zip(headers, cols[1:])))
            rows.append(row)
    return rows


def _parse_company_profile(soup: BeautifulSoup) -> tuple[str, str]:
    """Returns (company_full_name, about_text) from the page."""
    name = ""
    about = ""

    try:
        name = soup.find("h1").text.strip()
    except Exception:
        pass

    try:
        profile_div = soup.find("div", class_="company-profile")
        if profile_div:
            raw = profile_div.text
            # Strip junk headers
            for token in ("About", "Key Points", "Read More"):
                raw = raw.replace(token, "")
            about = raw.strip()
    except Exception:
        pass

    return name, about


def getStockData(symbol: str) -> dict | None:
    """
    Main entry point. Fetches all data for a symbol from screener.in.

    Returns a dict with keys:
        symbol, Company Name, About, ratios, pnl, balance_sheet, cash_flow, shareholding
    Returns None on failure.
    """
    try:
        soup = _fetch_page(symbol)
    except Exception as e:
        print(f"  [FETCH ERROR] {symbol}: {e}")
        return None

    try:
        company_name, about = _parse_company_profile(soup)
        ratios = _parse_ratios(soup)

        return {
            "symbol": symbol,
            "Company Name": company_name or symbol,
            "About": about or "N/A",
            "ratios": ratios,
            "pnl": _parse_table(soup, "profit-loss"),
            "balance_sheet": _parse_table(soup, "balance-sheet"),
            "cash_flow": _parse_table(soup, "cash-flow"),
            "shareholding": _parse_table(soup, "shareholding"),
        }
    except Exception as e:
        print(f"  [PARSE ERROR] {symbol}: {e}")
        return None
