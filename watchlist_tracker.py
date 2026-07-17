import requests
import dotenv
from dotenv import load_dotenv
import openpyxl
import sqlite3
import pathlib
import json
import os
import time
from datetime import datetime, timezone
from pathlib import Path
import shutil


load_dotenv()
API_KEY = os.getenv("API_KEY")
symbols = ["AUD/USD", "EUR/USD", "EUR/JPY", "GBP/USD", "USD/JPY", "USD/CAD", "BTC/USD"]
today_date = datetime.now(timezone.utc)
raw_data_file_name = f"{str(today_date.date())}_raw.json"
base_path = Path.cwd()
raw_data_path = base_path / "data" / "raw" / raw_data_file_name
db_path = base_path / "data" / "database"


def fetch_price_data(symbol, api_key):

    BASE_URL = (
        "https://api.twelvedata.com/time_series"
        "?apikey="
        + api_key
        + "&symbol="
        + symbol
        + "&interval=1day"
        + "&outputsize=1"
        + "&timezone=America/New_York"
        + "&format=JSON"
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


def save_raw_json(watchlist_data, raw_data_file_name, raw_data_path):
    raw_folder_path = Path.cwd() / "data" / "raw"
    try:
        raw_folder_path.mkdir(parents=True, exist_ok=True)
        with open(raw_data_path, "w") as file:
            json.dump(watchlist_data, file)
        print(f"{raw_data_file_name} written to {raw_data_path}")
        return True
    except OSError as e:
        print(f"Failed to write Json file: {e}")
        return False


def load_raw_json(filepath):
    try:
        with open(filepath, "r") as file:
            return json.load(file)
    except OSError as e:
        print(f"The specific file does not exist {e}")
        return None
    except json.JSONDecodeError as e:
        print(f"The file exists but isn't valid JSON: {e}")
        return None


def parse_watchlist_data(json_file_content):

    symbols_data_list = []

    for symbol in json_file_content:
        symbol_data = json_file_content[symbol]

        if symbol_data is None:
            print(f"Skipping {symbol}: no data was fetched for this symbol")
        try:
            trades_data = {
                "instrument": symbol,
                "date": symbol_data["values"][0]["datetime"],
                "open": float(symbol_data["values"][0]["open"]),
                "high": float(symbol_data["values"][0]["high"]),
                "low": float(symbol_data["values"][0]["low"]),
                "close": float(symbol_data["values"][0]["close"]),
            }
            symbols_data_list.append(trades_data)
        except KeyError as e:
            print(f"Json file content is missing an expected field: {e}")
            continue

    return symbols_data_list


def build_date_folder(base_path, date):

    year = date.strftime("%Y")
    month = date.strftime("%m")
    folder_path = base_path / "data" / year / month

    try:
        folder_path.mkdir(parents=True, exist_ok=True)
    except OSError as e:
        print(f"Failed to create folder: {e}")
        return None

    return folder_path


def archive_daily_files(source_paths, destination_folder):

    if destination_folder is None:
        print("Cannot archive files: destination folder was not created")
        return None

    for source_path in source_paths:
        try:
            shutil.move(source_path, destination_folder)
        except OSError as e:
            print(f"Could not move {source_path} to destination folder: {e}")
            return

    return destination_folder

def init_database(db_path):

    db_file = "watchlist_history.db"

    try:
        db_path.mkdir(parents=True, exist_ok=True)
    except OSError as e:
        print(f"Failed to create folder: {e}")
        return None

    connection = sqlite3.connect(db_path / db_file)
    cursor = connection.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS daily_prices (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            instrument TEXT NOT NULL,
            date TEXT,
            open REAL,
            high REAL,
            low REAL,
            close REAL    
        )
    """)

    connection.commit()
    connection.close()

    return db_path / db_file



# fetch_price_data("XAU/USD" , API_KEY)
# watchlist_data = fetch_watchlist_data(symbols, API_KEY)
# save_raw_json(watchlist_data, raw_data_file_name, raw_data_path)
# json_file_content = load_raw_json(raw_data_path)
# symbols_data_list = parse_watchlist_data(json_file_content)

# folder_path = build_date_folder(base_path, today_date)
# archive_daily_files([raw_data_path], folder_path)

database_file_path = init_database(db_path)
print(database_file_path)