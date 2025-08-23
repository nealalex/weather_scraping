# merger.py
# This script reads all raw CSV files, merges them, cleans the data,
# and saves two final files for the web application.

import pandas as pd
import os
import glob

print("--- Data Merger and Cleaner ---")

# --- Path Setup ---
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(os.path.dirname(SCRIPT_DIR))
RAW_DATA_DIR = os.path.join(PROJECT_ROOT, "data", "raw")
PROCESSED_DATA_DIR = os.path.join(PROJECT_ROOT, "data", "processed")
os.makedirs(PROCESSED_DATA_DIR, exist_ok=True)

# --- Data Loading and Merging ---
all_dataframes = []
metadata_records = []

if not os.path.exists(RAW_DATA_DIR) or not os.listdir(RAW_DATA_DIR):
    print(f"--- ERROR: RAW DATA NOT FOUND ---")
    print(f"The raw data directory is empty or does not exist: {RAW_DATA_DIR}")
    print(
        "Please run 'scraper.py' first to download the data, then run this script again."
    )
    exit()

print(f"Reading raw data from: {RAW_DATA_DIR}")

# Each subdirectory in 'raw' corresponds to a station
for station_dir in os.listdir(RAW_DATA_DIR):
    full_station_path = os.path.join(RAW_DATA_DIR, station_dir)
    if os.path.isdir(full_station_path):
        # Extract city name from the directory name (e.g., "Calgary_CALGARY_INTL_A")
        city_name = station_dir.split("_")[0]
        print(f"\nProcessing station for city: {city_name}")

        station_files = glob.glob(os.path.join(full_station_path, "*.csv"))
        if not station_files:
            print(f"  No CSV files found for {city_name}. Skipping.")
            continue

        station_dfs = []
        for f in station_files:
            try:
                df = pd.read_csv(f)
                # Add a validation check to ensure the CSV was scraped correctly.
                # If 'Year' is missing, it means the header row was skipped during scraping.
                if "Year" not in df.columns:
                    print(f"\n--- FATAL ERROR in {os.path.basename(f)} ---")
                    print(
                        "The 'Year' column is missing. This indicates the raw data file is corrupted."
                    )
                    print(
                        "Please check the 'skiprows' value in 'scraper.py', delete the contents of 'data/raw', and re-run the pipeline."
                    )
                    exit()
                df["City"] = city_name  # Add city column
                station_dfs.append(df)
            except pd.errors.EmptyDataError:
                print(f"  Warning: Skipping empty file {os.path.basename(f)}")
            except Exception as e:
                print(f"  Error reading {os.path.basename(f)}: {e}")

        if station_dfs:
            city_df = pd.concat(station_dfs, ignore_index=True)
            all_dataframes.append(city_df)
            # Create metadata record
            min_year = city_df["Year"].min()
            max_year = city_df["Year"].max()
            metadata_records.append(
                {"City": city_name, "start_year": min_year, "end_year": max_year}
            )
            print(
                f"  -> Merged {len(station_files)} files for {city_name}. Year range: {min_year}-{max_year}"
            )

if not all_dataframes:
    print("\nNo data was processed. Exiting.")
    exit()

# --- Data Cleaning ---
print("\nConcatenating all city data...")
merged_df = pd.concat(all_dataframes, ignore_index=True)

print("Cleaning data...")
# Rename columns for easier access
merged_df.rename(
    columns={
        "Date/Time": "Date_Time",
        "Max Temp (°C)": "Max_Temp_C",
        "Min Temp (°C)": "Min_Temp_C",
        "Mean Temp (°C)": "Mean_Temp_C",
        "Total Precip (mm)": "Total_Precip_mm",
    },
    inplace=True,
)

# Convert to datetime and numeric types
merged_df["Date_Time"] = pd.to_datetime(merged_df["Date_Time"])
numeric_cols = ["Max_Temp_C", "Min_Temp_C", "Mean_Temp_C", "Total_Precip_mm"]
for col in numeric_cols:
    merged_df[col] = pd.to_numeric(merged_df[col], errors="coerce")

# Keep only essential columns
final_cols = ["Date_Time", "Year", "Month", "Day", "City"] + numeric_cols
merged_df = merged_df[final_cols]

# Drop rows where all temperature data is missing
merged_df.dropna(
    subset=["Max_Temp_C", "Min_Temp_C", "Mean_Temp_C"], how="all", inplace=True
)

# --- Save Processed Data ---
output_data_path = os.path.join(PROCESSED_DATA_DIR, "all_cities_weather_data.csv")
output_meta_path = os.path.join(PROCESSED_DATA_DIR, "cities_metadata.csv")

merged_df.to_csv(output_data_path, index=False)
print(f"\n-> Saved merged and cleaned data to: {output_data_path}")

meta_df = pd.DataFrame(metadata_records)
meta_df.to_csv(output_meta_path, index=False)
print(f"-> Saved city metadata to: {output_meta_path}")

print("\n--- Merging complete! ---")
