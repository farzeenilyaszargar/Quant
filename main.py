import json
import random
import time
from stockFetch import getStockData



stocks = []

# Fetch stock data for each stock in the list

with open("listOfStocks.json", "r") as f:
    stocks = json.load(f)

for stock in stocks:
    result = getStockData(stock)
    print(f"Fetched data for {result}")
    time.sleep(random.uniform(2, 5))  


print("Done")