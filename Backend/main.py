from fastapi import FastAPI, Form
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime

app = FastAPI()

# Allow React frontend to communicate with FastAPI
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.post("/predict")
def predict(
    sunlight: float = Form(...),
    temperature: float = Form(...),
    cloud_cover: float = Form(...),
    season: str = Form(...),
    time: str = Form(...),
    date=datetime.now().date()
):

    print("Sunlight:", sunlight)
    print("Temperature:", temperature)
    print("Cloud Cover:", cloud_cover)
    print("Season:", season)
    print("Time:", time)
    print(date)

    # Temporary dummy prediction
    prediction = round(
        sunlight * 10
        + temperature * 0.5
        - cloud_cover * 0.1,
        2
    )

    return {
        "prediction": prediction,
        "date":str(date)
    }