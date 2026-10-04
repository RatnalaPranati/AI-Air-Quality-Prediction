# 🌍 AI-Based Real-Time Air Quality Prediction System

An AI/ML-based web application that provides real-time air quality information and predicts the **next-hour AQI** using machine learning.

## 📌 Project Overview

Air pollution is a major environmental and public health concern. This project combines real-time environmental data from Open-Meteo APIs with machine learning to analyze current air quality and predict the expected Air Quality Index (AQI) for the next hour.

The system uses an **Extra Trees Regressor** trained on historical air-quality data and provides an interactive web dashboard where users can enter a city and view air-quality information.

## 🎯 Objectives

- Monitor real-time air quality for a selected city
- Analyze major air pollutants
- Predict the next-hour AQI using machine learning
- Display current weather conditions
- Provide AQI category and health recommendations
- Visualize recent AQI trends
- Build an easy-to-use web interface for users

## ✨ Features

- 🌍 City-based air quality search
- 📊 Real-time AQI information
- 🤖 ML-based next-hour AQI prediction
- 🧪 Pollutant analysis
- 🌡️ Weather information
- 📈 24-hour AQI trend visualization
- 🏥 Health recommendations
- 💻 Responsive web interface
- 🔄 Real-time data from Open-Meteo APIs

## 🧠 Machine Learning

The project compares multiple machine learning algorithms:

- Random Forest Regressor
- Extra Trees Regressor
- Gradient Boosting Regressor

The **Extra Trees Regressor** provided the best performance and was selected for the final prediction system.

### Model Performance

| Metric | Value |
|---|---:|
| R² Score | 0.874 |
| RMSE | 22.09 |
| MAE | 10.88 |

### Input Features

The model uses the following air-quality parameters:

- PM10
- PM2.5
- Carbon Monoxide (CO)
- Nitrogen Dioxide (NO₂)
- Sulphur Dioxide (SO₂)
- Ozone (O₃)

### Prediction

The trained model predicts the **expected AQI for the next hour**.

## 🌐 Data Sources

The application uses Open-Meteo APIs for:

- Geocoding
- Air Quality Data
- Weather Data

The AQI displayed by the application follows the **US AQI scale**.

## 📊 AQI Categories

| AQI Range | Category |
|---|---|
| 0–50 | Good |
| 51–100 | Moderate |
| 101–150 | Unhealthy for Sensitive Groups |
| 151–200 | Unhealthy |
| 201–300 | Very Unhealthy |
| 301+ | Hazardous |

## 🏗️ System Architecture

```text
User
  ↓
Enter City
  ↓
Geocoding API
  ↓
Latitude & Longitude
  ↓
Open-Meteo Air Quality API
  ↓
Real-Time Pollutant Data
  ↓
Machine Learning Model
  ↓
Next-Hour AQI Prediction
  ↓
Flask Backend
  ↓
Web Dashboard
  ↓
AQI + Pollutants + Weather + Prediction + Recommendations
Technologies Used
Frontend
- HTML
- CSS
- JavaScript
- Chart.js
Backend
- Python
- Flask
- REST APIs
Machine Learning
- Scikit-learn
- Pandas
- NumPy
- Joblib
APIs
- Open-Meteo Geocoding API
- Open-Meteo Air Quality API
- Open-Meteo Weather API
Project Structure
AI-Air-Quality-Prediction/
│
├── data/
│   └── air_quality_training_data.csv
│
├── models/
│   ├── aqi_prediction_model.pkl
│   └── features.pkl
│
├── static/
│   ├── script.js
│   └── style.css
│
├── templates/
│   └── index.html
│
├── web_app.py
├── streamlit_app.py
├── train_ml_model.py
├── train_model.py
├── live_city_aqi.py
├── live_prediction.py
├── geocoding_test.py
├── test_api.py
├── requirements.txt
└── .python-version
How to Run Locally
git clone https://github.com/RatnalaPranati/AI-Air-Quality-Prediction.git
Open the project
cd AI-Air-Quality-Prediction

3. Create a virtual environment
python -m venv venv

4. Activate the virtual environment
Windows:
venv\Scripts\activate

5. Install dependencies
pip install -r requirements.txt

6. Run the Flask application
python web_app.py

7. Open in browser
http://127.0.0.1:5000

Future Scope
- Deep learning-based AQI prediction
- LSTM-based time-series forecasting
- More advanced pollutant forecasting
- City-to-city AQI comparison
- Interactive historical AQI analytics
- Personalized health recommendations
- Mobile application
- Cloud deployment and scalability
- Integration with additional environmental datasets
