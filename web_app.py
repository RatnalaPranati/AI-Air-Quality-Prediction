from flask import Flask, render_template, request, jsonify

import requests
import pandas as pd
import joblib
import os
import numpy as np


app = Flask(__name__)


# ============================================================
# LOAD ML MODEL
# ============================================================

MODEL_PATH = os.path.join(
    "models",
    "aqi_prediction_model.pkl"
)

FEATURES_PATH = os.path.join(
    "models",
    "features.pkl"
)


try:

    model = joblib.load(MODEL_PATH)

    features = joblib.load(FEATURES_PATH)

    print("ML model loaded successfully.")

    print("Features:", features)


except Exception as e:

    model = None

    features = [
        "pm10",
        "pm2_5",
        "carbon_monoxide",
        "nitrogen_dioxide",
        "sulphur_dioxide",
        "ozone"
    ]

    print("Error loading model:", e)


# ============================================================
# AQI CATEGORY
# ============================================================

def get_aqi_category(aqi):

    if aqi is None:
        return "Unknown"

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
# AQI COLOR / LEVEL
# ============================================================

def get_aqi_level(aqi):

    if aqi <= 50:
        return "good"

    elif aqi <= 100:
        return "moderate"

    elif aqi <= 150:
        return "sensitive"

    elif aqi <= 200:
        return "unhealthy"

    elif aqi <= 300:
        return "very-unhealthy"

    else:
        return "hazardous"


# ============================================================
# GEOCODING
# ============================================================

def get_coordinates(city):

    url = "https://geocoding-api.open-meteo.com/v1/search"

    params = {
        "name": city,
        "count": 1,
        "language": "en",
        "format": "json"
    }

    response = requests.get(
        url,
        params=params,
        timeout=15,
        headers={
            "User-Agent": "AI-Air-Quality-Prediction/1.0"
        }
    )

    if response.status_code != 200:

        raise Exception(
            f"Geocoding API failed with status "
            f"{response.status_code}"
        )

    data = response.json()

    if "results" not in data or len(data["results"]) == 0:

        raise Exception(
            f"Could not find location: {city}"
        )

    result = data["results"][0]

    return {
        "name": result.get("name"),
        "country": result.get("country"),
        "latitude": result.get("latitude"),
        "longitude": result.get("longitude")
    }


# ============================================================
# AIR QUALITY DATA
# ============================================================

def get_air_quality(latitude, longitude):

    url = "https://air-quality-api.open-meteo.com/v1/air-quality"

    params = {
        "latitude": latitude,
        "longitude": longitude,

        "current": (
            "pm10,"
            "pm2_5,"
            "carbon_monoxide,"
            "nitrogen_dioxide,"
            "sulphur_dioxide,"
            "ozone,"
            "us_aqi"
        ),

        "hourly": (
            "us_aqi,"
            "pm10,"
            "pm2_5,"
            "carbon_monoxide,"
            "nitrogen_dioxide,"
            "sulphur_dioxide,"
            "ozone"
        ),

        "forecast_days": 1,

        "timezone": "auto"
    }

    response = requests.get(
        url,
        params=params,
        timeout=20,
        headers={
            "User-Agent": "AI-Air-Quality-Prediction/1.0"
        }
    )

    if response.status_code != 200:

        print(
            "Air Quality API status:",
            response.status_code
        )

        print(
            "Air Quality API response:",
            response.text[:500]
        )

        raise Exception(
            f"Air quality API failed with status "
            f"{response.status_code}"
        )

    return response.json()


# ============================================================
# WEATHER DATA
# ============================================================

