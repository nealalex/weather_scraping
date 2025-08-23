"""
Configuration file for weather station data collection.
Add or modify city entries as needed.
"""

CITIES = {
    "Calgary": [
        {
            "station_id": 2205,
            "station_name": "CALGARY_INTL_AAB",
            "start_year": 1953,
            "end_year": 2012,
            "data_type": "hourly"
        },
        {
            "station_id": 50430,
            "station_name": "CALGARY_INTL_A",
            "start_year": 2012,
            "end_year": 2025,
            "data_type": "hourly"
        }
    ],
    "Fort St. John": [
        {
            "station_id": 1413,
            "station_name": "FORT_ST_JOHN_A",
            "start_year": 1953,
            "end_year": 2012,
            "data_type": "hourly"
        },
        {
            "station_id": 55198,
            "station_name": "FORT_ST_JOHN_AIRPORT",
            "start_year": 2021,
            "end_year": 2025,
            "data_type": "hourly"
        }
    ],
    "Vancouver": [
        {
            "station_id": 51442,
            "station_name": "VANCOUVER_INTL_A",
            "start_year": 2013,
            "end_year": 2025,
            "data_type": "hourly"
        }
    ],
}