import requests
import pandas as pd
import joblib


# ============================================================
# 1. AQI CATEGORY FUNCTION
# ============================================================

def get_aqi_category(aqi):

    if aqi <= 50:
        return "Good"

    elif aqi <= 100:
        return "Moderate"

    elif aqi <= 150:
        return "Unhealthy for Sensitive Groups"

    elif aqi <= 200:
        return "Unhealthy"

    elif aqi <= 300:
        return "Very Unhealthy"

    else:
        return "Hazardous"


# ============================================================
# 2. RECOMMENDATION FUNCTION
# ============================================================

def get_recommendation(aqi):

    if aqi <= 50:
        return "Air quality is good. Normal outdoor activities are fine."

    elif aqi <= 100:
        return "Air quality is acceptable. Sensitive people should monitor conditions."

    elif aqi <= 150:
        return "Sensitive groups should reduce prolonged outdoor activity."

    elif aqi <= 200:
        return "Consider reducing prolonged outdoor exposure and heavy activity."

    elif aqi <= 300:
        return "Avoid prolonged outdoor activity, especially for sensitive groups."

    else:
        return "Avoid outdoor exposure as much as possible and follow health guidance."


# ============================================================
# 3. LOAD TRAINED MACHINE LEARNING MODEL
# ============================================================

try:

    model = joblib.load(
        "models/aqi_prediction_model.pkl"
    )

    features = joblib.load(
        "models/features.pkl"
    )

    print("\nAI model loaded successfully!")

except Exception as e:

    print("\nERROR: Could not load the trained model.")
    print("Make sure these files exist:")
    print("models/aqi_prediction_model.pkl")
    print("models/features.pkl")
    print("\nError:", e)

    exit()


# ============================================================
# 4. GET CITY FROM USER
# ============================================================

city = input("\nEnter city name: ")


# ============================================================
# 5. GEOCODING API
# ============================================================

geo_url = "https://geocoding-api.open-meteo.com/v1/search"

geo_params = {

    "name": city,

    "count": 1,

    "language": "en",

    "format": "json"
}


try:

    geo_response = requests.get(
        geo_url,
        params=geo_params,
        timeout=15
    )

except requests.RequestException as e:

    print("\nCould not connect to location API.")
    print("Error:", e)

    exit()


if geo_response.status_code != 200:

    print("\nLocation API request failed.")

    print(
        "Status Code:",
        geo_response.status_code
    )

    exit()


geo_data = geo_response.json()


# ============================================================
# 6. CHECK LOCATION
# ============================================================

if "results" not in geo_data:

    print("\nCity not found.")

    print(
        "Please enter a valid city name."
    )

    exit()


location = geo_data["results"][0]


latitude = location["latitude"]

longitude = location["longitude"]

city_name = location["name"]

country = location.get(
    "country",
    "Unknown"
)


# ============================================================
# 7. LIVE AIR QUALITY API
# ============================================================

air_url = "https://air-quality-api.open-meteo.com/v1/air-quality"


air_params = {

    "latitude": latitude,

    "longitude": longitude,

    "current": (
        "pm10,"
        "pm2_5,"
        "carbon_monoxide,"
        "nitrogen_dioxide,"
        "sulphur_dioxide,"
        "ozone,"
        "us_aqi,"
        "us_aqi_pm2_5,"
        "us_aqi_pm10,"
        "us_aqi_carbon_monoxide,"
        "us_aqi_nitrogen_dioxide,"
        "us_aqi_sulphur_dioxide,"
        "us_aqi_ozone"
    ),

    "timezone": "auto"
}


try:

    air_response = requests.get(
        air_url,
        params=air_params,
        timeout=15
    )

except requests.RequestException as e:

    print("\nCould not connect to air-quality API.")

    print("Error:", e)

    exit()


if air_response.status_code != 200:

    print("\nAir-quality API request failed.")

    print(
        "Status Code:",
        air_response.status_code
    )

    exit()


air_data = air_response.json()


if "current" not in air_data:

    print("\nAir-quality data is unavailable.")

    exit()


current = air_data["current"]


# ============================================================
# 8. GET LIVE POLLUTION VALUES
# ============================================================

pm10 = current.get(
    "pm10",
    0
)

pm25 = current.get(
    "pm2_5",
    0
)

co = current.get(
    "carbon_monoxide",
    0
)

no2 = current.get(
    "nitrogen_dioxide",
    0
)

so2 = current.get(
    "sulphur_dioxide",
    0
)

o3 = current.get(
    "ozone",
    0
)


# ============================================================
# 9. CURRENT AQI
# ============================================================

current_aqi = current.get(
    "us_aqi",
    0
)


# ============================================================
# 10. CREATE INPUT FOR ML MODEL
# ============================================================

input_data = pd.DataFrame({

    "pm10": [pm10],

    "pm2_5": [pm25],

    "carbon_monoxide": [co],

    "nitrogen_dioxide": [no2],

    "sulphur_dioxide": [so2],

    "ozone": [o3]

})


# Make sure the feature order is exactly
# the same as the training data

input_data = input_data[features]


# ============================================================
# 11. MACHINE LEARNING PREDICTION
# ============================================================

try:

    predicted_aqi = model.predict(
        input_data
    )[0]

except Exception as e:

    print("\nML prediction failed.")

    print("Error:", e)

    exit()


predicted_aqi = round(
    float(predicted_aqi),
    2
)


# AQI cannot be negative

if predicted_aqi < 0:

    predicted_aqi = 0


# ============================================================
# 12. AQI CATEGORIES
# ============================================================

