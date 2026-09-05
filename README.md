# URJA-TEZHACK2026-ML08

## Reference

## About the dataset
A high-resolution three-year dataset supporting rooftop photovoltaics (PV) generation analytics

article link
https://www.nature.com/articles/s41597-025-04397-y#Sec8

database link
https://datadryad.org/dataset/doi:10.5061/dryad.m37pvmd99

### Objective
To forecast solar power generation with respect to weather parameters.

### Data Preprocessing

#### Stage-1
unzip the Dataset
and paste the 'Dataset; folder under '/data'

1. Fix typo in metadata
at file 'PV generation system metadata.ttl'
fix `brick:value 68.62 ] .` to `brick:value 68.62 ] ;` at line number 876

2. merge meterological data
3. merge pv generation data
#### Stage-2

1. Create site_id_ttl to filename mapping
2. add column 'ratedPowerKW' to pv-generation data

### Expected Output

### Running the Application

#### Backend (FastAPI)
- **Prerequisites**: Python 3.10+
- **Steps**:
  1. Open a terminal and navigate to the backend directory:
     ```bash
     cd Backend
     ```
  2. Activate the virtual environment (Windows):
     ```bash
     .\.venv\Scripts\activate
     ```
  3. Run the development server:
     ```bash
     uvicorn main:app --reload
     ```
  4. The backend API will be available at `http://localhost:8000`.

#### Frontend (React + Vite)
- **Prerequisites**: Node.js and npm
- **Steps**:
  1. Open a new terminal and navigate to the frontend directory:
     ```bash
     cd Frontend
     ```
  2. Install dependencies:
     ```bash
     npm install
     ```
  3. Start the development server:
     ```bash
     npm run dev
     ```
  4. The interface will be accessible at `http://localhost:5173`.
