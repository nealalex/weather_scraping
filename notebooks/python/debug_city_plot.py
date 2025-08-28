# debug_city_plot.py
import pandas as pd
import plotly.express as px
import os

# ############################################################################
# # MAIN DEBUGGING SCRIPT
# ############################################################################

# --- CHOOSE THE CITY TO DEBUG ---
# Simply change this variable to the city you want to investigate.
CITY_TO_DEBUG = "Victoria"
# #################################

def debug_city(city_name):
    """
    Loads the final processed data and generates a year-over-year spaghetti plot
    for a single specified city to help with debugging.
    """
    print(f"--- Running Debug for City: {city_name} ---")

    # --- 1. LOAD THE FINAL PROCESSED DATA ---
    base_dir = os.path.dirname(os.path.abspath(__file__)) if '__file__' in locals() else '.'
    data_path = os.path.join(base_dir, '..', '..', 'data', 'processed', 'all_cities_weather_data.csv')
    
    print(f"Loading data from: {data_path}")
    try:
        df = pd.read_csv(data_path, parse_dates=['Date_Time'])
    except FileNotFoundError:
        print(f"Error: Data file not found at {data_path}")
        return

    # --- 2. FILTER FOR THE SPECIFIED CITY ---
    city_df = df[df['City'].str.lower() == city_name.lower()].copy()

    if city_df.empty:
        print(f"\nCRITICAL: No data found for city '{city_name}' in the processed file.")
        print(f"Available cities are: {df['City'].unique()}")
        return

    # --- 3. PRINT CRITICAL DIAGNOSTIC INFO ---
    city_df['Year'] = city_df['Date_Time'].dt.year
    min_year = city_df['Year'].min()
    max_year = city_df['Year'].max()
    unique_years = city_df['Year'].nunique()

    print("\n--- DATA DIAGNOSTICS ---")
    print(f"Data shape for {city_name}: {city_df.shape}")
    print(f"Earliest year found: {min_year}")
    print(f"Latest year found:   {max_year}")
    print(f"Number of unique years: {unique_years}")
    print("--------------------------\n")

    # --- 4. GENERATE THE PLOT ---
    print("Generating plot...")
    city_df['Day_of_Year'] = city_df['Date_Time'].dt.dayofyear
    city_df = city_df[city_df['Day_of_Year'] != 366]

    city_df['Smoothed_Temp'] = city_df.groupby('Year')['Mean_Temp_C'].transform(
        lambda x: x.rolling(window=14, min_periods=1, center=True).mean()
    )

    sorted_years_desc = sorted(city_df['Year'].unique(), reverse=True)

    fig = px.line(
        city_df,
        x='Day_of_Year',
        y='Smoothed_Temp',
        color='Year',
        category_orders={'Year': sorted_years_desc},
        title=f'{city_name}: Smoothed Year-over-Year Temperature (DEBUG)',
        labels={'Day_of_Year': 'Day of the Year', 'Smoothed_Temp': 'Smoothed Mean Temperature (°C)'}
    )

    # --- 5. SAVE AND SHOW THE PLOT ---
    output_dir = os.path.join(base_dir, '..', '..', 'reports')
    os.makedirs(output_dir, exist_ok=True)
    output_filename = f"debug_plot_{city_name.lower()}.html"
    output_path = os.path.join(output_dir, output_filename)
    
    fig.write_html(output_path)
    fig.show()

    print(f"Debug plot saved to: {output_path}")

# --- This block now just calls the function with the hardcoded variable ---
if __name__ == "__main__":
    debug_city(CITY_TO_DEBUG)