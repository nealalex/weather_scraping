import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import os

def generate_comparison_report():
    """
    Loads weather data for all cities and generates a multi-plot
    interactive HTML report comparing them.
    """
    print("--- Generating Cross-City Comparison Weather Report ---")

    # --- 1. DEFINE FILE PATHS ---
    base_dir = os.path.dirname(os.path.abspath(__file__)) if '__file__' in locals() else '.'
    data_path = os.path.join(base_dir, '..', '..', 'data', 'processed', 'all_cities_weather_data.csv')
    output_dir = os.path.join(base_dir, '..', '..', 'reports')
    os.makedirs(output_dir, exist_ok=True)
    
    print(f"Loading data from: {data_path}")
    try:
        df = pd.read_csv(data_path, parse_dates=['Date_Time'])
        print("Data loaded successfully. Creating comparison plots...")
    except FileNotFoundError:
        print(f"Error: Data file not found at {data_path}")
        return

    # --- 2. PLOT 1: 30-DAY MOVING AVERAGE TEMPERATURE COMPARISON ---
    
    fig_line = go.Figure()
    
    # Loop through each city and add its moving average as a separate line
    for city in df['City'].unique():
        city_df = df[df['City'] == city].set_index('Date_Time').sort_index()
        
        # Resample to daily and calculate moving average
        daily_df = city_df.resample('D').agg({'Mean_Temp_C': 'mean'}).copy()
        daily_df['30-Day Avg'] = daily_df['Mean_Temp_C'].rolling(window=30, min_periods=1, center=True).mean()
        
        fig_line.add_trace(go.Scatter(
            x=daily_df.index, 
            y=daily_df['30-Day Avg'], 
            name=city, # The legend will show the city name
            mode='lines'
        ))

    fig_line.update_layout(
        title_text='30-Day Moving Average Temperature Comparison Across Cities',
        xaxis_title='Date',
        yaxis_title='Temperature (°C)',
        legend_title='City'
    )

    # --- 3. PLOT 2: MONTHLY TEMPERATURE DISTRIBUTION BOX PLOT COMPARISON ---
    
    # Plotly Express is great for this, as it can group by color automatically
    df['Month'] = pd.Categorical(
        df['Date_Time'].dt.month_name(),
        categories=['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December'],
        ordered=True
    )
    
    fig_box = px.box(
        df.sort_values('Month'), # Sort by month to ensure correct order
        x='Month',
        y='Mean_Temp_C',
        color='City', # This creates a separate, colored box for each city
        title='Monthly Temperature Distribution Comparison'
    )
    
    fig_box.update_layout(
        xaxis_title='Month',
        yaxis_title='Mean Temperature (°C)'
    )


    # --- 4. SAVE BOTH PLOTS TO A SINGLE HTML FILE ---
    output_filename = "weather_report.html" # The main comparison report file
    output_path = os.path.join(output_dir, output_filename)

    # First, write the line chart to a new file
    fig_line.write_html(output_path)

    # Then, open the same file in 'append' mode and add the box plot
    # The 'full_html=False' is crucial here. It prevents writing the <html>, <head>, <body> tags
    # and the massive Plotly.js library a second time.
    with open(output_path, 'a') as f:
        f.write(fig_box.to_html(full_html=False, include_plotlyjs='cdn'))

    print("-" * 50)
    print(f"Comparison report generation complete!")
    print(f"Interactive comparison report saved to: {output_path}")
    print("-" * 50)


# ############################################################################
# # MAIN EXECUTION BLOCK
# ############################################################################
if __name__ == "__main__":
    generate_comparison_report()