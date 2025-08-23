from flask import Flask, render_template, jsonify, request, send_file
from flask_cors import CORS
import requests
import pandas as pd
from datetime import datetime, timedelta
import json
from dateutil.relativedelta import relativedelta
import concurrent.futures
import io
import csv

app = Flask(__name__)
CORS(app)

# Environment Canada station IDs
STATION_IDS = {
    "Calgary": "50430",  # Calgary Int'l Airport
    "Toronto": "51459",  # Toronto Pearson Int'l Airport
    "Vancouver": "51442",  # Vancouver Int'l Airport
    "Montreal": "51157",  # Montreal Trudeau Int'l Airport
    "Edmonton": "50149",  # Edmonton Int'l Airport
    "Ottawa": "49568",  # Ottawa Int'l Airport
    "Winnipeg": "51097",  # Winnipeg Int'l Airport
    "Halifax": "50620",  # Halifax Int'l Airport
    "Quebec City": "51457",  # Jean Lesage Int'l Airport
    "Regina": "50438",  # Regina Int'l Airport
    "St. John's": "50089",  # St. John's Int'l Airport
    "Victoria": "51337",  # Victoria Int'l Airport
    "Saskatoon": "50091",  # Saskatoon Int'l Airport
}


def fetch_monthly_data(station_id, year, month):
    """
    Fetch one month of climate data for a station
    """
    url = f"https://climate.weather.gc.ca/climate_data/bulk_data_e.html?format=csv&stationID={station_id}&Year={year}&Month={month}&timeframe=2&submit=Download+Data"
    try:
        return pd.read_csv(url)
    except:
        return pd.DataFrame()


