import pandas as pd
import numpy as np

from sklearn.model_selection import train_test_split

from sklearn.ensemble import (
    RandomForestRegressor,
    ExtraTreesRegressor,
    GradientBoostingRegressor
)

from sklearn.metrics import (
    mean_absolute_error,
    mean_squared_error,
    r2_score
)

import joblib

from pathlib import Path


# ==========================================
# STEP 1: LOAD DATASET
# ==========================================

file_path = "data/air_quality_training_data.csv"

data = pd.read_csv(file_path)

print("Dataset loaded successfully!")

print("\nNumber of rows:", len(data))

print("\nColumns:")
print(data.columns.tolist())


# ==========================================
# STEP 2: DEFINE FEATURES
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


X = data[features]

y = data[target]


# ==========================================
# STEP 3: SPLIT DATA
# ==========================================

X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.20,
    random_state=42
)


print("\n===================================")
print("TRAINING / TESTING DATA")
print("===================================")

print("Training samples:", len(X_train))
print("Testing samples :", len(X_test))


# ==========================================
# STEP 4: CREATE MODELS
# ==========================================

models = {

    "Random Forest": RandomForestRegressor(
        n_estimators=200,
        random_state=42,
        n_jobs=-1
    ),

    "Extra Trees": ExtraTreesRegressor(
        n_estimators=200,
        random_state=42,
        n_jobs=-1
    ),

    "Gradient Boosting": GradientBoostingRegressor(
        random_state=42
    )
}


# ==========================================
# STEP 5: TRAIN MODELS
# ==========================================

results = []

best_model = None
best_model_name = None
best_rmse = float("inf")


print("\n===================================")
print("MODEL TRAINING")
print("===================================")


for name, model in models.items():

    print("\nTraining:", name)

    # Train
    model.fit(X_train, y_train)

    # Predict
    predictions = model.predict(X_test)


    # ======================================
    # EVALUATION
    # ======================================

    mae = mean_absolute_error(
        y_test,
        predictions
    )

    rmse = np.sqrt(
        mean_squared_error(
            y_test,
            predictions
        )
    )

    r2 = r2_score(
        y_test,
        predictions
    )


    print("MAE :", round(mae, 2))
    print("RMSE:", round(rmse, 2))
    print("R²  :", round(r2, 3))


    results.append({
        "Model": name,
        "MAE": mae,
        "RMSE": rmse,
        "R2": r2
    })


    # ======================================
    # FIND BEST MODEL
    # ======================================

    if rmse < best_rmse:

        best_rmse = rmse

        best_model = model

        best_model_name = name


# ==========================================
# STEP 6: SAVE RESULTS
# ==========================================

results_df = pd.DataFrame(results)

print("\n===================================")
print("MODEL COMPARISON")
print("===================================")

print(results_df)


# ==========================================
# STEP 7: SAVE BEST MODEL
# ==========================================

Path("models").mkdir(
    exist_ok=True
)


model_file = "models/aqi_prediction_model.pkl"


joblib.dump(
    best_model,
    model_file
)


# Save feature names too

feature_file = "models/features.pkl"

joblib.dump(
    features,
    feature_file
)


# ==========================================
# STEP 8: FINAL RESULT
# ==========================================

print("\n===================================")

print("BEST MODEL")
print("===================================")

print("Model:", best_model_name)

print("RMSE:", round(best_rmse, 2))

print("\nModel saved successfully!")

print("File:", model_file)

print("===================================")