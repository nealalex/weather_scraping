import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import os


def generate_max_temp_report():
    """
    Loads weather data for all cities and generates a comprehensive report
    focused on MAXIMUM temperatures to find the hottest locations.
    """
    print("--- Generating Maximum Temperature Summary Report ---")

    # --- 1. DEFINE FILE PATHS ---
    base_dir = (
        os.path.dirname(os.path.abspath(__file__)) if "__file__" in locals() else "."
    )
    data_path = os.path.join(
        base_dir, "..", "..", "data", "processed", "all_cities_weather_data.csv"
    )
    output_dir = os.path.join(base_dir, "..", "..", "reports")
    os.makedirs(output_dir, exist_ok=True)

    print(f"Loading data from: {data_path}")
    try:
        df = pd.read_csv(data_path, parse_dates=["Date_Time"])
        print("Data loaded successfully. Preparing data for plots...")
    except FileNotFoundError:
        print(f"Error: Data file not found at {data_path}")
        return

    # --- 2. DATA PREPARATION ---
    df["Day_of_Year"] = df["Date_Time"].dt.dayofyear
    df = df[df["Day_of_Year"] != 366]

    # --- 3. PLOT 1: CITY-TO-CITY AVERAGE MAX TEMP COMPARISON ---
    print("Generating Plot 1: City-to-City Average Max Temp Comparison...")
    # MODIFIED: Group by Max_Temp_C instead of Mean_Temp_C
    avg_day_df = df.groupby(["City", "Day_of_Year"])["Max_Temp_C"].mean().reset_index()

    fig_avg_day = px.line(
        avg_day_df,
        x="Day_of_Year",
        y="Max_Temp_C",  # MODIFIED
        color="City",
        title="City-to-City Comparison: Average Daily Maximum Temperature",  # MODIFIED
        labels={
            "Day_of_Year": "Day of the Year",
            "Max_Temp_C": "Average Maximum Temperature (°C)",
        },  # MODIFIED
    )
    fig_avg_day.update_layout(legend_title="Cities")

    # --- 4. ASSEMBLE THE HTML REPORT ---
    output_filename = "max_temp_summary_report.html"  # MODIFIED FILENAME
    output_path = os.path.join(output_dir, output_filename)

    fig_avg_day.write_html(output_path)
    print(f"Main comparison plot written to {output_path}")

    # --- 5. GENERATE AND APPEND DEEP-DIVE PLOTS FOR EACH CITY ---
    with open(output_path, "a") as f:
        for city in sorted(df["City"].unique()):
            print(f"Generating deep-dive plots for {city}...")
            city_df = df[df["City"] == city].copy()
            city_df["Year"] = city_df["Date_Time"].dt.year

            # PLOT 2 (per city): SMOOTHED YEAR-OVER-YEAR MAX TEMP PLOT
            # MODIFIED: Use Max_Temp_C
            city_df["Smoothed_Max_Temp"] = city_df.groupby("Year")[
                "Max_Temp_C"
            ].transform(
                lambda x: x.rolling(window=14, min_periods=1, center=True).mean()
            )

            sorted_years_desc = sorted(city_df["Year"].unique(), reverse=True)

            fig_spaghetti = px.line(
                city_df,
                x="Day_of_Year",
                y="Smoothed_Max_Temp",  # MODIFIED
                color="Year",
                category_orders={"Year": sorted_years_desc},
                title=f"{city}: Smoothed Year-over-Year Maximum Temperature (14-Day Rolling Average)",  # MODIFIED
                labels={
                    "Day_of_Year": "Day of the Year",
                    "Smoothed_Max_Temp": "Smoothed Maximum Temperature (°C)",
                },  # MODIFIED
            )

            # PLOT 3 (per city): MAX TEMP HEATMAP
            # MODIFIED: Pivot on Max_Temp_C
            heatmap_df = city_df.pivot_table(
                values="Max_Temp_C", index="Year", columns="Day_of_Year", aggfunc="mean"
            )
            heatmap_df = heatmap_df.sort_index(ascending=False)

            fig_heatmap = go.Figure(
                data=go.Heatmap(
                    z=heatmap_df.values,
                    x=heatmap_df.columns,
                    y=heatmap_df.index,
                    colorscale="Inferno",  # A great colorscale for heat
                    colorbar_title="Max Temp (°C)",
                )
            )
            fig_heatmap.update_layout(
                title=f"{city}: Daily Maximum Temperature Heatmap",  # MODIFIED
                xaxis_title="Day of the Year",
                yaxis_title="Year",
            )

            f.write(f"<hr><h1>Detailed Max Temp Analysis for {city}</h1>")  # MODIFIED
            f.write(fig_spaghetti.to_html(full_html=False, include_plotlyjs=False))
            f.write(fig_heatmap.to_html(full_html=False, include_plotlyjs=False))
            print(f"  > Appended {city}'s plots to the report.")

    print("-" * 50)
    print(f"Maximum temperature summary report generation complete!")
    print(f"Interactive summary report saved to: {output_path}")
    print("-" * 50)


if __name__ == "__main__":
    generate_max_temp_report()
