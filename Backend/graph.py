import pandas as pd
import joblib
import matplotlib.pyplot as plt
from pathlib import Path

# Paths
BASE_DIR = Path(__file__).resolve().parent

TEST_DATA_PATH = BASE_DIR.parent / "data" / "stage-3" / "test_data.csv"
MODEL_PATH = BASE_DIR / "solar_model.pkl"

# Load test data and trained model
df = pd.read_csv(TEST_DATA_PATH)
model = joblib.load(MODEL_PATH)

print("Test data loaded:", len(df), "rows")
print("Model loaded successfully")

# Convert time column
dt = pd.to_datetime(df["time"], format="mixed", dayfirst=True)

# Create the same time features used during training
df["hour"] = dt.dt.hour
df["minute"] = dt.dt.minute
df["day"] = dt.dt.day
df["month"] = dt.dt.month

print("Time features created successfully")

# Select the same features used during training
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

X_test = df[features]

# Predict for every test-data row
predictions = model.predict(X_test)

print("Predictions created for", len(predictions), "rows")

# Add predictions as a new column
df["predicted_generation"] = predictions

print("Predictions added to test data")


# Save as a new CSV file
OUTPUT_PATH = BASE_DIR / "test_data_with_predictions.csv"

df.to_csv(OUTPUT_PATH, index=False)

print("New CSV created successfully!")
print("Saved at:", OUTPUT_PATH)


# Create graph
plt.figure(figsize=(12, 6))

plt.plot(df["normalized_generation"].values,
         label="Actual",
         linewidth=2)

plt.plot(df["predicted_generation"].values,
         label="Predicted",
         linewidth=2)

plt.xlabel("Test Data Row")
plt.ylabel("Normalized Generation")
plt.title("Actual vs Predicted Solar Power")

plt.legend()
plt.grid(True, alpha=0.3)

plt.tight_layout()
plt.show()