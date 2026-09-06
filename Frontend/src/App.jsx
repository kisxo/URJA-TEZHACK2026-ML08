import { useState, useEffect } from "react";
import "./App.css";

function App() {
  const [formData, setFormData] = useState({
    time: "",
    irradiance_wm2: "",
    rainfall_mm: "",
    relative_humidity_pct: "",
    sea_level_pressure_hpa: "",
    temperature_c: "",
    visibility_km: "",
    wind_speed_ms: "",
  });

  const [prediction, setPrediction] = useState(null);
  const [history, setHistory] = useState([]);

  useEffect(() => {
    fetch("http://127.0.0.1:8000/history")
      .then((response) => response.json())
      .then((data) => {
        setHistory(data);
      })
      .catch((error) => {
        console.error("Error loading history:", error);
      });
  }, []);

  const handleChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value,
    });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();

    const data = new URLSearchParams();

    data.append("time", formData.time);
    data.append("irradiance_wm2", formData.irradiance_wm2);
    data.append("rainfall_mm", formData.rainfall_mm);
    data.append("relative_humidity_pct", formData.relative_humidity_pct);
    data.append("sea_level_pressure_hpa", formData.sea_level_pressure_hpa);
    data.append("temperature_c", formData.temperature_c);
    data.append("visibility_km", formData.visibility_km);
    data.append("wind_speed_ms", formData.wind_speed_ms);

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
          date: result.date, 
        }, 
        ...prevHistory, 
      ]); 
    } catch (error) { 
      console.error("Error:", error); 
      alert("Could not connect to FastAPI"); 
    } 
  }; 

  // # update
 
  return ( 
    <div className="app"> 
 
      <div className="sun"></div> 
 
      <h1>Solar Power Prediction</h1> 
 
      <div className="container"> 
 
        {/* FORM */} 
        <div className="form-card"> 
 
          {/* <h2>Enter Solar Data</h2>  */}
 
          <form onSubmit={handleSubmit}> 
{/*  
            <label>Date & Time</label> 
            <input 
              type="datetime-local" 
              name="time" 
              value={formData.time} 
              onChange={handleChange} 
              required 
            /> 
 
            <label>Irradiance (W/m²)</label> 
            <input 
              type="number" 
              name="irradiance_wm2" 
              step="0.1" 
              value={formData.irradiance_wm2} 
              onChange={handleChange} 
              required 
            /> 
 
            <label>Rainfall (mm)</label> 
            <input 
              type="number" 
              name="rainfall_mm" 
              step="0.1" 
              value={formData.rainfall_mm} 
              onChange={handleChange} 
              required 
            /> 
 
            <label>Relative Humidity (%)</label> 
            <input 
              type="number" 
              name="relative_humidity_pct" 
              step="0.1" 
              min="0" 
              max="100" 
              value={formData.relative_humidity_pct} 
              onChange={handleChange} 
              required 
            /> 
 
            <label>Sea Level Pressure (hPa)</label> 
            <input 
              type="number" 
              name="sea_level_pressure_hpa" 
              step="0.1" 
              value={formData.sea_level_pressure_hpa} 
              onChange={handleChange} 
              required 
            /> 
 
            <label>Temperature (°C)</label> 
            <input 
              type="number" 
              name="temperature_c" 
              step="0.1" 
              value={formData.temperature_c} 
              onChange={handleChange} 
              required 
            /> 
 
            <label>Visibility (km)</label> 
            <input 
              type="number" 
              name="visibility_km" 
              step="0.1" 
              value={formData.visibility_km} 
              onChange={handleChange} 
              required 
            /> 
 
            <label>Wind Speed (m/s)</label> 
            <input 
              type="number" 
              name="wind_speed_ms" 
              step="0.1" 
              value={formData.wind_speed_ms} 
              onChange={handleChange} 
              required 
            />  */}
 
            <button type="submit"> 
              Random Forecast
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
 
               
 
                <p className="history-prediction"> 
                  <strong>Prediction:</strong>{" "} 
                  {item.prediction} kWh 
                </p> 
 
              </div> 
 
            )) 
 
          )} 
 
        </div> 

        <button
  type="button"
  className="export-button"
  onClick={() => {
    window.location.href = "http://127.0.0.1:8000/export";
  }}
>
  Export CSV
</button>
 
      </div> 
 
    </div> 
  ); 
} 
 
export default App; 