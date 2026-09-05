import pandas as pd
from pathlib import Path
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
import joblib

# update

# 1. Load data
train_path = Path("../data/stage-3/training_data.csv")
test_path = Path("../data/stage-3/test_data.csv")

train = pd.read_csv(train_path)
test = pd.read_csv(test_path)

# 2. Convert time into useful numerical features
for df in [train, test]:
    df["time"] = pd.to_datetime(df["time"])
    df["hour"] = df["time"].dt.hour
    df["minute"] = df["time"].dt.minute
    df["day"] = df["time"].dt.day
    df["month"] = df["time"].dt.month

# 3. Select input features
features = [
    "hour",
    "minute",
    "day",
    "month",
    "irradiance_wm2",
    "rainfall_mm",
    "relative_humidity_pct",
    "sea_level_pressure_hpa",
    "temperature_c",
    "visibility_km",
    "wind_speed_ms"
]

X_train = train[features]
y_train = train["normalized_generation"]

X_test = test[features]
y_test = test["normalized_generation"]

# 4. Create Linear Regression model
model = LinearRegression()

# 5. Train the model
model.fit(X_train, y_train)

# 6. Make predictions
predictions = model.predict(X_test)

# 7. Evaluate
mae = mean_absolute_error(y_test, predictions)
rmse = mean_squared_error(y_test, predictions) ** 0.5
r2 = r2_score(y_test, predictions)

print("Model Training Complete!")
print("-------------------------")
print(f"MAE  : {mae:.4f}")
print(f"RMSE : {rmse:.4f}")
print(f"R²   : {r2:.4f}")

# 8. Save trained model
joblib.dump(model, "solar_model.pkl")

print("\nModel saved as solar_model.pkl")