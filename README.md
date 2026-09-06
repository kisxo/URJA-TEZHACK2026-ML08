# URJA-TEZHACK2026-ML08

## Introduction

This project focuses on forecasting solar power generation using advanced machine learning models, including XGBoost and Random Forest. Utilizing a dataset obtained from [https://datadryad.org/dataset/doi:10.5061/dryad.m37pvmd99], the project encompasses comprehensive steps such as data cleaning, preprocessing, feature engineering, exploratory data analysis (EDA), model building, hyperparameter tuning, and model evaluation.

## Reference

## About the dataset
A high-resolution three-year dataset supporting rooftop photovoltaics (PV) generation analytics

article link
https://www.nature.com/articles/s41597-025-04397-y#Sec8

database link
https://datadryad.org/dataset/doi:10.5061/dryad.m37pvmd99 

### Objective
To forecast solar power generation with respect to weather parameters.

## Data Collection and Preprocessing

### Dataset Acquisition
The dataset was sourced from Kaggle, containing historical data on weather features and solar power generation.

### Data Quality Assurance
* **Missing Values:** Handled missing values through imputation or removal to maintain data integrity.
* **Outlier Detection:** Identified and addressed outliers to prevent distortion of model training.
* **Data Splitting:** The dataset was split into training and testing sets to facilitate unbiased evaluation of model performance.
* **Feature Scaling:** Features were scaled using StandardScaler to enhance model stability and convergence during training.

### Data Preprocessing

#### Stage-1
unzip the Dataset
and paste the 'Dataset; folder under '/data'

1. Fix typo in metadata
at file 'PV generation system metadata.ttl'
fix `brick:value 68.62 ] .` to `brick:value 68.62 ] ;` at line number 876

2. merge meterological data
run `merge-meteorological-data.ipynb`

3. merge pv generation data
run `merge-pv-data.ipynb`

#### Stage-2
run `normolize-generation.ipynb`

1. Create site_id_ttl to filename mapping
2. add column 'ratedPowerKW' to pv-generation data

#### Stage-3
run `pretrain_preprocessing.ipynb`
1. fixed length output size
2. Split training and testing data
training < 2023
testing > 2022


## Exploratory Data Analysis (EDA)

* **Data Distribution Visualization:** Histograms were used to visualize and understand the distribution of each feature.
* **Correlation Analysis:** Investigated relationships between features and the target variable (SystemProduction) to identify key predictors.

## Model Development and Evaluation

### Model Selection
Various regression models were evaluated, including:
* Linear Regression
* Decision Tree Regressor
* Random Forest Regressor
* XGBoost

### Model Performance Metrics
Models were assessed using R-squared, Mean Squared Error (MSE), Root Mean Squared Error (RMSE), and Mean Absolute Error (MAE).

## Summary of Model Performance

| Model | R² | MSE | RMSE | MAE |
|---|---|---|---|---|
| Linear Regression | 0.553262 |   0.0013 | 0.0364 |0.0182 |
| Decision Tree |  0.622105 | 0.0011 | 0.0328 | 0.0178 |
| Random Forest | 0.732888 |   0.0008 |0.0276 | 0.0163 |
| XGBoost | 0.815073 | 0.0006 | 0.0252 | 0.0141 |

## Feature Importance Analysis

* **Key Features Identified:** Analyzed feature importance to gain insights into the model's decision-making process. Radiation, sunshine, and air temperature emerged as significant predictors of solar power generation.

### Poject Setup:s


- *Prerequisites*: Python 3.10+
- *Steps*:
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
  4. The backend API will be available at http://localhost:8000.

#### Frontend (React + Vite)
- *Prerequisites*: Node.js and npm
- *Steps*:
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
  4. The interface will be accessible at http://localhost:5173.
