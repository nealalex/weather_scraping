# 01_config.py
# Central configuration for cities and their weather stations for DAILY data.
#
# To find more stations:
# 1. Go to: https://climate.weather.gc.ca/historical_data/search_e.html
# 2. Find your desired station.
# 3. The "Station ID" is what you need for the 'station_id' field below.
# 4. Check the available years for "Daily" data and set 'start_year' and 'end_year'.

CITIES = {
    "Calgary": [
        {
            "station_name": "CALGARY_INTL_A",
            "station_id": 50430,
            "start_year": 1990,
            "end_year": 2023,
        }
    ],
    "Toronto": [
        {
            "station_name": "TORONTO_PEARSON_INTL_A",
            "station_id": 51459,
            "start_year": 1990,
            "end_year": 2023,
        }
    ],
    "Vancouver": [
        {
            "station_name": "VANCOUVER_INTL_A",
            "station_id": 51442,
            "start_year": 1990,
            "end_year": 2023,
        }
    ],
    "Montreal": [
        {
            "station_name": "MONTREAL_TRUDEAU_INTL_A",
            "station_id": 51157,
            "start_year": 1990,
            "end_year": 2023,
        }
    ],
}
