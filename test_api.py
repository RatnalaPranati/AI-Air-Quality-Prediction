import requests

url = "https://air-quality-api.open-meteo.com/v1/air-quality"

params = {
    "latitude": 17.3850,
    "longitude": 78.4867,
    "current": "pm10,pm2_5,carbon_monoxide,nitrogen_dioxide,sulphur_dioxide,ozone,us_aqi",
    "timezone": "auto"
}

response = requests.get(url, params=params)

if response.status_code == 200:

    data = response.json()
    current = data["current"]

    print("\n====================================")
    print("     REAL-TIME AIR QUALITY DATA")
    print("====================================")

    print("Time:", current["time"])

    print("\nPollution Values")
    print("------------------------------------")

    print("PM2.5 :", current["pm2_5"], "µg/m³")
    print("PM10  :", current["pm10"], "µg/m³")
    print("CO    :", current["carbon_monoxide"], "µg/m³")
    print("NO2   :", current["nitrogen_dioxide"], "µg/m³")
    print("SO2   :", current["sulphur_dioxide"], "µg/m³")
    print("O3    :", current["ozone"], "µg/m³")

    print("\nCurrent AQI:", current["us_aqi"])

    print("====================================")

else:
    print("API request failed")
    print("Status Code:", response.status_code)