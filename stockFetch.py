import requests
from bs4 import BeautifulSoup
import pandas as pd
import json
import random
import time
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

BASE_URL = "https://www.screener.in/company/{}/consolidated/"

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/119.0",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36"
]

def get_session():
    session = requests.Session()
    retry = Retry(
        total=3,
        backoff_factor=1,
        status_forcelist=[429, 500, 502, 503, 504],
    )
    adapter = HTTPAdapter(max_retries=retry)
    session.mount("https://", adapter)
    session.mount("http://", adapter)
    return session

SESSION = get_session()

def fetch_page(symbol):
    url = BASE_URL.format(symbol)
    headers = {
        "User-Agent": random.choice(USER_AGENTS),
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5",
        "DNT": "1",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1"
    }
    # Add a jitter delay before every request
    time.sleep(random.uniform(5, 10))
    
    res = SESSION.get(url, headers=headers, timeout=30)
    if res.status_code != 200:
        raise Exception(f"Failed to fetch page: HTTP {res.status_code}")
    return BeautifulSoup(res.text, "html.parser")


def get_ratios(soup):
    ratios = {}

    top = soup.find_all("li", class_="flex flex-space-between")

    for item in top:
        key = item.find("span", class_="name").text.strip()
        value = item.find("span", class_="number").text.strip()
        ratios[key] = value

    # Also try to get Sector and Industry
    try:
        peers = soup.find("div", {"id": "peers"})
        if peers:
            links = peers.find_all("a")
            # Usually Breadcrumbs or Peers section has sector/industry links
            # More reliable: look for the breadcrumb at the top
            breadcrumb = soup.find("p", class_="breadcrumb")
            if breadcrumb:
                links = breadcrumb.find_all("a")
                if len(links) >= 3:
                    ratios["Sector"] = links[1].text.strip()
                    ratios["Industry"] = links[2].text.strip()
    except:
        pass

    return ratios


def parse_table(soup, section_id):
    section = soup.find("section", {"id": section_id})
    table = section.find("table")

    headers = [th.text.strip() for th in table.find_all("th")][1:]

    rows = []
    for tr in table.find_all("tr")[1:]:
        cols = [td.text.strip().replace(",", "") for td in tr.find_all("td")]
        if cols:
            rows.append(cols)

    df = pd.DataFrame(rows, columns=["Metric"] + headers)
    return df


def getStockData(symbol):
    try:
        soup = fetch_page(symbol)
        data = {'symbol': symbol}
        
        # 1. Basic Ratios from top panel
        ratios = get_ratios(soup)
        data['ratios'] = ratios
        
        # 2. Financial Tables
        try:
            data['pnl'] = parse_table(soup, "profit-loss").to_dict('records')
        except: data['pnl'] = []
            
        try:
            data['balance_sheet'] = parse_table(soup, "balance-sheet").to_dict('records')
        except: data['balance_sheet'] = []
            
        try:
            data['cash_flow'] = parse_table(soup, "cash-flow").to_dict('records')
        except: data['cash_flow'] = []

        try:
            data['shareholding'] = parse_table(soup, "shareholding").to_dict('records')
        except: data['shareholding'] = []

        return data
    except Exception as e:
        print(f"Error fetching data for {symbol}: {e}")
        return None
