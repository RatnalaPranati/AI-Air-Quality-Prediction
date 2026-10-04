import requests


# ==========================================
# STEP 1: GET CITY FROM USER
# ==========================================

city = input("Enter city name: ")


# ==========================================
# STEP 2: FIND LATITUDE AND LONGITUDE
# ==========================================

geo_url = "https://geocoding-api.open-meteo.com/v1/search"

geo_params = {
    "name": city,
    "count": 1,
    "language": "en",
    "format": "json"
}

geo_response = requests.get(geo_url, params=geo_params)


if geo_response.status_code != 200:
    print("Could not connect to location API.")
    exit()


geo_data = geo_response.json()


if "results" not in geo_data:
    print("City not found.")
    exit()


location = geo_data["results"][0]

latitude = location["latitude"]
longitude = location["longitude"]

city_name = location["name"]
country = location["country"]


# ==========================================
# STEP 3: GET REAL-TIME AIR QUALITY
# ==========================================

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
        "us_aqi"
    ),

    "timezone": "auto"
}


air_response = requests.get(
    air_url,
    params=air_params
)


if air_response.status_code != 200:
    print("Could not get air-quality data.")
    exit()


air_data = air_response.json()

current = air_data["current"]


# ==========================================
# STEP 4: DISPLAY RESULT
# ==========================================

print("\n")
print("==============================================")
print("       REAL-TIME AIR QUALITY SYSTEM")
print("==============================================")

print("City       :", city_name)
print("Country    :", country)
print("Time       :", current["time"])

print("\n----------------------------------------------")
print("             POLLUTION VALUES")
print("----------------------------------------------")

print("PM2.5      :", current["pm2_5"], "µg/m³")
print("PM10       :", current["pm10"], "µg/m³")
print("CO         :", current["carbon_monoxide"], "µg/m³")
print("NO2        :", current["nitrogen_dioxide"], "µg/m³")
print("SO2        :", current["sulphur_dioxide"], "µg/m³")
print("O3         :", current["ozone"], "µg/m³")

print("\n----------------------------------------------")

print("CURRENT AQI :", current["us_aqi"])

print("----------------------------------------------")