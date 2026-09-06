import csv
import io

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import StreamingResponse, JSONResponse

from predict import random_predict
from db import SessionLocal, ForecastRow, PredictionRecord, init_db

app = FastAPI()

# ==============================
# Allow React frontend
# ==============================
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.post("/predict/{forecast_only}/{model}/{days}")
def predict(forecast_only: bool, model: str, days: str):
    try:
        valid_days = int(days)
    except (TypeError, ValueError):
        valid_days = 0

    if valid_days < 1:
        return JSONResponse(status_code=400, content={"error": "days must be a positive integer"})

    try:
        record = random_predict(forecast_only, model, valid_days)
    except Exception as e:
        print(e)
        return JSONResponse(status_code=500, content={"error": str(e)})

    # record is a dict (see predict.py), and image_path is already a full
    # relative path like "images/<uuid>.png" — don't prefix with a slash
    # twice or index into it as if it were an object.
    image_path = record["image_path"]
    return {"image_url": f"http://127.0.0.1:8000/{image_path}"}


@app.get("/history")
def get_history():
    db = SessionLocal()
    try:
        history = db.query(PredictionRecord).order_by(PredictionRecord.id.desc()).all()
        return [_prediction_record_to_dict(item) for item in history]
    finally:
        db.close()


CSV_HEADER = [
    "ID",
    "Prediction ID",
    "Year",
    "Month",
    "Day",
    "Hour",
    "Minute",
    "Site ID",
    "Irradiance",
    "Rainfall",
    "Humidity",
    "Pressure",
    "Temperature",
    "Visibility",
    "Wind Speed",
    "Actual Generation",
    "Forecasted Generation",
]


def _forecast_row_to_csv_row(item: ForecastRow) -> list:
    return [
        item.id,
        item.prediction_id,
        item.year,
        item.month,
        item.day,
        item.hour,
        item.minute,
        item.site_id_ttl,
        item.irradiance_wm2,
        item.rainfall_mm,
        item.relative_humidity_pct,
        item.sea_level_pressure_hpa,
        item.temperature_c,
        item.visibility_km,
        item.wind_speed_ms,
        item.normalized_generation,
        item.forecasted_generation,
    ]


def _rows_to_csv_response(rows: list[ForecastRow], filename: str) -> StreamingResponse:
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(CSV_HEADER)
    for item in rows:
        writer.writerow(_forecast_row_to_csv_row(item))
    output.seek(0)

    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename={filename}"},
    )


@app.get("/export")
def export_csv():
    db = SessionLocal()
    try:
        history = db.query(ForecastRow).order_by(ForecastRow.id.desc()).all()
        return _rows_to_csv_response(history, "solar_predictions.csv")
    finally:
        db.close()


@app.get("/export/{prediction_id}")
def export_csv_for_prediction(prediction_id: int):
    db = SessionLocal()
    try:
        record = db.query(PredictionRecord).filter(PredictionRecord.id == prediction_id).first()
        if record is None:
            return JSONResponse(status_code=404, content={"error": "Prediction run not found"})

        rows = (
            db.query(ForecastRow)
            .filter(ForecastRow.prediction_id == prediction_id)
            .order_by(ForecastRow.id.asc())
            .all()
        )
        return _rows_to_csv_response(rows, f"solar_prediction_{prediction_id}.csv")
    finally:
        db.close()


@app.delete("/history/clear")
def clear_history():
    """Clear all prediction records and their cascade-linked forecast rows from the database."""
    init_db()
    session = SessionLocal()
    try:
        # Query and delete all prediction records; SQLAlchemy cascade handles the child forecast rows automatically
        deleted_predictions = session.query(PredictionRecord).delete()
        session.commit()

        return {
            "status": "success",
            "message": "History and related forecast rows cleared successfully.",
            "deleted_predictions": deleted_predictions,
        }
    except Exception as e:
        session.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Failed to clear history: {str(e)}",
        )
    finally:
        session.close()


def _prediction_record_to_dict(item: PredictionRecord) -> dict:
    return {
        "id": item.id,
        "forecast_only": item.forecast_only,
        "no_of_days": item.no_of_days,
        "plot_date": item.plot_date.isoformat() if item.plot_date else None,
        "peak_actual": item.peak_actual,
        "peak_predicted": item.peak_predicted,
        "image_path": item.image_path,
        "created_at": item.created_at.isoformat() if item.created_at else None,
    }


def _forecast_row_to_dict(item: ForecastRow) -> dict:
    return {
        "id": item.id,
        "prediction_id": item.prediction_id,
        "year": item.year,
        "month": item.month,
        "day": item.day,
        "hour": item.hour,
        "minute": item.minute,
        "site_id_ttl": item.site_id_ttl,
        "irradiance_wm2": item.irradiance_wm2,
        "rainfall_mm": item.rainfall_mm,
        "relative_humidity_pct": item.relative_humidity_pct,
        "sea_level_pressure_hpa": item.sea_level_pressure_hpa,
        "temperature_c": item.temperature_c,
        "visibility_km": item.visibility_km,
        "wind_speed_ms": item.wind_speed_ms,
        "normalized_generation": item.normalized_generation,
        "forecasted_generation": item.forecasted_generation,
    }


# Serve generated plot images. Must be mounted after routes are defined so
# the more specific routes above take precedence.
app.mount("/images", StaticFiles(directory="images"), name="images")