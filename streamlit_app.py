import streamlit as st
import requests
import pandas as pd
import joblib
import plotly.express as px


# ============================================================
# PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="AI Air Quality Prediction",
    page_icon="🌍",
    layout="wide"
)


# ============================================================
# SIMPLE PAGE STYLING
# ============================================================

st.markdown("""
<style>

.block-container {
    max-width: 1400px;
    padding-top: 2rem;
    padding-bottom: 2rem;
}

.main-title {
    text-align: center;
    font-size: 40px;
    font-weight: 700;
    margin-bottom: 5px;
}

.subtitle {
    text-align: center;
    color: #666666;
    font-size: 17px;
    margin-bottom: 25px;
}

.section-title {
    font-size: 24px;
    font-weight: 700;
    margin-top: 30px;
    margin-bottom: 15px;
}

.footer {
    text-align: center;
    color: #777777;
    font-size: 13px;
    margin-top: 35px;
}

</style>
""", unsafe_allow_html=True)


# ============================================================
# LOAD TRAINED MODEL
# ============================================================

@st.cache_resource
def load_model():

    model = joblib.load(
        "models/aqi_prediction_model.pkl"
    )

    features = joblib.load(
        "models/features.pkl"
    )

    return model, features


try:

    model, features = load_model()

except Exception as e:

    st.error("❌ Unable to load the trained ML model.")

    st.code(str(e))

    st.stop()


# ============================================================
# AQI CATEGORY
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
# AQI ICON
# ============================================================

def get_aqi_icon(aqi):

    if aqi <= 50:
        return "🟢"

    elif aqi <= 100:
        return "🟡"

    elif aqi <= 150:
        return "🟠"

    elif aqi <= 200:
        return "🔴"

    elif aqi <= 300:
        return "🟣"

    else:
        return "🟤"


# ============================================================
# HEALTH RECOMMENDATION
# ============================================================

def get_recommendation(aqi):

    if aqi <= 50:

        return (
            "Air quality is good. "
            "Normal outdoor activities are fine."
        )

    elif aqi <= 100:

        return (
            "Air quality is acceptable. "
            "Sensitive people should monitor conditions."
        )

    elif aqi <= 150:

        return (
            "Sensitive groups should reduce "
            "prolonged outdoor activity."
        )

    elif aqi <= 200:

        return (
            "Consider reducing prolonged outdoor exposure "
            "and strenuous outdoor activity."
        )

    elif aqi <= 300:

        return (
            "Avoid prolonged outdoor activity, "
            "especially for sensitive groups."
        )

    else:

        return (
            "Avoid outdoor exposure as much as possible "
            "and follow local health guidance."
        )


# ============================================================
# GEOCODING API
# ============================================================

@st.cache_data(ttl=300)
def get_location(city):

    url = (
        "https://geocoding-api.open-meteo.com/v1/search"
    )

    params = {
        "name": city,
        "count": 1,
        "language": "en",
        "format": "json"
    }

    response = requests.get(
        url,
        params=params,
        timeout=15
    )

    response.raise_for_status()

    data = response.json()

    if "results" not in data:

        return None

    return data["results"][0]


# ============================================================
# AIR QUALITY API
# ============================================================

@st.cache_data(ttl=300)
def get_air_quality(latitude, longitude):

    url = (
        "https://air-quality-api.open-meteo.com/v1/air-quality"
    )

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
            "us_aqi,"
            "us_aqi_pm2_5,"
            "us_aqi_pm10,"
            "us_aqi_carbon_monoxide,"
            "us_aqi_nitrogen_dioxide,"
            "us_aqi_sulphur_dioxide,"
            "us_aqi_ozone"
        ),

        "hourly": "us_aqi",

        "forecast_hours": 24,

        "timezone": "auto"
    }

    response = requests.get(
        url,
        params=params,
        timeout=15
    )

    response.raise_for_status()

    return response.json()


# ============================================================
# WEATHER API
# ============================================================

@st.cache_data(ttl=300)
def get_weather(latitude, longitude):

    url = (
        "https://api.open-meteo.com/v1/forecast"
    )

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

    response = requests.get(
        url,
        params=params,
        timeout=15
    )

    response.raise_for_status()

    return response.json()


