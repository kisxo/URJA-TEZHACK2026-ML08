from fastapi import FastAPI, Form
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime
from pathlib import Path
import pandas as pd
import joblib

from sqlalchemy import create_engine, Column, Integer, Float, DateTime
from sqlalchemy.orm import declarative_base, sessionmaker


# update
import csv
from fastapi.responses import StreamingResponse
import io

app = FastAPI()


# SQLite database
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
DATABASE_PATH = BASE_DIR / "solar_prediction.db"

DATABASE_URL = f"sqlite:///{DATABASE_PATH}"
print("running")

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False}
)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

Base = declarative_base()

class Prediction(Base):
    __tablename__ = "predictions"

    id = Column(Integer, primary_key=True, index=True)
    time = Column(DateTime)

    irradiance_wm2 = Column(Float)
    rainfall_mm = Column(Float)
    relative_humidity_pct = Column(Float)
    sea_level_pressure_hpa = Column(Float)
    temperature_c = Column(Float)
    visibility_km = Column(Float)
    wind_speed_ms = Column(Float)

    prediction = Column(Float)

Base.metadata.create_all(bind=engine)


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


# ==============================
# Load trained model
# ==============================

model_path = Path(__file__).parent / "solar_model.pkl"
model = joblib.load(model_path)


# ==============================
# Prediction
# ==============================

@app.post("/predict")
def predict(
    time: str = Form(...),
    irradiance_wm2: float = Form(...),
    rainfall_mm: float = Form(...),
    relative_humidity_pct: float = Form(...),
    sea_level_pressure_hpa: float = Form(...),
    temperature_c: float = Form(...),
    visibility_km: float = Form(...),
    wind_speed_ms: float = Form(...),
):

    # Convert time from React into datetime
    dt = datetime.fromisoformat(time)

    # Extract time features used during model training
    hour = dt.hour
    minute = dt.minute
    day = dt.day
    month = dt.month

    # Create input in the SAME order used during training
    input_data = pd.DataFrame([{
        "hour": hour,
        "minute": minute,
        "day": day,
        "month": month,
        "irradiance_wm2": irradiance_wm2,
        "rainfall_mm": rainfall_mm,
        "relative_humidity_pct": relative_humidity_pct,
        "sea_level_pressure_hpa": sea_level_pressure_hpa,
        "temperature_c": temperature_c,
        "visibility_km": visibility_km,
        "wind_speed_ms": wind_speed_ms
    }])

    # Get prediction from trained model
    prediction = model.predict(input_data)[0]

    db = SessionLocal()

    new_prediction = Prediction(
        time=dt,
        irradiance_wm2=irradiance_wm2,
        rainfall_mm=rainfall_mm,
        relative_humidity_pct=relative_humidity_pct,
        sea_level_pressure_hpa=sea_level_pressure_hpa,
        temperature_c=temperature_c,
        visibility_km=visibility_km,
        wind_speed_ms=wind_speed_ms,
        prediction=float(prediction)
    )
    
    db.add(new_prediction)
    db.commit()
    db.close()

    print("Prediction:", prediction)

    # Return prediction to React
    return {
        "prediction": round(float(prediction), 4),
        "date": str(dt.date())
    }


@app.get("/history")
def get_history():
    db = SessionLocal()

    history = db.query(Prediction).order_by(Prediction.id.desc()).all()

    db.close()

    return [
        {
            "id": item.id,
            "time": item.time,
            "irradiance_wm2": item.irradiance_wm2,
            "rainfall_mm": item.rainfall_mm,
            "relative_humidity_pct": item.relative_humidity_pct,
            "sea_level_pressure_hpa": item.sea_level_pressure_hpa,
            "temperature_c": item.temperature_c,
            "visibility_km": item.visibility_km,
            "wind_speed_ms": item.wind_speed_ms,
            "prediction": item.prediction
        }
        for item in history
    ]

#to csv
@app.get("/export")
def export_csv():
    db = SessionLocal()

    history = db.query(Prediction).order_by(Prediction.id.desc()).all()

    db.close()

    output = io.StringIO()
    writer = csv.writer(output)

    writer.writerow([
        "ID",
        "Time",
        "Irradiance",
        "Rainfall",
        "Humidity",
        "Pressure",
        "Temperature",
        "Visibility",
        "Wind Speed",
        "Prediction"
    ])

    for item in history:
        writer.writerow([
            item.id,
            item.time,
            item.irradiance_wm2,
            item.rainfall_mm,
            item.relative_humidity_pct,
            item.sea_level_pressure_hpa,
            item.temperature_c,
            item.visibility_km,
            item.wind_speed_ms,
            item.prediction
        ])

    output.seek(0)

    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={
            "Content-Disposition": "attachment; filename=solar_predictions.csv"
        }
    )