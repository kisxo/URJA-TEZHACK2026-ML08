import { useState } from "react";
import "./App.css";
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
} from "recharts";

function App() {
  const [formData, setFormData] = useState({
    sunlight: "",
    temperature: "",
    cloud_cover: "",
    season: "",
    time: "",
  });

  const [prediction, setPrediction] = useState(null);
  const [history, setHistory] = useState([]);

  const handleChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value,
    });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();

    const data = new URLSearchParams();

    data.append("sunlight", formData.sunlight);
    data.append("temperature", formData.temperature);
    data.append("cloud_cover", formData.cloud_cover);
    data.append("season", formData.season);
    data.append("time", formData.time);

    try {
      const response = await fetch("http://127.0.0.1:8000/predict", {
        method: "POST",
        headers: {
          "Content-Type": "application/x-www-form-urlencoded",
        },
        body: data,
      });

      const result = await response.json();

      setPrediction(result.prediction);

      setHistory((prevHistory) => [
        {
          ...formData,
          prediction: result.prediction,
          date:result.date
        },
        ...prevHistory,
      ]);
    } catch (error) {
      console.error("Error:", error);
      alert("Could not connect to FastAPI");
    }
  };

  return (
    <div className="app">

      <div className="sun"></div> <h1>Solar Power Prediction</h1>

      <div className="container">

        {/* FORM */}
        <div className="form-card">

          <h2>Enter Solar Data</h2>

          <form onSubmit={handleSubmit}>

            <label>Sunlight (hours)</label>
            <input
              type="number"
              name="sunlight"
              step="0.1"
              value={formData.sunlight}
              onChange={handleChange}
              required
            />

            <label>Temperature (°C)</label>
            <input
              type="number"
              name="temperature"
              step="0.1"
              value={formData.temperature}
              onChange={handleChange}
              required
            />

            <label>Cloud Cover (%)</label>
            <input
              type="number"
              name="cloud_cover"
              min="0"
              max="100"
              value={formData.cloud_cover}
              onChange={handleChange}
              required
            />

            <label>Season</label>
            <select
              name="season"
              value={formData.season}
              onChange={handleChange}
              required
            >
              <option value="">Select season</option>
              <option value="Spring">Spring</option>
              <option value="Summer">Summer</option>
              <option value="Autumn">Autumn</option>
              <option value="Winter">Winter</option>
            </select>

            <label>Time</label>
            <input
              type="time"
              name="time"
              value={formData.time}
              onChange={handleChange}
              required
            />

            <button type="submit">
              Predict Solar Power
            </button>

          </form>

          {prediction !== null && (
            <div className="prediction">
              <h2>Predicted Solar Power</h2>
              <div className="prediction-value">
                {prediction} kWh
              </div>
            </div>
          )}

        </div>


        {/* HISTORY */}
        <div className="history-card">

          <h2>📊 Prediction History</h2>

          {history.length === 0 ? (
            <p className="empty">
              No predictions yet.
            </p>
          ) : (

            history.map((item, index) => (

              <div className="history-item" key={index}>

                <p>
                  <strong>Sunlight:</strong>{" "}
                  {item.sunlight} hours
                </p>

                <p>
                  <strong>Temperature:</strong>{" "}
                  {item.temperature} °C
                </p>

                <p>
                  <strong>Cloud Cover:</strong>{" "}
                  {item.cloud_cover}%
                </p>

                <p>
                  <strong>Season:</strong>{" "}
                  {item.season}
                </p>

                <p>
                  <strong>Time:</strong>{" "}
                  {item.time}
                </p>

                <p>
                  <strong>Date</strong>{" "}
                  {item.date}
                </p>

                <p className="history-prediction">
                  <strong>Prediction:</strong>{" "}
                  {item.prediction} kWh
                </p>

              </div>

            ))

          )}

        </div>

      </div>



    </div>


  );
}

export default App;