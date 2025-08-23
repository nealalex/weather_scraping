import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import os

def generate_summary_report():
    """
    Loads weather data for all cities and generates a comprehensive, multi-plot
    interactive HTML report that compares them and provides deep-dive plots for each.
    """
    print("--- Generating Comprehensive Summary Weather Report ---")

    # --- 1. DEFINE FILE PATHS ---
    base_dir = os.path.dirname(os.path.abspath(__file__)) if '__file__' in locals() else '.'
    data_path = os.path.join(base_dir, '..', '..', 'data', 'processed', 'all_cities_weather_data.csv')
    output_dir = os.path.join(base_dir, '..', '..', 'reports')
    os.makedirs(output_dir, exist_ok=True)
    
    print(f"Loading data from: {data_path}")
    try:
        df = pd.read_csv(data_path, parse_dates=['Date_Time'])
        print("Data loaded successfully. Preparing data for plots...")
    except FileNotFoundError:
        print(f"Error: Data file not found at {data_path}")
        return

    # --- 2. DATA PREPARATION ---
    df['Day_of_Year'] = df['Date_Time'].dt.dayofyear
    df = df[df['Day_of_Year'] != 366]

    # --- 3. PLOT 1: CITY-TO-CITY AVERAGE DAY COMPARISON ---
    print("Generating Plot 1: City-to-City Average Day Comparison...")
    avg_day_df = df.groupby(['City', 'Day_of_Year'])['Mean_Temp_C'].mean().reset_index()

    fig_avg_day = px.line(
        avg_day_df,
        x='Day_of_Year',
        y='Mean_Temp_C',
        color='City',
        title='City-to-City Comparison: Average Daily Mean Temperature',
        labels={'Day_of_Year': 'Day of the Year', 'Mean_Temp_C': 'Average Mean Temperature (°C)'}
    )
    fig_avg_day.update_layout(legend_title='Cities')

    # --- 4. ASSEMBLE THE HTML REPORT ---
    output_filename = "weather_summary_report.html"
    output_path = os.path.join(output_dir, output_filename)

    fig_avg_day.write_html(output_path)
    print(f"Main comparison plot written to {output_path}")

    # --- 5. GENERATE AND APPEND DEEP-DIVE PLOTS FOR EACH CITY ---
    with open(output_path, 'a') as f:
        for city in sorted(df['City'].unique()):
            print(f"Generating deep-dive plots for {city}...")
            city_df = df[df['City'] == city].copy()
            city_df['Year'] = city_df['Date_Time'].dt.year

            # --- PLOT 2 (per city): SMOOTHED YEAR-OVER-YEAR "SPAGHETTI PLOT" ---
            city_df['Smoothed_Temp'] = city_df.groupby('Year')['Mean_Temp_C'].transform(
                lambda x: x.rolling(window=14, min_periods=1, center=True).mean()
            )

            # --- FIX: SORT THE LEGEND IN DESCENDING ORDER ---
            # 1. Get the unique years and sort them from newest to oldest.
            sorted_years_desc = sorted(city_df['Year'].unique(), reverse=True)

            # 2. Pass this sorted list to the 'category_orders' argument.
            fig_spaghetti = px.line(
                city_df,
                x='Day_of_Year',
                y='Smoothed_Temp',
                color='Year',
                category_orders={'Year': sorted_years_desc}, # This line sorts the legend!
                title=f'{city}: Smoothed Year-over-Year Temperature (14-Day Rolling Average)',
                labels={'Day_of_Year': 'Day of the Year', 'Smoothed_Temp': 'Smoothed Mean Temperature (°C)'}
            )

            # --- PLOT 3 (per city): YEAR VS. DAY-OF-YEAR HEATMAP ---
            heatmap_df = city_df.pivot_table(
                values='Mean_Temp_C',
                index='Year',
                columns='Day_of_Year',
                aggfunc='mean'
            )
            # Sort the heatmap index (Year) in descending order to match the spaghetti plot
            heatmap_df = heatmap_df.sort_index(ascending=False)


            fig_heatmap = go.Figure(data=go.Heatmap(
                z=heatmap_df.values,
                x=heatmap_df.columns,
                y=heatmap_df.index,
                colorscale='RdBu_r',
                colorbar_title='Mean Temp (°C)'
            ))
            fig_heatmap.update_layout(
                title=f'{city}: Daily Mean Temperature Heatmap',
                xaxis_title='Day of the Year',
                yaxis_title='Year'
            )

            # Append plots to the HTML file
            f.write(f"<hr><h1>Detailed Analysis for {city}</h1>")
            f.write(fig_spaghetti.to_html(full_html=False, include_plotlyjs=False))
            f.write(fig_heatmap.to_html(full_html=False, include_plotlyjs=False))
            print(f"  > Appended {city}'s plots to the report.")


    print("-" * 50)
    print(f"Comprehensive summary report generation complete!")
    print(f"Interactive summary report saved to: {output_path}")
    print("-" * 50)

# ############################################################################
# # MAIN EXECUTION BLOCK
# ############################################################################
if __name__ == "__main__":
    generate_summary_report()