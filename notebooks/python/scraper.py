# 02_scraper.py
# This script downloads daily weather data for all stations defined in 01_config.py.
# This version has been updated to be more robust by dynamically finding the header row.

import requests
import pandas as pd
import time
import io
import os
from datetime import datetime

# --- Configuration ---
# Import the CITIES dictionary from our configuration file
try:
    from config import CITIES
except ImportError:
    print("--- CONFIGURATION ERROR ---")
    print("Error: Could not import the 'CITIES' dictionary from 'config.py'.")
    print("Please ensure 'config.py' exists in the same directory as this script.")
    exit()

# --- ADD THIS LINE FOR DEBUGGING ---
print(f"--- Config loaded. Found {len(CITIES)} cities: {list(CITIES.keys())} ---")

print("--- Weather Data Scraper ---")

# --- Constants ---
DELAY_BETWEEN_REQUESTS = 1  # seconds
BASE_URL = "https://climate.weather.gc.ca/climate_data/bulk_data_e.html"
TIMEFRAME_MAP = {
    "hourly": 1,
    "daily": 2,
    "monthly": 3,
}
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
        data_type = station_info.get("data_type", "daily")  # Default to daily
        timeframe = TIMEFRAME_MAP.get(data_type.lower())

        if not timeframe:
            print(f"  WARNING: Invalid data_type '{data_type}' for {station_name}. Skipping.")
            continue
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
                "timeframe": timeframe,
            }

            output_filepath = os.path.join(station_dir, f"{year}_daily_weather.csv")
            print(f"  Fetching data for {year}...")

            try:
                response = requests.get(BASE_URL, params=params, headers=HEADERS)
                response.raise_for_status()  # Raises an HTTPError for bad responses

                # --- MODIFIED SECTION ---
                # Dynamically find the header row instead of using a fixed skiprows value.
                # This makes the scraper more robust if the website changes its format.
                raw_text = response.text
                lines = raw_text.splitlines()

                header_row_index = -1
                for i, line in enumerate(lines):
                    # The correct header contains these key column names. This is more reliable
                    # than checking for just one column like "Year".
                    if '"Date/Time"' in line and '"Max Temp (°C)"' in line and '"Min Temp (°C)"' in line:
                        header_row_index = i
                        break

                if header_row_index == -1:
                    print(f"    WARNING: Could not find header row for {year}. Skipping file.")
                    continue

                # Use the dynamically found header_row_index as the value for skiprows.
                df = pd.read_csv(io.StringIO(raw_text), skiprows=header_row_index)
                # --- END OF MODIFIED SECTION ---

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