# ============================================================
# HEADER
# ============================================================

st.markdown(
    '<div class="main-title">🌍 AI Air Quality Prediction</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="subtitle">'
    'Real-Time Air Quality Monitoring & Next-Hour AQI Prediction'
    '</div>',
    unsafe_allow_html=True
)


# ============================================================
# CITY SEARCH
# ============================================================

st.markdown(
    "### 📍 Search Location"
)

input_col, button_col = st.columns(
    [5, 1]
)


with input_col:

    city = st.text_input(
        "City",
        value="Hyderabad",
        placeholder="Enter city name",
        label_visibility="collapsed"
    )


with button_col:

    search_button = st.button(
        "🔄 Get Live Data",
        type="primary",
        use_container_width=True
    )


# ============================================================
# VALIDATE INPUT
# ============================================================

if city.strip() == "":

    st.warning(
        "Please enter a city name."
    )

    st.stop()


# ============================================================
# GET LOCATION
# ============================================================

try:

    location = get_location(
        city.strip()
    )

except requests.RequestException as e:

    st.error(
        "Unable to connect to the location service."
    )

    st.code(str(e))

    st.stop()


if location is None:

    st.error(
        "❌ Location not found. "
        "Please enter a valid city."
    )

    st.stop()


latitude = location["latitude"]

longitude = location["longitude"]

city_name = location["name"]

country = location.get(
    "country",
    ""
)


# ============================================================
# GET LIVE AIR QUALITY
# ============================================================

try:

    air_data = get_air_quality(
        latitude,
        longitude
    )

    weather_data = get_weather(
        latitude,
        longitude
    )

except requests.RequestException as e:

    st.error(
        "Unable to retrieve live air-quality or weather data."
    )

    st.code(str(e))

    st.stop()


current = air_data["current"]

weather = weather_data["current"]


# ============================================================
# EXTRACT POLLUTION VALUES
# ============================================================

pm25 = current.get(
    "pm2_5",
    0
)

pm10 = current.get(
    "pm10",
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
# CURRENT AQI
# ============================================================

current_aqi = float(
    current.get(
        "us_aqi",
        0
    )
)


# ============================================================
# MACHINE LEARNING INPUT
# ============================================================

input_data = pd.DataFrame({

    "pm10": [pm10],

    "pm2_5": [pm25],

    "carbon_monoxide": [co],

    "nitrogen_dioxide": [no2],

    "sulphur_dioxide": [so2],

    "ozone": [o3]

})


# Make sure feature order matches training

input_data = input_data[
    features
]


# ============================================================
# ML PREDICTION
# ============================================================

try:

    predicted_aqi = model.predict(
        input_data
    )[0]

except Exception as e:

    st.error(
        "The ML model could not generate a prediction."
    )

    st.code(str(e))

    st.stop()


predicted_aqi = max(
    0,
    round(
        float(predicted_aqi),
        2
    )
)


# ============================================================
# AQI INFORMATION
# ============================================================

current_category = get_aqi_category(
    current_aqi
)

predicted_category = get_aqi_category(
    predicted_aqi
)

current_icon = get_aqi_icon(
    current_aqi
)

predicted_icon = get_aqi_icon(
    predicted_aqi
)


difference = round(
    predicted_aqi - current_aqi,
    2
)


# ============================================================
# MAIN POLLUTANT
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

    "NO₂": current.get(
        "us_aqi_nitrogen_dioxide",
        0
    ),

    "SO₂": current.get(
        "us_aqi_sulphur_dioxide",
        0
    ),

    "O₃": current.get(
        "us_aqi_ozone",
        0
    )

}


main_pollutant = max(
    pollutant_aqi,
    key=pollutant_aqi.get
)


# ============================================================
# WEATHER
# ============================================================

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
# LOCATION INFORMATION
# ============================================================

st.success(
    f"📍 {city_name}, {country}    |    "
    f"🕐 Updated: {current.get('time', 'Live')}"
)


