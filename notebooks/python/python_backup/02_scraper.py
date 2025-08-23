# 02_scraper.py
# This script downloads daily weather data for all stations defined in 01_config.py.

import requests
import pandas as pd
import time
import io
import os
import sys
from datetime import datetime
import importlib

# --- Configuration ---
# Add the script's directory to the Python path to ensure robust module loading,
# especially when the script is run from a different working directory.
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import the CITIES dictionary from our configuration file
try:
    # Standard 'import' fails for module names starting with a number (e.g., '01_config').
    # We use importlib to load the module programmatically by its string name.
    config_module = importlib.import_module("01_config")
    CITIES = config_module.CITIES
except (ImportError, ModuleNotFoundError):
    print("--- CONFIGURATION ERROR ---")
    print("Error: Could not import the 'CITIES' dictionary from '01_config.py'.")
    print("Please ensure '01_config.py' exists in the same directory as this script.")
    exit()

print("--- Weather Data Scraper ---")

# --- Constants ---
DELAY_BETWEEN_REQUESTS = 1  # seconds
BASE_URL = "https://climate.weather.gc.ca/climate_data/bulk_data_e.html"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
}

# --- Path Setup ---
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(os.path.dirname(SCRIPT_DIR))
RAW_DATA_DIR = os.path.join(PROJECT_ROOT, "data", "raw")
os.makedirs(RAW_DATA_DIR, exist_ok=True)

# --- Main Scraping Logic ---
current_year = datetime.now().year

for city_name, stations in CITIES.items():
    for station_info in stations:
        station_id = station_info["station_id"]
        station_name = station_info["station_name"]
        start_year = station_info["start_year"]
        # Ensure we don't try to fetch data for future years
        end_year = min(station_info["end_year"], current_year)

        print(f"\nProcessing: {city_name} - {station_name} (ID: {station_id})")
        print(f"Years: {start_year} to {end_year}")

        station_dir = os.path.join(RAW_DATA_DIR, f"{city_name}_{station_name}")
        os.makedirs(station_dir, exist_ok=True)

        for year in range(start_year, end_year + 1):
            params = {
                "format": "csv",
                "stationID": station_id,
                "Year": year,
                "timeframe": 2,  # 2 for Daily data
            }

            output_filepath = os.path.join(station_dir, f"{year}_daily_weather.csv")
            print(f"  Fetching data for {year}...")

            try:
                response = requests.get(BASE_URL, params=params, headers=HEADERS)
                response.raise_for_status()  # Raises an HTTPError for bad responses

                # The number of header lines for daily data is 25.
                # Using skiprows=24 was causing the header row to be skipped.
                # We use read_csv directly on the response content
                df = pd.read_csv(io.StringIO(response.text), skiprows=25)
                df.to_csv(output_filepath, index=False)
                print(f"    -> Saved to {output_filepath}")

            except requests.exceptions.RequestException as e:
                print(f"    ERROR: Could not download data for {year}. Reason: {e}")
            except pd.errors.EmptyDataError:
                print(f"    WARNING: No data available for {year}. The file is empty.")
            except Exception as e:
                print(f"    An unexpected error occurred for {year}: {e}")

            time.sleep(DELAY_BETWEEN_REQUESTS)

print("\n--- Scraping complete! ---")