def get_weather(latitude, longitude):

    url = "https://api.open-meteo.com/v1/forecast"

    params = {
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

        response = requests.get(
            url,
            params=params,
            timeout=20,
            headers={
                "User-Agent": "AI-Air-Quality-Prediction/1.0"
            }
        )

        print(
            "Weather API status:",
            response.status_code
        )

        if response.status_code != 200:

            print(
                "Weather API response:",
                response.text[:500]
            )

            raise Exception(
                f"Weather API failed with status "
                f"{response.status_code}"
            )

        return response.json()

    except requests.exceptions.Timeout:

        raise Exception(
            "Weather API request timed out."
        )

    except requests.exceptions.RequestException as e:

        raise Exception(
            f"Weather API connection error: {str(e)}"
        )


# ============================================================
# MAIN POLLUTANT
# ============================================================

def find_main_pollutant(air_data):

    current = air_data.get(
        "current",
        {}
    )

    pollutants = {

        "PM2.5": current.get(
            "pm2_5"
        ),

        "PM10": current.get(
            "pm10"
        ),

        "CO": current.get(
            "carbon_monoxide"
        ),

        "NO₂": current.get(
            "nitrogen_dioxide"
        ),

        "SO₂": current.get(
            "sulphur_dioxide"
        ),

        "O₃": current.get(
            "ozone"
        )
    }

    valid_pollutants = {

        name: value

        for name, value in pollutants.items()

        if value is not None
    }

    if not valid_pollutants:

        return "Unknown"

    return max(
        valid_pollutants,
        key=valid_pollutants.get
    )


# ============================================================
# ML PREDICTION
# ============================================================

def predict_next_hour(air_data):

    current = air_data.get(
        "current",
        {}
    )

    input_data = {

        "pm10": current.get(
            "pm10",
            0
        ),

        "pm2_5": current.get(
            "pm2_5",
            0
        ),

        "carbon_monoxide": current.get(
            "carbon_monoxide",
            0
        ),

        "nitrogen_dioxide": current.get(
            "nitrogen_dioxide",
            0
        ),

        "sulphur_dioxide": current.get(
            "sulphur_dioxide",
            0
        ),

        "ozone": current.get(
            "ozone",
            0
        )
    }

    df = pd.DataFrame(
        [input_data]
    )

    # Make sure feature order matches training

    if features is not None:

        try:

            df = df[features]

        except Exception:

            pass

    if model is None:

        return None

    prediction = model.predict(df)[0]

    # AQI cannot be negative

    prediction = max(
        0,
        float(prediction)
    )

    return round(
        prediction,
        2
    )


# ============================================================
# RECOMMENDATION
# ============================================================

def get_recommendation(aqi):

    if aqi <= 50:

        return {

            "title": "Air quality is good",

            "message": (
                "Air quality is considered satisfactory. "
                "Outdoor activities are generally safe."
            )
        }

    elif aqi <= 100:

        return {

            "title": "Air quality is acceptable",

            "message": (
                "Most people can continue normal outdoor activities. "
                "Sensitive individuals should monitor their symptoms."
            )
        }

    elif aqi <= 150:

        return {

            "title": "Sensitive groups should take care",

            "message": (
                "People with respiratory or heart conditions, "
                "children and older adults should reduce prolonged "
                "outdoor exertion."
            )
        }

    elif aqi <= 200:

        return {

            "title": "Limit prolonged outdoor activity",

            "message": (
                "Everyone may begin to experience health effects. "
                "Consider reducing prolonged outdoor activities."
            )
        }

    elif aqi <= 300:

        return {

            "title": "Avoid prolonged outdoor exposure",

            "message": (
                "Health alert conditions may affect everyone. "
                "Reduce outdoor activities and consider wearing "
                "appropriate protection."
            )
        }

    else:

        return {

            "title": "Hazardous air quality",

            "message": (
                "Health warnings of emergency conditions are possible. "
                "Avoid outdoor exposure as much as possible."
            )
        }


# ============================================================
# HOME PAGE
# ============================================================

@app.route("/")
def home():

    return render_template(
        "index.html"
    )


# ============================================================
# AIR QUALITY API
# ============================================================

@app.route("/api/air-quality")
def air_quality_api():

    city = request.args.get(
        "city",
        ""
    ).strip()

    if not city:

        return jsonify({

            "success": False,

            "error": "Please enter a city name."

        }), 400

    try:

        # ----------------------------------------------------
        # LOCATION
        # ----------------------------------------------------

        location = get_coordinates(
            city
        )

        latitude = location["latitude"]

        longitude = location["longitude"]


        # ----------------------------------------------------
        # AIR QUALITY
        # ----------------------------------------------------

        air_data = get_air_quality(
            latitude,
            longitude
        )

        current_air = air_data.get(
            "current",
            {}
        )

        current_aqi = current_air.get(
            "us_aqi"
        )

        if current_aqi is None:

            current_aqi = 0

        current_aqi = round(
            float(current_aqi),
            2
        )


        # ----------------------------------------------------
        # WEATHER
        # ----------------------------------------------------

        weather_data = get_weather(
            latitude,
            longitude
        )

        current_weather = weather_data.get(
            "current",
            {}
        )


        # ----------------------------------------------------
        # ML PREDICTION
        # ----------------------------------------------------

        predicted_aqi = predict_next_hour(
            air_data
        )

        if predicted_aqi is None:

            predicted_aqi = current_aqi


        # ----------------------------------------------------
        # MAIN POLLUTANT
        # ----------------------------------------------------

        main_pollutant = find_main_pollutant(
            air_data
        )


        # ----------------------------------------------------
        # RECOMMENDATION
        # ----------------------------------------------------

        recommendation = get_recommendation(
            current_aqi
        )


        # ----------------------------------------------------
        # HOURLY TREND
        # ----------------------------------------------------

        hourly = air_data.get(
            "hourly",
            {}
        )

        hourly_times = hourly.get(
            "time",
            []
        )

        hourly_aqi = hourly.get(
            "us_aqi",
            []
        )

        trend = []

        for time, aqi in zip(
            hourly_times,
            hourly_aqi
        ):

            if aqi is not None:

                trend.append({

                    "time": time,

                    "aqi": round(
                        float(aqi),
                        2
                    )
                })


        # ----------------------------------------------------
        # RESULT
        # ----------------------------------------------------

        result = {

            "success": True,

            "location": {

                "city": location["name"],

                "country": location["country"],

                "latitude": latitude,

                "longitude": longitude
            },

            "current": {

                "aqi": current_aqi,

                "category": get_aqi_category(
                    current_aqi
                ),

                "level": get_aqi_level(
                    current_aqi
                ),

                "main_pollutant": main_pollutant,

                "pollutants": {

                    "pm2_5": current_air.get(
                        "pm2_5"
                    ),

                    "pm10": current_air.get(
                        "pm10"
                    ),

                    "carbon_monoxide": current_air.get(
                        "carbon_monoxide"
                    ),

                    "nitrogen_dioxide": current_air.get(
                        "nitrogen_dioxide"
                    ),

                    "sulphur_dioxide": current_air.get(
                        "sulphur_dioxide"
                    ),

                    "ozone": current_air.get(
                        "ozone"
                    )
                }
            },

            "prediction": {

                "aqi": predicted_aqi,

                "category": get_aqi_category(
                    predicted_aqi
                ),

                "level": get_aqi_level(
                    predicted_aqi
                ),

                "difference": round(
                    predicted_aqi - current_aqi,
                    2
                )
            },

            "weather": {

                "temperature": current_weather.get(
                    "temperature_2m"
                ),

                "humidity": current_weather.get(
                    "relative_humidity_2m"
                ),

                "wind_speed": current_weather.get(
                    "wind_speed_10m"
                )
            },

            "trend": trend,

            "recommendation": recommendation
        }

        return jsonify(
            result
        )


    except Exception as e:

        print(
            "ERROR:",
            str(e)
        )

        return jsonify({

            "success": False,

            "error": str(e)

        }), 500


# ============================================================
# RUN FLASK SERVER
# ============================================================

if __name__ == "__main__":

    app.run(

        debug=True,

        host="127.0.0.1",

        port=5000
    )