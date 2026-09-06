import { useEffect, useState } from "react";
import "./App.css";

function App() {
  const [prediction, setPrediction] = useState(null);
  const [imageUrl, setImageUrl] = useState(null);
  const [history, setHistory] = useState([]);
  const [loading, setLoading] = useState(false);
  const [useActual, setUseActual] = useState(false);
  const [days, setDays] = useState(1);

  // Load prediction history
  useEffect(() => {
    const loadHistory = async () => {
      try {
        const response = await fetch("http://127.0.0.1:8000/history");

        if (!response.ok) {
          throw new Error("Failed to load history");
        }

        const data = await response.json();
        setHistory(data);
      } catch (error) {
        console.error("Error loading history:", error);
      }
    };

    loadHistory();
  }, []);

  const handleSubmit = async (e) => {
    e.preventDefault();

    setLoading(true);

    try {
      const response = await fetch(
        `http://127.0.0.1:8000/predict/${useActual}/${days}`,
        {
          method: "POST",
        }
      );

      if (!response.ok) {
        throw new Error("Prediction request failed");
      }

      const result = await response.json();

      setPrediction(result.prediction);
      setImageUrl(result.image_url || null);

      setHistory((prevHistory) => [
        {
          time: result.time,
          irradiance_wm2: result.irradiance_wm2,
          rainfall_mm: result.rainfall_mm,
          relative_humidity_pct: result.relative_humidity_pct,
          sea_level_pressure_hpa: result.sea_level_pressure_hpa,
          temperature_c: result.temperature_c,
          visibility_km: result.visibility_km,
          wind_speed_ms: result.wind_speed_ms,
          prediction: result.prediction,
          date: result.date,
          image_url: result.image_url,
        },
        ...prevHistory,
      ]);
    } catch (error) {
      console.error("Error:", error);
      alert("Could not connect to FastAPI");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="app">
      <div className="sun"></div>

      <h1>Solar Power Prediction</h1>

      <div className="container">
        {prediction !== null && (
          <div className="prediction">
            <h2>Predicted Solar Power</h2>

            {imageUrl && (
              <img
                src={imageUrl}
                alt="Prediction visualization"
                width={1000}
                className="prediction-image"
              />
            )}
          </div>
        )}
      </div>

      {/* FORECAST */}
      <div className="form-card">
        <form onSubmit={handleSubmit}>
          <label>
            <input
              type="checkbox"
              checked={useActual}
              onChange={(e) => setUseActual(e.target.checked)}
            />
            Forecast Only
          </label>

          <label>
            Forecast Days
            <input
              type="number"
              min="1"
              value={days}
              onChange={(e) => setDays(Number(e.target.value))}
            />
          </label>

          <button type="submit" disabled={loading}>
            {loading ? "Generating..." : "Random Forecast"}
          </button>
        </form>
      </div>

      {/* EXPORT */}
      <button
        type="button"
        className="export-button"
        onClick={() => {
          window.location.href = "http://127.0.0.1:8000/export";
        }}
      >
        Export CSV
      </button>

      {/* HISTORY */}
      <div className="history-card">
        <h2>📊 Prediction History</h2>

        {history.length === 0 ? (
          <p className="empty">No predictions yet.</p>
        ) : (
          history.map((item, index) => (
            <div className="history-item" key={index}>
              <p>
                <strong>Irradiance:</strong>{" "}
                {item.irradiance_wm2} W/m²
              </p>

              <p>
                <strong>Rainfall:</strong>{" "}
                {item.rainfall_mm} mm
              </p>

              <p>
                <strong>Humidity:</strong>{" "}
                {item.relative_humidity_pct}%
              </p>

              <p>
                <strong>Pressure:</strong>{" "}
                {item.sea_level_pressure_hpa} hPa
              </p>

              <p>
                <strong>Temperature:</strong>{" "}
                {item.temperature_c} °C
              </p>

              <p>
                <strong>Visibility:</strong>{" "}
                {item.visibility_km} km
              </p>

              <p>
                <strong>Wind Speed:</strong>{" "}
                {item.wind_speed_ms} m/s
              </p>

              <p>
                <strong>Date & Time:</strong>{" "}
                {item.time}
              </p>

              {item.image_url && (
                <img
                  src={item.image_url}
                  alt="Historical prediction visualization"
                  className="history-image"
                />
              )}

              <p className="history-prediction">
                <strong>Prediction:</strong>{" "}
                {item.prediction} kWh
              </p>
            </div>
          ))
        )}
      </div>
    </div>
  );
}

export default App;