def get_historical_weather(city, years=2):
    """
    Get historical weather data from Environment Canada
    """
    if city not in STATION_IDS:
        return {"error": "City not found"}

    station_id = STATION_IDS[city]
    end_date = datetime.now()
    start_date = end_date - relativedelta(years=years)

    # Get current conditions (daily data)
    current_url = f"https://climate.weather.gc.ca/climate_data/bulk_data_e.html?format=csv&stationID={station_id}&Year={end_date.year}&Month={end_date.month}&Day={end_date.day}&timeframe=1&submit=Download+Data"
    try:
        current_df = pd.read_csv(current_url)
        latest = current_df.iloc[-1]
    except Exception as e:
        return {"error": f"Error fetching current data: {str(e)}"}

    # Fetch historical monthly data in parallel
    dates = []
    current_date = start_date
    while current_date <= end_date:
        dates.append((current_date.year, current_date.month))
        current_date += relativedelta(months=1)

    all_data = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
        future_to_date = {
            executor.submit(fetch_monthly_data, station_id, year, month): (year, month)
            for year, month in dates
        }
        for future in concurrent.futures.as_completed(future_to_date):
            df = future.result()
            if not df.empty:
                all_data.append(df)

    if not all_data:
        return {"error": "No historical data available"}

    # Combine all monthly data
    historical_df = pd.concat(all_data, ignore_index=True)

    # Process current conditions
    temp = latest.get("Temp (°C)", latest.get("Mean Temp (°C)"))
    conditions = latest.get("Weather", "Not available")
    humidity = latest.get("Rel Hum (%)", 0)
    wind_speed = latest.get("Wind Spd (km/h)", 0) * 0.277778
    precip = latest.get("Total Precip (mm)", 0)
    snow = latest.get("Snow on Grnd (cm)", 0)

    # Process historical data
    historical_data = []
    for _, row in historical_df.iterrows():
        mean_temp = row.get("Mean Temp (°C)")
        total_precip = row.get("Total Precip (mm)", 0)
        total_snow = row.get("Total Snow (cm)", 0)

        if pd.notna(mean_temp):
            historical_data.append(
                {
                    "date": row.get("Date/Time"),
                    "temp": round(float(mean_temp), 1),
                    "precip": round(float(total_precip), 1)
                    if pd.notna(total_precip)
                    else 0,
                    "snow": round(float(total_snow), 1) if pd.notna(total_snow) else 0,
                }
            )

    # Calculate historical statistics
    avg_temp = historical_df["Mean Temp (°C)"].mean()
    total_precip = (
        historical_df["Total Precip (mm)"].sum()
        if "Total Precip (mm)" in historical_df
        else 0
    )
    total_snow = (
        historical_df["Total Snow (cm)"].sum()
        if "Total Snow (cm)" in historical_df
        else 0
    )

    # Enhanced seasonal analysis
    historical_df["Date"] = pd.to_datetime(historical_df["Date/Time"])
    historical_df["Season"] = historical_df["Date"].dt.month.map(
        {
            12: "Winter",
            1: "Winter",
            2: "Winter",
            3: "Spring",
            4: "Spring",
            5: "Spring",
            6: "Summer",
            7: "Summer",
            8: "Summer",
            9: "Fall",
            10: "Fall",
            11: "Fall",
        }
    )
    historical_df["Year"] = historical_df["Date"].dt.year

    # Calculate seasonal statistics
    seasonal_stats = (
        historical_df.groupby(["Year", "Season"])
        .agg(
            {
                "Mean Temp (°C)": "mean",
                "Total Precip (mm)": "sum",
                "Total Snow (cm)": "sum",
            }
        )
        .round(1)
    )

    # Calculate seasonal averages across all years
    seasonal_averages = seasonal_stats.groupby("Season").mean().round(1)

    # Convert to dictionary format
    seasonal_data = {
        "temperatures": seasonal_averages["Mean Temp (°C)"].to_dict(),
        "precipitation": seasonal_averages["Total Precip (mm)"].to_dict(),
        "snow": seasonal_averages["Total Snow (cm)"].to_dict(),
        "yearly_seasonal": seasonal_stats.reset_index().to_dict("records"),
    }

    return {
        "current": {
            "temp": round(float(temp), 1) if pd.notna(temp) else None,
            "description": conditions,
            "humidity": round(float(humidity), 1) if pd.notna(humidity) else None,
            "wind_speed": round(float(wind_speed), 1) if pd.notna(wind_speed) else None,
            "precip": round(float(precip), 1) if pd.notna(precip) else 0,
            "snow": round(float(snow), 1) if pd.notna(snow) else 0,
        },
        "historical": {
            "avg_temp": round(float(avg_temp), 1) if pd.notna(avg_temp) else None,
            "total_precip": round(float(total_precip), 1)
            if pd.notna(total_precip)
            else 0,
            "total_snow": round(float(total_snow), 1) if pd.notna(total_snow) else 0,
            "years": years,
            "seasonal_averages": seasonal_data,
            "monthly_data": historical_data,
        },
    }


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/get_weather", methods=["POST"])
def weather_comparison():
    print("Received weather comparison request")  # Debug log
    data = request.get_json()
    print(f"Request data: {data}")  # Debug log
    city1 = data.get("city1", "Calgary")
    city2 = data.get("city2", "")

    print(f"Fetching weather for {city1} and {city2}")  # Debug log
    weather1 = get_historical_weather(city1)
    weather2 = get_historical_weather(city2)
    print("Weather data fetched successfully")  # Debug log

    return jsonify({"city1": weather1, "city2": weather2})


@app.route("/export_data", methods=["POST"])
def export_data():
    data = request.get_json()
    city1 = data.get("city1", "Calgary")
    city2 = data.get("city2", "")

    # Get weather data
    weather1 = get_historical_weather(city1)
    weather2 = get_historical_weather(city2) if city2 else None

    # Create CSV in memory
    output = io.StringIO()
    writer = csv.writer(output)

    # Write headers
    headers = ["City", "Date", "Temperature (°C)", "Precipitation (mm)", "Snow (cm)"]
    writer.writerow(headers)

    # Write data for first city
    for entry in weather1["historical"]["monthly_data"]:
        writer.writerow(
            [city1, entry["date"], entry["temp"], entry["precip"], entry["snow"]]
        )

    # Write data for second city if present
    if weather2:
        for entry in weather2["historical"]["monthly_data"]:
            writer.writerow(
                [city2, entry["date"], entry["temp"], entry["precip"], entry["snow"]]
            )

    # Prepare the output
    output.seek(0)
    return send_file(
        io.BytesIO(output.getvalue().encode("utf-8")),
        mimetype="text/csv",
        as_attachment=True,
        download_name=f"weather_comparison_{datetime.now().strftime('%Y%m%d')}.csv",
    )


if __name__ == "__main__":
    app.run(debug=True)
