import requests

# Ask the user for a city
city = input("Enter city name: ")

# Geocoding API
url = "https://geocoding-api.open-meteo.com/v1/search"

params = {
    "name": city,
    "count": 1,
    "language": "en",
    "format": "json"
}

response = requests.get(url, params=params)

if response.status_code == 200:

    data = response.json()

    if "results" in data:

        location = data["results"][0]

        print("\n================================")
        print("       LOCATION FOUND")
        print("================================")

        print("City      :", location["name"])
        print("Country   :", location["country"])
        print("Latitude  :", location["latitude"])
        print("Longitude :", location["longitude"])

    else:
        print("Location not found.")

else:
    print("API request failed.")