# ============================================================
# AIR QUALITY OVERVIEW
# ============================================================

st.markdown(
    '<div class="section-title">🌡️ Air Quality Overview</div>',
    unsafe_allow_html=True
)


current_col, prediction_col = st.columns(
    2
)


# ------------------------------------------------------------
# CURRENT AQI
# ------------------------------------------------------------

with current_col:

    st.subheader(
        "Current AQI"
    )

    st.metric(
        label=current_category,
        value=round(current_aqi)
    )

    st.write(
        f"{current_icon} **Main Pollutant:** "
        f"{main_pollutant}"
    )


# ------------------------------------------------------------
# PREDICTED AQI
# ------------------------------------------------------------

with prediction_col:

    st.subheader(
        "🤖 Predicted Next-Hour AQI"
    )

    st.metric(
        label=predicted_category,
        value=predicted_aqi,
        delta=difference
    )

    if difference > 10:

        st.warning(
            "⚠️ AQI is expected to increase "
            "during the next hour."
        )

    elif difference < -10:

        st.success(
            "✅ AQI is expected to improve "
            "during the next hour."
        )

    else:

        st.info(
            "→ AQI is expected to remain relatively stable."
        )


# ============================================================
# LIVE POLLUTION
# ============================================================

st.markdown(
    '<div class="section-title">📡 Live Pollution Levels</div>',
    unsafe_allow_html=True
)


p1, p2, p3, p4, p5, p6 = st.columns(
    6
)


p1.metric(
    "PM2.5",
    f"{pm25:.1f}"
)

p2.metric(
    "PM10",
    f"{pm10:.1f}"
)

p3.metric(
    "CO",
    f"{co:.1f}"
)

p4.metric(
    "NO₂",
    f"{no2:.1f}"
)

p5.metric(
    "SO₂",
    f"{so2:.1f}"
)

p6.metric(
    "O₃",
    f"{o3:.1f}"
)


st.caption(
    "Pollutant concentrations are shown in µg/m³."
)


# ============================================================
# AQI TREND + WEATHER
# ============================================================

trend_col, weather_col = st.columns(
    [2, 1]
)


# ------------------------------------------------------------
# AQI TREND
# ------------------------------------------------------------

with trend_col:

    st.markdown(
        '<div class="section-title">📈 AQI Trend</div>',
        unsafe_allow_html=True
    )

    hourly = air_data.get(
        "hourly",
        {}
    )

    if (
        "time" in hourly
        and "us_aqi" in hourly
    ):

        trend = pd.DataFrame({

            "Time": hourly["time"],

            "AQI": hourly["us_aqi"]

        })


        trend = trend.dropna()


        if not trend.empty:

            fig = px.line(
                trend,
                x="Time",
                y="AQI",
                markers=True,
                title="Next 24 Hours"
            )

            fig.update_layout(
                height=400,
                xaxis_title=None,
                yaxis_title="AQI"
            )

            st.plotly_chart(
                fig,
                use_container_width=True
            )

        else:

            st.info(
                "AQI trend data is not available."
            )

    else:

        st.info(
            "AQI trend data is not available."
        )


# ------------------------------------------------------------
# WEATHER
# ------------------------------------------------------------

with weather_col:

    st.markdown(
        '<div class="section-title">🌤️ Current Weather</div>',
        unsafe_allow_html=True
    )

    st.metric(
        "🌡️ Temperature",
        f"{temperature:.1f} °C"
    )

    st.metric(
        "💧 Humidity",
        f"{humidity:.0f}%"
    )

    st.metric(
        "💨 Wind Speed",
        f"{wind_speed:.1f} km/h"
    )


# ============================================================
# POLLUTANT ANALYSIS
# ============================================================

st.markdown(
    '<div class="section-title">📊 Pollutant Analysis</div>',
    unsafe_allow_html=True
)


pollutant_data = pd.DataFrame({

    "Pollutant": [
        "PM2.5",
        "PM10",
        "CO",
        "NO₂",
        "SO₂",
        "O₃"
    ],

    "Concentration": [
        pm25,
        pm10,
        co,
        no2,
        so2,
        o3
    ]

})


