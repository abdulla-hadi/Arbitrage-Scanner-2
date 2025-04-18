
from flask import Flask, render_template
import requests

app = Flask(__name__)

def get_arbitrage_opportunities():
    url = "https://api.coingecko.com/api/v3/exchanges"
    exchanges = requests.get(url).json()
    tickers_url = "https://api.coingecko.com/api/v3/coins/markets?vs_currency=usd&order=volume_desc&per_page=50&page=1"
    coins = requests.get(tickers_url).json()

    opportunities = []
    for coin in coins:
        if 'id' not in coin:
            continue
        coin_id = coin['id']
        coin_tickers = requests.get(f"https://api.coingecko.com/api/v3/coins/{coin_id}/tickers").json()
        prices = {}
        for ticker in coin_tickers.get("tickers", []):
            market = ticker["market"]["name"]
            price = ticker["converted_last"].get("usd")
            volume = ticker["converted_volume"].get("usd", 0)
            if price and volume > 10000:
                prices[market] = price

        if len(prices) >= 2:
            min_ex = min(prices, key=prices.get)
            max_ex = max(prices, key=prices.get)
            min_price = prices[min_ex]
            max_price = prices[max_ex]
            spread = (max_price - min_price) / min_price * 100

            if spread > 1:
                opportunities.append({
                    "symbol": coin["symbol"].upper(),
                    "name": coin["name"],
                    "min_exchange": min_ex,
                    "max_exchange": max_ex,
                    "min_price": round(min_price, 4),
                    "max_price": round(max_price, 4),
                    "spread": round(spread, 2)
                })

    sorted_opps = sorted(opportunities, key=lambda x: x["spread"], reverse=True)
    return sorted_opps[:20]

@app.route("/")
def index():
    data = get_arbitrage_opportunities()
    return render_template("index.html", data=data)
