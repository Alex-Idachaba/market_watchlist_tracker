import requests
import dotenv
from dotenv import load_dotenv
import openpyxl
import sqlite3
import pathlib
import json
import os

load_dotenv()
API_KEY = os.getenv("API_KEY")

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

response = fetch_price_data("XAU/USD", API_KEY)
print(response)