import os
import uuid
from datetime import datetime, timezone

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import joblib

from db import init_db, SessionLocal, PredictionRecord, ForecastRow


# Resolve paths relative to this file, not the process's current working
# directory, so the script works no matter where it's invoked from.
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ACTUAL_DATA_PATH = os.path.join(BASE_DIR, "stage-3", "actual_data.csv")
FORECAST_DATA_PATH = os.path.join(BASE_DIR, "stage-3", "forecast_data.csv")

ORIGINAL_FORECAST_COLUMNS = [
    'hour', 'minute', 'day', 'month', 'year', 'site_id_ttl',
    'irradiance_wm2', 'rainfall_mm', 'relative_humidity_pct',
    'sea_level_pressure_hpa', 'temperature_c', 'visibility_km', 'wind_speed_ms',
    'normalized_generation',
]

FEATURES = [
    'hour_sin', 'hour_cos', 'month_sin', 'month_cos', 'day',
    'irradiance_wm2', 'rainfall_mm', 'relative_humidity_pct',
    'sea_level_pressure_hpa', 'temperature_c', 'visibility_km', 'wind_speed_ms',
    'site_id_ttl',
]
TARGET = 'normalized_generation'


def _load_dataset(forecast_only: bool) -> pd.DataFrame:
    path = FORECAST_DATA_PATH if forecast_only else ACTUAL_DATA_PATH
    df = pd.read_csv(path)

    missing = set(ORIGINAL_FORECAST_COLUMNS) - set(df.columns)
    if missing:
        raise ValueError(f"Input CSV '{path}' is missing required columns: {sorted(missing)}")

    return df


def _add_cyclical_features(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df['hour_sin'] = np.sin(2 * np.pi * df['hour'] / 24)
    df['hour_cos'] = np.cos(2 * np.pi * df['hour'] / 24)
    df['month_sin'] = np.sin(2 * np.pi * df['month'] / 12)
    df['month_cos'] = np.cos(2 * np.pi * df['month'] / 12)
    return df


def random_predict(forecast_only: bool = False, model: str = 'xg', no_of_days: int = 1):
    """
    Run the trained model against a dataset, plot a randomly chosen window of
    `no_of_days` days, persist the run + row-level forecasts to the DB, and
    return a summary dict.
    """
    if no_of_days < 1:
        raise ValueError("no_of_days must be >= 1")

    MODEL_PATH = f"urja-{model}.joblib"

    if not os.path.exists(MODEL_PATH):
        raise FileNotFoundError(f"Model file not found at {MODEL_PATH}")


    model = joblib.load(MODEL_PATH)

    dataset_df = _load_dataset(forecast_only)

    # Keep only the original columns (drop engineered features later), before
    # anything else mutates dataset_df. Reset the index explicitly so that
    # positional alignment with numpy arrays (y_test.values, y_pred3, mask)
    # is guaranteed regardless of what pd.read_csv/dtype casting might do.
    dataset_df = dataset_df.reset_index(drop=True)
    save_df = dataset_df[ORIGINAL_FORECAST_COLUMNS].copy()

    dataset_df = _add_cyclical_features(dataset_df)

    # Cast categorical column to match training dtype.
    dataset_df['site_id_ttl'] = dataset_df['site_id_ttl'].astype('category')

    try:
        dataset_df['datetime'] = pd.to_datetime(
            dataset_df[['year', 'month', 'day', 'hour', 'minute']]
        )
    except (ValueError, KeyError) as exc:
        raise ValueError(f"Could not construct datetime column from input data: {exc}") from exc

    X_test = dataset_df[FEATURES]
    y_test = dataset_df[TARGET]

    y_pred3 = model.predict(X_test)

    # Append the forecast to the clean saved dataframe. Both save_df and
    # dataset_df share the same reset RangeIndex, so this assignment aligns
    # by row order correctly.
    save_df['forecasted_generation'] = y_pred3

    available_days = dataset_df['datetime'].dt.normalize().unique()
    if len(available_days) == 0:
        raise ValueError("No dates available in dataset to sample from.")

    max_start_offset = max(len(available_days) - no_of_days, 0)
    if max_start_offset == 0:
        random_day = pd.Timestamp(available_days.min())
    else:
        # Pick a random valid start day such that [start, start + no_of_days)
        # stays within the available date range where possible.
        sorted_days = np.sort(available_days)
        start_idx = np.random.randint(0, len(sorted_days) - no_of_days + 1) \
            if len(sorted_days) >= no_of_days else 0
        random_day = pd.Timestamp(sorted_days[start_idx])

    window_end = random_day + pd.Timedelta(days=no_of_days)
    mask = ((dataset_df['datetime'] >= random_day) & (dataset_df['datetime'] < window_end)).to_numpy()

    if not mask.any():
        raise ValueError(f"No rows found in window {random_day} to {window_end}.")

    times = dataset_df.loc[mask, 'datetime']
    actual_vals = y_test.to_numpy()[mask]
    pred_vals = y_pred3[mask]

    peak_actual = float(np.nanmax(actual_vals))
    peak_pred = float(np.nanmax(pred_vals))

    fig, ax = plt.subplots(figsize=(14, 6))

    ax.plot(times, actual_vals, color='black', linewidth=1.5, label='Actual')
    ax.plot(times, pred_vals, color='#2ecc71', linewidth=1.5, label='Forecast')
    ax.axhline(y=0.01, color='red', linewidth=1, linestyle='-', label='Low Generation (0.01)')
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
    filename = f'images/{uuid.uuid4()}.png'
    plt.savefig(filename, dpi=300, bbox_inches='tight', facecolor='white')
    plt.close(fig)

    print(f"Plotted window starting: {random_day.strftime('%Y-%m-%d')} ({no_of_days} day(s))")
    print(f"Saved to {filename}")

    # --- Store prediction result in DB after prediction ---
    init_db()
    session = SessionLocal()
    try:
        record = PredictionRecord(
            forecast_only=forecast_only,
            no_of_days=no_of_days,
            plot_date=random_day.to_pydatetime(),
            peak_actual=peak_actual,
            peak_predicted=peak_pred,
            image_path=filename,
            created_at=datetime.now(timezone.utc),
        )
        session.add(record)
        session.commit()
        session.refresh(record)

        # --- Bulk store the forecast dataframe, linked to this prediction run ---
        forecast_rows = [
            ForecastRow(
                prediction_id=record.id,
                hour=int(row.hour),
                minute=int(row.minute),
                day=int(row.day),
                month=int(row.month),
                year=int(row.year),
                site_id_ttl=str(row.site_id_ttl),
                irradiance_wm2=float(row.irradiance_wm2),
                rainfall_mm=float(row.rainfall_mm),
                relative_humidity_pct=float(row.relative_humidity_pct),
                sea_level_pressure_hpa=float(row.sea_level_pressure_hpa),
                temperature_c=float(row.temperature_c),
                visibility_km=float(row.visibility_km),
                wind_speed_ms=float(row.wind_speed_ms),
                normalized_generation=float(row.normalized_generation),
                forecasted_generation=float(row.forecasted_generation),
            )
            for row in save_df.itertuples(index=False)
        ]
        session.bulk_save_objects(forecast_rows)
        session.commit()

        result = {
            "id": record.id,
            "image_path": filename,
            "plot_date": record.plot_date.isoformat(),
            "peak_actual": record.peak_actual,
            "peak_predicted": record.peak_predicted,
            "created_at": record.created_at.isoformat(),
            "forecast_rows_stored": len(forecast_rows),
        }
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()

    return result


if __name__ == "__main__":
    random_predict(forecast_only=False, no_of_days=1)