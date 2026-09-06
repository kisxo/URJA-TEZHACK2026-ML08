import { useEffect, useState, useCallback } from "react";
import "./App.css";

const API_BASE = "http://127.0.0.1:8000";

function formatDate(isoString) {
  if (!isoString) return "—";
  const d = new Date(isoString);
  if (Number.isNaN(d.getTime())) return isoString;
  return d.toLocaleString();
}

function App() {
  const [imageUrl, setImageUrl] = useState(null);
  const [history, setHistory] = useState([]);
  const [loading, setLoading] = useState(false);
  const [historyLoading, setHistoryLoading] = useState(true);
  const [historyError, setHistoryError] = useState(null);
  const [forecastOnly, setForecastOnly] = useState(false);
  const [days, setDays] = useState(1);

  const loadHistory = useCallback(async () => {
    setHistoryLoading(true);
    setHistoryError(null);
    try {
      const response = await fetch(`${API_BASE}/history`);
      if (!response.ok) {
        throw new Error("Failed to load history");
      }
      const data = await response.json();
      setHistory(data);
    } catch (error) {
      console.error("Error loading history:", error);
      setHistoryError(error.message || "Failed to load history");
    } finally {
      setHistoryLoading(false);
    }
  }, []);

  // Load prediction history on mount
  useEffect(() => {
    loadHistory();
  }, [loadHistory]);

  const handleSubmit = async (e) => {
    e.preventDefault();

    if (!Number.isInteger(days) || days < 1) {
      alert("Forecast days must be a positive whole number");
      return;
    }

    setLoading(true);

    try {
      const response = await fetch(
        `${API_BASE}/predict/${forecastOnly}/${days}`,
        { method: "POST" }
      );

      if (!response.ok) {
        const body = await response.json().catch(() => null);
        throw new Error(body?.error || "Prediction request failed");
      }

      const result = await response.json();

      // /predict only returns { image_url }. The full record (peak values,
      // plot_date, etc.) lives in the DB, so refetch history rather than
      // trying to fabricate a history row from fields the endpoint doesn't
      // return.
      setImageUrl(result.image_url || null);
      await loadHistory();
    } catch (error) {
      console.error("Error:", error);
      alert(error.message || "Could not connect to FastAPI");
    } finally {
      setLoading(false);
    }
  };

  const handleClearHistory = async (e) => {
    e.preventDefault();
    window.confirm("This will delete all history!")

    setLoading(true);

    try {
      const response = await fetch(
        `${API_BASE}/history/clear`,
        { method: "DELETE" }
      );

      if (!response.ok) {
        const body = await response.json().catch(() => null);
        throw new Error(body?.error || "Prediction request failed");
      }

      await loadHistory();
    } catch (error) {
      console.error("Error:", error);
      alert(error.message || "Could not connect to FastAPI");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="app">
      <div className="sun"></div>

      <h1>Solar Power Prediction</h1>

      <div className="container">
        {imageUrl && (
          <div className="prediction">
            <h2>Predicted Solar Power</h2>
            <img
              src={imageUrl}
              alt="Prediction visualization"
              width={1000}
              className="prediction-image"
            />
          </div>
        )}
      </div>

      {/* FORECAST */}
      <div className="form-card">
        <form onSubmit={handleSubmit}>

          <label>
            <input
              type="checkbox"
              checked={forecastOnly}
              onChange={(e) => setForecastOnly(e.target.checked)}
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

            <button onClick={handleClearHistory} className="clear" disabled={loading}>
              {loading ? "Clearing..." : "Clear History"}
            </button>

            <button type="submit" disabled={loading}>
              {loading ? "Generating..." : "Forecast"}
            </button>
        </form>
      </div>

      {/* HISTORY */}
      <div className="history-card">
        <h2>Prediction History</h2>

        {historyLoading && <p className="loading">Loading history…</p>}

        {!historyLoading && historyError && (
          <p className="error">{historyError}</p>
        )}

        {!historyLoading && !historyError && history.length === 0 && (
          <p className="empty">No predictions yet.</p>
        )}

        {!historyLoading &&
          !historyError &&
          history.map((item) => (
            <div className="history-item" key={item.id}>
              <p>
                <strong>Run Date:</strong> {formatDate(item.plot_date)}
              </p>

              <p>
                <strong>Mode:</strong>{" "}
                {item.forecast_only ? "Forecast" : "Actual"}
              </p>

              <p>
                <strong>Days:</strong> {item.no_of_days}
              </p>

              <p>
                <strong>Peak Actual:</strong>{" "}
                {item.peak_actual != null
                  ? `${item.peak_actual.toFixed(3)} kWh`
                  : "—"}
              </p>

              <p>
                <strong>Peak Predicted:</strong>{" "}
                {item.peak_predicted != null
                  ? `${item.peak_predicted.toFixed(3)} kWh`
                  : "—"}
              </p>

              {item.image_path && (
                <a
                  href={`${API_BASE}/${item.image_path}`}
                  target="_blank"
                  rel="noopener noreferrer"
                >
                  <img
                    src={`${API_BASE}/${item.image_path}`}
                    alt="Historical prediction visualization"
                    className="history-image"
                  />
                </a>
              )}

              <p>
                <strong>Created:</strong> {formatDate(item.created_at)}
              </p>

              <button
                type="button"
                className="export-button export-button--small"
                onClick={() => {
                  window.location.href = `${API_BASE}/export/${item.id}`;
                }}
              >
                Export CSV
              </button>
            </div>
          ))}
      </div>
    </div>
  );
}

export default App;