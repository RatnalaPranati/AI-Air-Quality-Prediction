import requests
import pandas as pd
import numpy as np
from pathlib import Path

# ==========================================
# CITIES
# ==========================================

cities = {
    "Hyderabad": (17.3850, 78.4867),
    "Delhi": (28.6139, 77.2090),
    "Mumbai": (19.0760, 72.8777),
    "Bengaluru": (12.9716, 77.5946),
    "Chennai": (13.0827, 80.2707),
    "Kolkata": (22.5726, 88.3639),
    "Pune": (18.5204, 73.8567),
    "Ahmedabad": (23.0225, 72.5714),
    "Jaipur": (26.9124, 75.7873),
    "Lucknow": (26.8467, 80.9462)
}


# ==========================================
# API
# ==========================================

url = "https://air-quality-api.open-meteo.com/v1/air-quality"


# ==========================================
# STORE DATA
# ==========================================

all_data = []


# ==========================================
# DOWNLOAD DATA
# ==========================================

for city, coordinates in cities.items():

    latitude = coordinates[0]
    longitude = coordinates[1]

    print("Downloading data for:", city)

    params = {
        "latitude": latitude,
        "longitude": longitude,

        "hourly": (
            "pm10,"
            "pm2_5,"
            "carbon_monoxide,"
            "nitrogen_dioxide,"
            "sulphur_dioxide,"
            "ozone,"
            "us_aqi"
        ),

        "past_days": 90,
        "forecast_days": 0,
        "timezone": "auto"
    }

    response = requests.get(url, params=params)

    if response.status_code == 200:

        data = response.json()

        hourly = data["hourly"]

        df = pd.DataFrame(hourly)

        df["city"] = city

        all_data.append(df)

        print("Successfully downloaded:", city)

    else:

        print("Failed to download:", city)


# ==========================================
# COMBINE ALL CITIES
# ==========================================

if len(all_data) == 0:

    print("No data downloaded.")
    exit()


final_data = pd.concat(all_data, ignore_index=True)


# ==========================================
# CREATE NEXT-HOUR AQI
# ==========================================

final_data["next_hour_aqi"] = (
    final_data
    .groupby("city")["us_aqi"]
    .shift(-1)
)


# ==========================================
# SELECT IMPORTANT COLUMNS
# ==========================================

features = [
    "pm10",
    "pm2_5",
    "carbon_monoxide",
    "nitrogen_dioxide",
    "sulphur_dioxide",
    "ozone"
]

target = "next_hour_aqi"


final_data = final_data[
    features + [target]
]


# ==========================================
# REMOVE MISSING VALUES
# ==========================================

final_data = final_data.dropna()


# ==========================================
# SAVE DATASET
# ==========================================

Path("data").mkdir(exist_ok=True)

final_data.to_csv(
    "data/air_quality_training_data.csv",
    index=False
)


# ==========================================
# DISPLAY INFORMATION
# ==========================================

print("\n======================================")
print("       DATASET CREATED")
print("======================================")

print("Number of rows:", len(final_data))

print("\nColumns:")
print(final_data.columns.tolist())

print("\nFirst 5 rows:")
print(final_data.head())

print("\nDataset saved successfully!")

print(
    "\nFile:"
    " data/air_quality_training_data.csv"
)