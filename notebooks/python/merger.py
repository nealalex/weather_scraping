import pandas as pd
import os
from config import CITIES # Import the CITIES dictionary from your config file

def merge_and_clean_data():
    """
    Merges all raw CSV files from the nested directory structure into a single,
    cleaned data file. It correctly assigns the primary city name to all
    associated station data and standardizes column names.
    """
    print("--- Starting Data Merging and Cleaning Process ---")

    # --- DEFINE FILE PATHS ---
    base_dir = os.path.dirname(os.path.abspath(__file__)) if '__file__' in locals() else '.'
    raw_data_dir = os.path.join(base_dir, '..', '..', 'data', 'raw')
    processed_data_dir = os.path.join(base_dir, '..', '..', 'data', 'processed')
    os.makedirs(processed_data_dir, exist_ok=True)
    
    all_station_dataframes = []

    # Loop through the CITIES dictionary from the config file
    for city_name, stations_list in CITIES.items():
        print(f"Processing city: {city_name}")
        for station_info in stations_list:
            # --- THIS IS THE NEW LOGIC ---
            # Construct the specific directory name for this station
            station_name = station_info['station_name']
            station_dir_path = os.path.join(raw_data_dir, f"{city_name}_{station_name}")

            if os.path.isdir(station_dir_path):
                print(f"  > Found directory: {station_dir_path}")
                # Loop through every file inside that station's directory
                for filename in os.listdir(station_dir_path):
                    if filename.endswith('_daily_weather.csv'):
                        file_path = os.path.join(station_dir_path, filename)
                        try:
                            # Read the yearly data file
                            yearly_df = pd.read_csv(file_path)
                            
                            # --- CRITICAL FIX ---
                            # Assign the main 'city_name' (e.g., "Victoria") to all rows
                            yearly_df['City'] = city_name 
                            
                            all_station_dataframes.append(yearly_df)
                        except Exception as e:
                            print(f"    > WARNING: Could not read file {filename}. Error: {e}")
            else:
                print(f"  > WARNING: Directory not found for station: {station_name}. Skipping.")

    if not all_station_dataframes:
        print("\nERROR: No data was merged. Check if raw data exists and paths are correct. Exiting.")
        return

    # Concatenate all the individual yearly dataframes into one large dataframe
    final_df = pd.concat(all_station_dataframes, ignore_index=True)
    print("\nAll raw data files have been concatenated.")

    # --- DATA CLEANING AND STANDARDIZATION ---
    print("Cleaning and standardizing column names...")
    
    # Define a mapping from old, messy names to new, clean names
    # This will handle the columns present in the raw yearly CSVs
    column_rename_map = {
        'Date/Time': 'Date_Time', # Name in raw files is often 'Date/Time'
        'Year': 'Year',
        'Month': 'Month',
        'Day': 'Day',
        'Max Temp (°C)': 'Max_Temp_C',
        'Min Temp (°C)': 'Min_Temp_C',
        'Mean Temp (°C)': 'Mean_Temp_C',
        'Total Precip (mm)': 'Total_Precip_mm',
        'City': 'City'
    }

    # Find which columns from the map actually exist in the dataframe
    existing_columns = [col for col in column_rename_map if col in final_df.columns]
    
    # Select only the columns we need and rename them
    final_df = final_df[existing_columns]
    final_df = final_df.rename(columns=column_rename_map)

    # Convert Date_Time to proper datetime objects and handle any errors
    final_df['Date_Time'] = pd.to_datetime(final_df['Date_Time'], errors='coerce')
    final_df.dropna(subset=['Date_Time'], inplace=True)
    
    # --- SAVE THE FINAL PROCESSED FILE ---
    output_path = os.path.join(processed_data_dir, 'all_cities_weather_data.csv')
    final_df.to_csv(output_path, index=False)
    
    print("\n--- Merging and Cleaning Process Complete ---")
    print(f"Final processed file saved to: {output_path}")
    print(f"Total rows in final dataset: {len(final_df)}")


if __name__ == "__main__":
    merge_and_clean_data()