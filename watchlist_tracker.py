import requests
import dotenv
from dotenv import load_dotenv
import openpyxl
import sqlite3
import pathlib
import json
import os
import time

load_dotenv()
API_KEY = os.getenv("API_KEY")
symbols = ["AUD/USD", "EUR/USD", "EUR/JPY", "GBP/USD", "USD/JPY", "USD/CAD",
            "BTC/USD"]

def fetch_price_data(symbol , api_key):

    BASE_URL = (
        "https://api.twelvedata.com/time_series"
        "?apikey=" + api_key +
        "&symbol=" + symbol +
        "&interval=1min" +
        "&outputsize=1" +
        "&timezone=America/Argentina/Rio_Gallegos" +
        "&start_date=2026-07-12T14:07:00" +
        "&end_date=2026-07-12T14:08:00" +
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

def fetch_watchlist_data(symbols, api_key):

    watchlist_data = {}

    for symbol in symbols:
        response = fetch_price_data(symbol, api_key)
        if not response:
            print(f"Could not fetch: {symbol} data")
            continue
        watchlist_data[symbol] = response
        time.sleep(8)

    return watchlist_data


watch_data = fetch_watchlist_data(symbols, API_KEY)
