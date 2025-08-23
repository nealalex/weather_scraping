import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import argparse
import sys
import os

def generate_report(city_name):
    """
    Loads weather data, filters it for a specific city, and generates
    a multi-plot interactive HTML report including a heatmap.
    """
    print("--- Generating Advanced Interactive Weather Report ---")

    # --- 1. DEFINE FILE PATHS ---
    base_dir = os.path.dirname(os.path.abspath(__file__)) if '__file__' in locals() else '.'
    data_path = os.path.join(base_dir, '..', '..', 'data', 'processed', 'all_cities_weather_data.csv')
    output_dir = os.path.join(base_dir, '..', '..', 'reports')
    os.makedirs(output_dir, exist_ok=True)
    
    print(f"Loading data from: {data_path}")
    try:
        df = pd.read_csv(data_path, parse_dates=['Date_Time'])
        print("Data loaded successfully. Creating plots...")
    except FileNotFoundError:
        print(f"Error: Data file not found at {data_path}")
        return
    except ValueError as e:
        print(f"Error reading the CSV. It might be missing a key column. Details: {e}")
        return

    # --- 2. FILTER DATA FOR THE CHOSEN CITY ---
    city_df = df[df['City'].str.lower() == city_name.lower()].copy()

    if city_df.empty:
        print(f"Error: No data found for city '{city_name}'. Please check the city name.")
        print(f"Available cities in the dataset are: {df['City'].unique()}")
        return
    
    city_df = city_df.set_index('Date_Time').sort_index()
    
    # --- 3. CREATE PLOTS ---
    # Resample to daily for the line charts
    daily_df = city_df.resample('D').agg({
        'Max_Temp_C': 'max',
        'Min_Temp_C': 'min',
        'Mean_Temp_C': 'mean'
    }).copy()
    
    daily_df['30-Day Avg Temp (°C)'] = daily_df['Mean_Temp_C'].rolling(window=30, min_periods=1, center=True).mean()

    # --- Create a 3-ROW subplot figure ---
    fig = make_subplots(
        rows=3, cols=1,
        shared_xaxes=True,
        subplot_titles=(
            f'Daily Temperature Trends for {city_name}', 
            f'Monthly Temperature Distribution for {city_name}',
            f'Average Monthly Temperature Heatmap for {city_name}' # New title for heatmap
        ),
        vertical_spacing=0.1
    )

    # PLOT 1: Daily Temperature with Moving Average
    fig.add_trace(go.Scatter(x=daily_df.index, y=daily_df['Min_Temp_C'], name='Min Temp', line=dict(color='blue', width=1), opacity=0.5), row=1, col=1)
    fig.add_trace(go.Scatter(x=daily_df.index, y=daily_df['Max_Temp_C'], name='Max Temp', line=dict(color='red', width=1), opacity=0.5), row=1, col=1)
    fig.add_trace(go.Scatter(x=daily_df.index, y=daily_df['30-Day Avg Temp (°C)'], name='30-Day Avg', line=dict(color='black', width=2)), row=1, col=1)

    # PLOT 2: Monthly Box Plot for Mean Temperature
    city_df['MonthName'] = city_df.index.month_name()
    month_order = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December']
    fig.add_trace(go.Box(x=city_df['MonthName'], y=city_df['Mean_Temp_C'], name='Temp Dist.', marker_color='lightblue'), row=2, col=1)

    # --- PLOT 3: HEATMAP ---
    # Prepare data for the heatmap by pivoting
    heatmap_data = city_df.pivot_table(
        values='Mean_Temp_C', 
        index=city_df.index.year, 
        columns=city_df.index.month,
        aggfunc='mean'
    )
    # Rename month number columns to month names for the heatmap
    heatmap_data.columns = month_order

    fig.add_trace(go.Heatmap(
        z=heatmap_data.values,
        x=heatmap_data.columns,
        y=heatmap_data.index,
        colorscale='RdBu_r', # Red-Blue reversed (hot is red, cold is blue)
        colorbar_title='Avg Temp (°C)'
    ), row=3, col=1)


    # --- 4. CUSTOMIZE LAYOUT ---
    fig.update_layout(
        title_text=f'Comprehensive Weather Report for {city_name}',
        height=1200, # Increase height for the extra plot
        xaxis2_categoryorder='array',
        xaxis2_categoryarray=month_order
    )
    fig.update_yaxes(title_text="Temperature (°C)", row=1, col=1)
    fig.update_yaxes(title_text="Temperature (°C)", row=2, col=1)
    fig.update_yaxes(title_text="Year", row=3, col=1)


    # --- 5. SAVE REPORT ---
    output_filename = f"weather_report_{city_name.replace(' ', '_').lower()}.html"
    output_path = os.path.join(output_dir, output_filename)
    
    fig.write_html(output_path)
    
    print("-" * 50)
    print(f"Report generation complete!")
    print(f"Comprehensive interactive report saved to: {output_path}")
    print("-" * 50)


# ############################################################################
# # MAIN EXECUTION BLOCK
# ############################################################################
if __name__ == "__main__":
    if 'ipykernel' in sys.modules:
        city_to_generate = "Calgary"
        print(f"Running in interactive mode. Using default city: '{city_to_generate}'")
    else:
        parser = argparse.ArgumentParser(description="Generate an advanced interactive weather report for a specific city.")
        parser.add_argument("--city", type=str, required=True, help="The city to generate the report for (e.g., 'Calgary').")
        args = parser.parse_args()
        city_to_generate = args.city

    generate_report(city_to_generate)