import requests
import dotenv
from dotenv import load_dotenv
import openpyxl
import sqlite3
import pathlib
import json
import os
import time
from datetime import datetime, timedelta
from pathlib import Path

load_dotenv()
API_KEY = os.getenv("API_KEY")
symbols = ["AUD/USD", "EUR/USD", "EUR/JPY", "GBP/USD", "USD/JPY", "USD/CAD",
            "BTC/USD"]
now = datetime.now() - timedelta(days=1)
start_date_custom_time = now.replace(hour=14, minute=7, second=0, microsecond=0)
end_date_custom_time = now.replace(hour=14, minute=8, second=0, microsecond=0)

start_date = start_date_custom_time.isoformat()
end_date = end_date_custom_time.isoformat()

def fetch_price_data(symbol , api_key, start_date, end_date):

    BASE_URL = (
        "https://api.twelvedata.com/time_series"
        "?apikey=" + api_key +
        "&symbol=" + symbol +
        "&interval=1min" +
        "&outputsize=1" +
        "&timezone=America/Argentina/Rio_Gallegos" +
        "&start_date=" + start_date +
        "&end_date=" + end_date +
        "&format=JSON"
    )

    try:
        response = requests.get(BASE_URL, timeout=10)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.ConnectionError:
        print("Network error - could not reach the Twelvedata API")
        return None
    except requests.exceptions.Timeout:
        print("Request timed out - the API took too long to respond")
        return None
    except requests.exceptions.HTTPError as e:
        print(f"API returned an error: {e}")
        return None

def fetch_watchlist_data(symbols, api_key, start_date, end_date):

    watchlist_data = {}

    for symbol in symbols:
        response = fetch_price_data(symbol, api_key, start_date, end_date)
        if not response:
            print(f"Could not fetch: {symbol} data")
            continue
        watchlist_data[symbol] = response
        time.sleep(8)

    return watchlist_data


watchlist_data = fetch_watchlist_data(symbols, API_KEY, start_date, end_date)


data = Path.cwd() / "data" / "raw"
raw_data_file_name = f"{str(now.date())}_raw.json"

if not data.exists():
    data.mkdir(parents=True, exist_ok=True)

try:
    with open(data/raw_data_file_name, "w") as file:
        json.dump(watchlist_data, file)
    print(f"{raw_data_file_name} written to {data}")
except OSError as e:
    print(f"Failed to write Json file: {e}")