current_category = get_aqi_category(
    current_aqi
)

predicted_category = get_aqi_category(
    predicted_aqi
)


# ============================================================
# 13. MAIN POLLUTANT
# ============================================================

pollutant_aqi = {

    "PM2.5": current.get(
        "us_aqi_pm2_5",
        0
    ),

    "PM10": current.get(
        "us_aqi_pm10",
        0
    ),

    "CO": current.get(
        "us_aqi_carbon_monoxide",
        0
    ),

    "NO2": current.get(
        "us_aqi_nitrogen_dioxide",
        0
    ),

    "SO2": current.get(
        "us_aqi_sulphur_dioxide",
        0
    ),

    "O3": current.get(
        "us_aqi_ozone",
        0
    )
}


main_pollutant = max(
    pollutant_aqi,
    key=pollutant_aqi.get
)


# ============================================================
# 14. WEATHER API
# ============================================================

weather_url = "https://api.open-meteo.com/v1/forecast"


weather_params = {

    "latitude": latitude,

    "longitude": longitude,

    "current": (
        "temperature_2m,"
        "relative_humidity_2m,"
        "wind_speed_10m"
    ),

    "timezone": "auto"
}


try:

    weather_response = requests.get(
        weather_url,
        params=weather_params,
        timeout=15
    )

except requests.RequestException as e:

    print("\nCould not connect to weather API.")

    print("Error:", e)

    exit()


if weather_response.status_code != 200:

    print("\nWeather API request failed.")

    print(
        "Status Code:",
        weather_response.status_code
    )

    exit()


weather_data = weather_response.json()


if "current" not in weather_data:

    print("\nWeather data is unavailable.")

    exit()


weather = weather_data["current"]


temperature = weather.get(
    "temperature_2m",
    0
)

humidity = weather.get(
    "relative_humidity_2m",
    0
)

wind_speed = weather.get(
    "wind_speed_10m",
    0
)


# ============================================================
# 15. PREDICTION DIFFERENCE
# ============================================================

difference = predicted_aqi - current_aqi


# ============================================================
# 16. PREDICTION ANALYSIS
# ============================================================

if difference > 10:

    prediction_message = (
        "AQI is expected to increase."
    )

elif difference < -10:

    prediction_message = (
        "AQI is expected to improve."
    )

else:

    prediction_message = (
        "AQI is expected to remain relatively stable."
    )


# ============================================================
# 17. HEALTH RECOMMENDATION
# ============================================================

recommendation = get_recommendation(
    predicted_aqi
)


# ============================================================
# 18. DISPLAY COMPLETE RESULT
# ============================================================

print("\n")

print("==========================================================")

print(
    "       REAL-TIME AI AIR QUALITY PREDICTION SYSTEM"
)

print("==========================================================")


# ------------------------------------------------------------
# LOCATION
# ------------------------------------------------------------

print("\nLOCATION")

print("----------------------------------------------------------")

print(
    "City            :",
    city_name
)

print(
    "Country         :",
    country
)

print(
    "Latitude        :",
    latitude
)

print(
    "Longitude       :",
    longitude
)

print(
    "Data Time       :",
    current.get(
        "time",
        "Unavailable"
    )
)


# ------------------------------------------------------------
# LIVE POLLUTION
# ------------------------------------------------------------

print("\nREAL-TIME POLLUTION")

print("----------------------------------------------------------")

print(
    "PM2.5           :",
    pm25,
    "µg/m³"
)

print(
    "PM10            :",
    pm10,
    "µg/m³"
)

print(
    "CO              :",
    co,
    "µg/m³"
)

print(
    "NO2             :",
    no2,
    "µg/m³"
)

print(
    "SO2             :",
    so2,
    "µg/m³"
)

print(
    "O3              :",
    o3,
    "µg/m³"
)


# ------------------------------------------------------------
# WEATHER
# ------------------------------------------------------------

print("\nLIVE WEATHER")

print("----------------------------------------------------------")

print(
    "Temperature     :",
    temperature,
    "°C"
)

print(
    "Humidity        :",
    humidity,
    "%"
)

print(
    "Wind Speed      :",
    wind_speed,
    "km/h"
)


# ------------------------------------------------------------
# AQI
# ------------------------------------------------------------

print("\nAQI INFORMATION")

print("----------------------------------------------------------")

print(
    "Current AQI             :",
    current_aqi
)

print(
    "Current AQI Category    :",
    current_category
)

print(
    "Predicted Next-Hour AQI:",
    predicted_aqi
)

print(
    "Predicted AQI Category  :",
    predicted_category
)


# ------------------------------------------------------------
# MAIN POLLUTANT
# ------------------------------------------------------------

print("\nMAIN POLLUTANT")

print("----------------------------------------------------------")

print(
    "Main Pollutant          :",
    main_pollutant
)


# ------------------------------------------------------------
# AI PREDICTION ANALYSIS
# ------------------------------------------------------------

print("\nAI PREDICTION ANALYSIS")

print("----------------------------------------------------------")

print(
    "AQI Difference          :",
    round(difference, 2)
)

print(
    "Prediction              :",
    prediction_message
)


# ------------------------------------------------------------
# RECOMMENDATION
# ------------------------------------------------------------

print("\nHEALTH / ENVIRONMENT RECOMMENDATION")

print("----------------------------------------------------------")

print(
    recommendation
)


# ------------------------------------------------------------
# END
# ------------------------------------------------------------

print("\n==========================================================")

print(
    "             ANALYSIS COMPLETED"
)

print("==========================================================")