# 04_webapp.py
# A robust Flask web application to visualize the weather data.
# This app handles data loading errors gracefully without crashing.

import pandas as pd
import plotly
import plotly.express as px
import json
import os
from flask import Flask, render_template, request, jsonify

# --- Global Cache & Error Tracking ---
# These variables will hold the loaded data and any loading errors.
WEATHER_DF = None
META_DF = None
DATA_LOAD_ERROR = None


def load_data_if_needed():
    """
    Loads data into global variables if they haven't been loaded yet.
    Sets a global error message if loading fails.
    """
    global WEATHER_DF, META_DF, DATA_LOAD_ERROR

    # Return if data is already loaded successfully
    if WEATHER_DF is not None and DATA_LOAD_ERROR is None:
        return

    print("--- Weather Visualization Web App ---")
    try:
        # --- Path Setup ---
        script_dir = os.path.dirname(os.path.abspath(__file__))
        project_root = os.path.dirname(os.path.dirname(script_dir))
        processed_data_dir = os.path.join(project_root, "data", "processed")

        # These paths point to the output of the '03_merger.py' script
        data_file = os.path.join(processed_data_dir, "all_cities_weather_data.csv")
        meta_file = os.path.join(processed_data_dir, "cities_metadata.csv")

        print(f"Attempting to load metadata from {meta_file}...")
        META_DF = pd.read_csv(meta_file)
        print(f"Attempting to load weather data from {data_file}...")
        WEATHER_DF = pd.read_csv(data_file, parse_dates=["Date_Time"])

        DATA_LOAD_ERROR = None  # Clear any previous errors
        print("Data loaded successfully.")

    except FileNotFoundError as e:
        error_message = (
            f"A required data file was not found: {e.filename}. "
            "Please run '02_scraper.py' and '03_merger.py' to generate the data, "
            "then restart this web application."
        )
        print(f"--- FATAL ERROR: {error_message} ---")
        DATA_LOAD_ERROR = error_message
        # Set dataframes to empty to prevent further errors
        WEATHER_DF = pd.DataFrame()
        META_DF = pd.DataFrame()

    except Exception as e:
        error_message = f"An unexpected error occurred during data loading: {e}"
        print(f"--- FATAL ERROR: {error_message} ---")
        DATA_LOAD_ERROR = error_message
        WEATHER_DF = pd.DataFrame()
        META_DF = pd.DataFrame()


def create_app():
    """Creates and configures the Flask application using the factory pattern."""
    app = Flask(__name__)

    # Attempt to load data when the app starts.
    with app.app_context():
        load_data_if_needed()

        @app.route("/")
        def index():
            """Renders the main page with selectors for cities, years, and metrics."""
            if DATA_LOAD_ERROR:
                # If data loading failed, show a helpful error page.
                return render_template("error.html", error_message=DATA_LOAD_ERROR)

            # Prepare data for the template from the loaded dataframes
            cities = META_DF["City"].unique().tolist()
            years = list(
                range(
                    int(META_DF["start_year"].min()), int(META_DF["end_year"].max()) + 1
                )
            )
            metrics = {
                "Mean_Temp_C": "Mean Temperature (°C)",
                "Max_Temp_C": "Max Temperature (°C)",
                "Min_Temp_C": "Min Temperature (°C)",
                "Total_Precip_mm": "Total Precipitation (mm)",
            }

            return render_template(
                "index.html",
                cities=cities,
                years=years,
                metrics=metrics,
            )

        @app.route("/plot", methods=["POST"])
        def create_plot():
            """Creates a plot based on user selections and returns it as JSON."""
            # If data failed to load, prevent plotting.
            if DATA_LOAD_ERROR:
                return jsonify(
                    {"error": "Data is not loaded. Cannot create plot."}
                ), 500

            selections = request.get_json()

            selected_cities = selections.get("cities", [])
            selected_years = [int(y) for y in selections.get("years", [])]
            selected_metric = selections.get("metric")

            if not all([selected_cities, selected_years, selected_metric]):
                return jsonify(
                    {
                        "error": "Missing selections. Please select cities, years, and a metric."
                    }
                ), 400

            # Use the globally loaded WEATHER_DF
            df = WEATHER_DF

            # Define metrics to get the friendly name for the plot title and labels
            metrics = {
                "Mean_Temp_C": "Mean Temperature (°C)",
                "Max_Temp_C": "Max Temperature (°C)",
                "Min_Temp_C": "Min Temperature (°C)",
                "Total_Precip_mm": "Total Precipitation (mm)",
            }
            metric_name = metrics.get(selected_metric, selected_metric)

            # Filter the main dataframe based on selections
            filtered_df = df[
                (df["City"].isin(selected_cities)) & (df["Year"].isin(selected_years))
            ].copy()

            if filtered_df.empty:
                return jsonify(
                    {"error": "No data available for the selected criteria."}
                ), 404

            # Create a 'Day of Year' column for plotting across different years
            filtered_df["Day_of_Year"] = filtered_df["Date_Time"].dt.dayofyear

            # Aggregate data: calculate the mean of the metric for each day of the year across all selected years
            plot_df = (
                filtered_df.groupby(["City", "Day_of_Year"])[selected_metric]
                .mean()
                .reset_index()
            )

            # Create the plot
            fig = px.line(
                plot_df,
                x="Day_of_Year",
                y=selected_metric,
                color="City",
                title=f"Average {metric_name} for {', '.join(selected_cities)}",
                labels={
                    "Day_of_Year": "Day of the Year",
                    selected_metric: metric_name,
                    "City": "City",
                },
            )
            fig.update_layout(title_x=0.5, legend_title_text="Cities")

            # Convert the plot to JSON
            graph_json = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)

            # Return the JSON string directly as a response with the correct mimetype.
            return app.response_class(response=graph_json, mimetype="application/json")

    return app


# --- Main Execution ---
if __name__ == "__main__":
    # Create the app instance using our factory
    app = create_app()
    print("Starting Flask server...")
    print("Open http://127.0.0.1:5001 in your web browser.")
    # Binding to host='0.0.0.0' makes the server accessible from your network.
    # This is often necessary on macOS to bypass local connection issues.
    app.run(host="0.0.0.0", port=5001, debug=True)
