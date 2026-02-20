import requests
from bs4 import BeautifulSoup
import pandas as pd

BASE_URL = "https://www.screener.in/company/{}/consolidated/"

HEADERS = {
    "User-Agent": "Mozilla/5.0"
}

def fetch_page(symbol):
    url = BASE_URL.format(symbol)
    res = requests.get(url, headers=HEADERS)
    if res.status_code != 200:
        raise Exception("Failed to fetch page")
    return BeautifulSoup(res.text, "lxml")


def get_ratios(soup):
    ratios = {}

    top = soup.find_all("li", class_="flex flex-space-between")

    for item in top:
        key = item.find("span", class_="name").text.strip()
        value = item.find("span", class_="number").text.strip()
        ratios[key] = value

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
    soup = fetch_page(symbol)

    data = {}

    # Ratios
    data["ratios"] = get_ratios(soup)

    # Tables
    data["profit_loss"] = parse_table(soup, "profit-loss")
    data["balance_sheet"] = parse_table(soup, "balance-sheet")
    data["cash_flow"] = parse_table(soup, "cash-flow")

    return data
