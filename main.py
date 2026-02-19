import json
import time
import listOfStocks # type: ignore
from stockFetch import stockFetchData


results = []

# Fetch stock data for each stock in the list

for stock in listOfStocks.stocks:
    result = stockFetchData(stock)
    results.append(result)
    time.sleep(1)


# store in json file
with open('stockData.json', 'w') as f:
    json.dump(results, f, indent=4)



print("Done")