fig_pollution = px.bar(
    pollutant_data,
    x="Pollutant",
    y="Concentration",
    text="Concentration",
    title="Current Pollutant Concentrations"
)


fig_pollution.update_traces(
    texttemplate="%{text:.1f}",
    textposition="outside"
)


fig_pollution.update_layout(
    height=400,
    yaxis_title="µg/m³"
)


st.plotly_chart(
    fig_pollution,
    use_container_width=True
)


# ============================================================
# AI PREDICTION ANALYSIS
# ============================================================

st.markdown(
    '<div class="section-title">🤖 AI Prediction Analysis</div>',
    unsafe_allow_html=True
)


analysis1, analysis2, analysis3 = st.columns(
    3
)


analysis1.metric(
    "Current AQI",
    round(current_aqi)
)

analysis2.metric(
    "Predicted AQI",
    predicted_aqi
)

analysis3.metric(
    "AQI Difference",
    f"{difference:+.2f}"
)


if difference > 10:

    st.warning(
        "⚠️ The model predicts that air quality "
        "may worsen during the next hour."
    )

elif difference < -10:

    st.success(
        "✅ The model predicts that air quality "
        "may improve during the next hour."
    )

else:

    st.info(
        "→ The model predicts relatively stable "
        "air quality during the next hour."
    )


# ============================================================
# HEALTH RECOMMENDATION
# ============================================================

st.markdown(
    '<div class="section-title">'
    '⚠️ Health / Environment Recommendation'
    '</div>',
    unsafe_allow_html=True
)


st.info(
    get_recommendation(
        predicted_aqi
    )
)


# ============================================================
# MACHINE LEARNING DETAILS
# ============================================================

with st.expander(
    "🔬 Machine Learning Model Details"
):

    st.subheader(
        "Extra Trees Regressor"
    )


    ml1, ml2, ml3 = st.columns(
        3
    )


    ml1.metric(
        "R² Score",
        "0.874"
    )

    ml2.metric(
        "RMSE",
        "22.09"
    )

    ml3.metric(
        "MAE",
        "10.88"
    )


    st.write(
        """
        The system compares multiple machine learning
        algorithms and uses the best-performing model
        for next-hour AQI prediction.

        **Input Features**

        • PM2.5
        • PM10
        • Carbon Monoxide (CO)
        • Nitrogen Dioxide (NO₂)
        • Sulphur Dioxide (SO₂)
        • Ozone (O₃)

        **Prediction Target**

        Next-hour AQI

        **Models Compared**

        • Random Forest
        • Extra Trees
        • Gradient Boosting

        Extra Trees achieved the best test performance.
        """
    )


# ============================================================
# HOW THE PROJECT WORKS
# ============================================================

with st.expander(
    "💡 How This System Works"
):

    st.write(
        """
        **1. User enters a city**

        The system accepts a city or location from the user.

        **2. Location detection**

        The location API converts the city into
        latitude and longitude.

        **3. Real-time air-quality data**

        Current PM2.5, PM10, CO, NO₂, SO₂ and O₃
        values are retrieved.

        **4. Data processing**

        The live pollutant values are arranged in
        the same feature order used during model training.

        **5. Machine learning prediction**

        The Extra Trees model predicts the expected
        AQI for the next hour.

        **6. Decision support**

        The application displays the current AQI,
        predicted AQI, trend, main pollutant, weather
        and a general environmental recommendation.
        """
    )


# ============================================================
# IMPORTANT DISCLAIMER
# ============================================================

st.divider()


st.caption(
    "🌐 Real-time data source: Open-Meteo Air Quality "
    "and Weather APIs."
)


st.caption(
    "⚠️ The current implementation uses the US AQI scale. "
    "The application is intended for educational and "
    "project demonstration purposes."
)


# ============================================================
# FOOTER
# ============================================================

st.markdown(
    '<div class="footer">'
    'AI-Based Air Quality Monitoring & Short-Term Prediction System'
    '<br>'
    'Machine Learning • Real-Time APIs • Data Visualization'
    '</div>',
    unsafe_allow_html=True
)