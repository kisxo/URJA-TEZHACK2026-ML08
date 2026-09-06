from sqlalchemy import (
    create_engine, Column, String, Boolean, Integer, Float, DateTime, ForeignKey
)
from sqlalchemy.orm import sessionmaker, declarative_base, relationship

sqlite_file_name = "solar_.db"
DATABASE_URL = f"sqlite:///{sqlite_file_name}"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()
 
 
class PredictionRecord(Base):
    __tablename__ = "prediction_history"
 
    # Plain auto-incrementing integer PK; the DB assigns this on insert,
    # so calling code never needs to pass id= at all.
    id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    forecast_only = Column(Boolean, nullable=True, default=False)
    no_of_days = Column(Integer, nullable=True, default=1)
    plot_date = Column(DateTime, nullable=True)
    peak_actual = Column(Float, nullable=True)
    peak_predicted = Column(Float, nullable=True)
    image_path = Column(String, nullable=True)
    created_at = Column(DateTime, nullable=True)
 
    forecast_rows = relationship(
        "ForecastRow", back_populates="prediction_run", cascade="all, delete-orphan"
    )
 
 
class ForecastRow(Base):
    __tablename__ = "forecast_rows"
 
    id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    prediction_id = Column(
        Integer, ForeignKey("prediction_history.id"), nullable=True, index=True
    )
 
    hour = Column(Integer, nullable=True)
    minute = Column(Integer, nullable=True)
    day = Column(Integer, nullable=True)
    month = Column(Integer, nullable=True)
    year = Column(Integer, nullable=True)
    site_id_ttl = Column(String, nullable=True)
    irradiance_wm2 = Column(Float, nullable=True)
    rainfall_mm = Column(Float, nullable=True)
    relative_humidity_pct = Column(Float, nullable=True)
    sea_level_pressure_hpa = Column(Float, nullable=True)
    temperature_c = Column(Float, nullable=True)
    visibility_km = Column(Float, nullable=True)
    wind_speed_ms = Column(Float, nullable=True)
    normalized_generation = Column(Float, nullable=True)
    forecasted_generation = Column(Float, nullable=True)
 
    prediction_run = relationship("PredictionRecord", back_populates="forecast_rows")
 
 
def init_db():
    Base.metadata.create_all(bind=engine)
 
