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

    # Used only for comparison
    "Random Forest": RandomForestRegressor(
        n_estimators=50,
        max_depth=12,
        min_samples_leaf=3,
        random_state=42,
        n_jobs=-1
    ),

    # Lightweight model selected for deployment
    "Extra Trees": ExtraTreesRegressor(
        n_estimators=50,
        max_depth=12,
        min_samples_leaf=3,
        random_state=42,
        n_jobs=-1
    ),

    # Used for comparison
    "Gradient Boosting": GradientBoostingRegressor(
        n_estimators=100,
        max_depth=3,
        random_state=42
    )
}


# ==========================================
# STEP 5: TRAIN MODELS
# ==========================================

results = []

extra_trees_model = None
extra_trees_rmse = None

print("\n===================================")
print("MODEL TRAINING")
print("===================================")


for name, model in models.items():

    print("\nTraining:", name)

    model.fit(X_train, y_train)

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

    # Keep Extra Trees model separately
    if name == "Extra Trees":
        extra_trees_model = model
        extra_trees_rmse = rmse


# ==========================================
# STEP 6: MODEL COMPARISON
# ==========================================

results_df = pd.DataFrame(results)

print("\n===================================")
print("MODEL COMPARISON")
print("===================================")

print(results_df.to_string(index=False))


# ==========================================
# STEP 7: SELECT EXTRA TREES
# ==========================================

print("\n===================================")
print("DEPLOYMENT MODEL")
print("===================================")

print("Selected model: Extra Trees")

print(
    "Reason: Extra Trees provides competitive "
    "accuracy with a smaller model suitable "
    "for free cloud deployment."
)

print(
    "Extra Trees RMSE:",
    round(extra_trees_rmse, 2)
)


# ==========================================
# STEP 8: SAVE EXTRA TREES MODEL
# ==========================================

Path("models").mkdir(
    exist_ok=True
)

model_file = "models/aqi_prediction_model.pkl"

joblib.dump(
    extra_trees_model,
    model_file,
    compress=3
)


# ==========================================
# STEP 9: SAVE FEATURE NAMES
# ==========================================

feature_file = "models/features.pkl"

joblib.dump(
    features,
    feature_file
)


# ==========================================
# STEP 10: CHECK MODEL SIZE
# ==========================================

model_size_mb = (
    Path(model_file).stat().st_size
    / (1024 * 1024)
)


# ==========================================
# STEP 11: FINAL RESULT
# ==========================================

print("\n===================================")
print("FINAL MODEL")
print("===================================")

print("Model:", "Extra Trees")

print("RMSE:", round(extra_trees_rmse, 2))

print("Model file size:",
      round(model_size_mb, 2),
      "MB")

print("\nModel saved successfully!")

print("File:", model_file)

print("Features saved:", feature_file)

print("===================================")