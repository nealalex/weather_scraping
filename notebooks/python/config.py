# config.py
# Central configuration for cities and their weather stations.
# This file supports multiple station IDs for a single city to handle
# cases where station IDs have changed over the years.
#
# To find more stations:
# 1. Go to: https://climate.weather.gc.ca/historical_data/search_e.html
# 2. Find your desired station.
# 3. The "Station ID" is what you need for the 'station_id' field below.
# 4. Check the available years for "Daily" data and set 'start_year' and 'end_year'.

CITIES = {
    "Calgary": [
        {
            "station_id": 2205,
            "station_name": "CALGARY_INTL_A_OLD",
            "start_year": 1953,
            "end_year": 2012,
            "data_type": "daily",
        },
        {
            "station_id": 50430,
            "station_name": "CALGARY_INTL_A",
            "start_year": 2012,
            "end_year": 2025,
            "data_type": "daily",
        },
    ],
    "Fort St. John": [
        {
            "station_id": 1413,
            "station_name": "FORT_ST_JOHN_A",
            "start_year": 1953,
            "end_year": 2012,
            "data_type": "daily",
        },
        {
            "station_id": 55198,
            "station_name": "FORT_ST_JOHN_AIRPORT",
            "start_year": 2021,
            "end_year": 2025,
            "data_type": "daily",
        },
    ],
    "Vancouver": [
        {
            "station_id": 51442,
            "station_name": "VANCOUVER_INTL_A",
            "start_year": 2013,
            "end_year": 2025,
            "data_type": "daily",
        }
    ],
    # --- NEW STATIONS ADDED BELOW ---
"Victoria": [
        {
            "station_id": 1202,
            "station_name": "VICTORIA_INTL_A_OLD", # Renamed to be clear
            "start_year": 1953,
            "end_year": 2013, # Adjusted end year
            "data_type": "daily",
        },
        { # ADD THIS ENTIRE NEW BLOCK
            "station_id": 51337,
            "station_name": "VICTORIA_INTL_A",
            "start_year": 2013,
            "end_year": 2025, # Or your desired end year
            "data_type": "daily",
        }
    ],
    "Edmonton": [
        {
            "station_id": 1867,
            "station_name": "EDMONTON_INTL_A_OLD",
            "start_year": 1960,
            "end_year": 2012,
            "data_type": "daily",
        },
        {
            "station_id": 50149,
            "station_name": "EDMONTON_INTL_CS",
            "start_year": 2012,
            "end_year": 2025,
            "data_type": "daily",
        },
    ],
    "Fredericton": [
        {
            "station_id": 6157,
            "station_name": "FREDERICTON_A_OLD",
            "start_year": 1953,
            "end_year": 2012,
            "data_type": "daily",
        },
        {
            "station_id": 50513,
            "station_name": "FREDERICTON_A",
            "start_year": 2012,
            "end_year": 2025,
            "data_type": "daily",
        },
    ],
    "Regina": [
        {
            "station_id": 3002,
            "station_name": "REGINA_INTL_A_OLD",
            "start_year": 1953,
            "end_year": 2012,
            "data_type": "daily",
        },
        {
            "station_id": 50420,
            "station_name": "REGINA_INTL_A",
            "start_year": 2012,
            "end_year": 2025,
            "data_type": "daily",
        },
    ],
    "Toronto": [
        {
            "station_id": 5097,
            "station_name": "TORONTO_PEARSON_INTL_A_OLD",
            "start_year": 1953,
            "end_year": 2013,
            "data_type": "daily",
        },
        {
            "station_id": 51459,
            "station_name": "TORONTO_PEARSON_INTL_A",
            "start_year": 2013,
            "end_year": 2025,
            "data_type": "daily",
        },
    ],
    "Montreal": [
        {
            "station_id": 5415,
            "station_name": "MONTREAL_TRUDEAU_INTL_A_OLD",
            "start_year": 1953,
            "end_year": 2013,
            "data_type": "daily",
        },
        {
            "station_id": 51157,
            "station_name": "MONTREAL_TRUDEAU_INTL_A",
            "start_year": 2013,
            "end_year": 2025,
            "data_type": "daily",
        },
    ],
}
