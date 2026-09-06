import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import joblib
from xgboost import XGBRegressor


def random_predict():
    model = joblib.load("urja.joblib")

    dataset_df = pd.read_csv('stage-3/test_data.csv')

    for d in [dataset_df]:
        d['hour_sin'] = np.sin(2 * np.pi * d['hour'] / 24)
        d['hour_cos'] = np.cos(2 * np.pi * d['hour'] / 24)
        d['month_sin'] = np.sin(2 * np.pi * d['month'] / 12)
        d['month_cos'] = np.cos(2 * np.pi * d['month'] / 12)

    features = [
        'hour_sin', 'hour_cos', 'month_sin', 'month_cos', 'day',
        'irradiance_wm2', 'rainfall_mm', 'relative_humidity_pct',
        'sea_level_pressure_hpa', 'temperature_c', 'visibility_km', 'wind_speed_ms',
        'site_id_ttl'
    ]
    target = 'normalized_generation'

    dataset_df['datetime'] = pd.to_datetime(dataset_df[['year', 'month', 'day', 'hour', 'minute']])

    # IMPORTANT: cast categorical column to match training dtype
    dataset_df['site_id_ttl'] = dataset_df['site_id_ttl'].astype('category')

    X_test = dataset_df[features]
    y_test = dataset_df[target]

    y_pred3 = model.predict(X_test)

    # Use dataset_df consistently (was test_df — undefined before)
    available_days = dataset_df['datetime'].dt.date.unique()
    random_day = np.random.choice(available_days)
    random_day = pd.Timestamp(random_day)

    mask = (dataset_df['datetime'] >= random_day) & (dataset_df['datetime'] < random_day + pd.Timedelta(days=2))
    mask = mask.values  # convert to numpy boolean array once, use everywhere

    times = dataset_df.loc[mask, 'datetime']
    actual_vals = y_test.values[mask]
    pred_vals = y_pred3[mask]

    peak_actual = actual_vals.max()
    peak_pred = pred_vals.max()

    fig, ax = plt.subplots(figsize=(14, 6))

    ax.plot(times, actual_vals, color='black', linewidth=1.5, label='Actual')
    ax.plot(times, pred_vals, color='#2ecc71', linewidth=1.5, label='Model 3')

    ax.set_title('Actual vs Model 3 — All Sites', fontsize=13)
    ax.set_xlabel('Time')
    ax.set_ylabel('normalized_generation')
    ax.legend(loc='upper right', frameon=True)
    ax.grid(alpha=0.3)

    label_text = (
        f"{random_day.strftime('%B %d, %Y')}\n"
        f"Peak Actual: {peak_actual:.3f} kwh\n"
        f"Peak Predicted: {peak_pred:.3f} kwh"
    )

    ax.text(
        0.02, 0.95, label_text,
        transform=ax.transAxes,
        fontsize=12, fontweight='bold',
        verticalalignment='top',
        bbox=dict(boxstyle='round,pad=0.5', facecolor='white', edgecolor='gray', alpha=0.9)
    )

    plt.tight_layout()
    plt.savefig('actual_vs_model3_random_day.png', dpi=150, bbox_inches='tight', facecolor='white')
    print(f"Plotted random day: {random_day.strftime('%Y-%m-%d')}")
    print("Saved to actual_vs_model3_random_day.png")


if __name__ == "__main__":
    random_predict()