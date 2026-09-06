# SOLAR POWER GENERATION FORECASTING
**Technical Project Documentation**
Team URJA • Team ID 0054 • Problem Statement ML08
TezHack 2026
Uday Subba
Raktim Rabha
Joydeep Roy
Anal Kashyap Bharali

## 1. Executive Summary
URJA is a machine-learning-based solar power generation forecasting system designed to estimate photovoltaic (PV) generation from historical generation, meteorological conditions, temporal information and site identity. The project uses the high-resolution three-year rooftop PV dataset published with the Nature Scientific Data paper and distributed through Dryad. The reference dataset contains measured PV generation from 60 grid-connected rooftop PV stations in Hong Kong over 2021–2023, with PV measurements at 5-minute intervals and meteorological measurements at 1-minute intervals.

The project pipeline consists of metadata repair, PV and meteorological data consolidation, site-capacity mapping, capacity-normalized generation, temporal feature engineering, fixed-length data preparation, chronological evaluation, regression-model comparison and application integration.

Four regression approaches are evaluated: Linear Regression, Decision Tree Regressor, Random Forest Regressor and XGBoost. The repository reports XGBoost as the strongest model, with R² = 0.815073, RMSE = 0.0252 and MAE = 0.0141, while Random Forest is the second-best reported model.

## 2. Project Overview

### 2.1 Objective
To forecast solar power generation with respect to weather parameters.

### 2.2 Core Idea
The central idea is to learn the relationship between environmental conditions, time-of-day/seasonal behavior, PV site characteristics and capacity-normalized generation. The trained model can then be exposed through a web application so that forecasts can be generated, visualized, retained and exported.

### 2.3 Intended Users
* Solar PV operators and rooftop-system managers.
* Energy planners and grid-support teams.
* PV performance analysts.
* Researchers and developers working with solar forecasting systems.

### 2.4 Project Components

| Layer | Current project component |
| :--- | :--- |
| **Data** | Nature/Dryad high-resolution rooftop PV dataset |
| **Preprocessing** | Three notebook stages for metadata, merging, normalization and preparation |
| **Models** | Linear Regression, Decision Tree, Random Forest, XGBoost |
| **Primary model** | XGBoost |
| **Backend** | FastAPI |
| **Frontend** | React + Vite |
| **Persistence** | SQLite / SQLAlchemy |
| **Output** | Forecast plot, prediction history, CSV export |

## 3. Problem Definition and Motivation

### 3.1 Problem
Solar generation is inherently variable because PV output changes with solar irradiance, cloud/weather conditions, temperature, seasonality and the operating characteristics of individual PV systems. This variability makes planning and balancing more difficult.

### 3.2 Why Forecasting Matters
* Reduce uncertainty in expected solar generation.
* Support operational planning around variable renewable generation.
* Provide an interpretable comparison between observed and predicted generation.
* Create a reusable forecasting workflow rather than a single offline model.

### 3.3 Forecasting Formulation
The latest XGBoost notebook explicitly defines a native 15-minute interval and four forecast steps, corresponding to a one-hour forecast horizon. The final report should retain the one-hour terminology only when the final training target is frozen consistently with that formulation.

## 4. Reference Dataset
The project uses one external scientific dataset reference: “A high-resolution three-year dataset supporting rooftop photovoltaics (PV) generation analytics,” published by Zinan Lin and collaborators and distributed through Dryad.

### 4.1 Dataset Scope

| Property | Reference dataset |
| :--- | :--- |
| **PV stations** | 60 grid-connected rooftop PV stations |
| **Location** | Hong Kong University of Science and Technology campus, Hong Kong |
| **Period** | 2021–2023 |
| **PV sampling** | 5-minute intervals |
| **Meteorological sampling** | 1-minute intervals |
| **Weather station** | 1 on-site weather station |
| **Metadata** | Brick schema represented in .ttl format |

Dryad states that the dataset contains measured PV power generation and on-site weather data from 60 rooftop PV stations over three years. It also states that the data can support PV generation forecasting and other PV analytics.

### 4.2 Project Sample Count
The project presentation currently reports a sample count of 4,345,976. This value should be treated as the project-reported sample count for the prepared dataset and should be frozen against the exact final CSV version before final submission.

### 4.3 External Reference Policy
Only the Nature scientific article and its corresponding Dryad dataset are treated as the project's external technical references. The ML models, preprocessing workflow and application are the team's own implementation.

## 5. Data Acquisition and Data Structure

### 5.1 Source Files
The original dataset contains PV generation files, meteorological data and Brick-schema metadata. The repository preprocessing notebooks organize these source materials into a machine-learning-ready structure.

### 5.2 Brick Metadata
Brick is used by the source dataset to represent building/PV-system metadata. During Stage 1, the repository explicitly repairs a syntax issue in “PV generation system metadata.ttl” before using the metadata.

### 5.3 PV Generation Data
PV generation is associated with individual sites. Site metadata provides rated power, which is later used to normalize generation so that systems of different capacities can be compared on a common scale.

### 5.4 Meteorological Variables

| Feature | Unit | Why relevant to PV generation |
| :--- | :--- | :--- |
| **Irradiance** | W/m² | Direct measure of incoming solar radiation and a primary driver of PV output. |
| **Rainfall** | mm | Indicates precipitation/weather conditions that can coincide with reduced solar availability. |
| **Relative humidity** | % | Captures atmospheric moisture and weather state. |
| **Sea-level pressure** | hPa | Provides broader atmospheric-state information. |
| **Temperature** | °C | PV output is influenced by operating temperature and temperature is correlated with weather conditions. |
| **Visibility** | km | Can provide information about atmospheric clarity/conditions. |
| **Wind speed** | m/s | Represents atmospheric conditions and can relate to temperature and weather changes. |

## 6. Data Preprocessing Pipeline

*Figure 1. Three-stage project data preparation pipeline.*

### 6.1 Stage 1 — Metadata and Data Consolidation
* Unzip the dataset and place the Dataset folder under `/data`.
* Repair the Brick metadata syntax issue specified in the README.
* Run `merge-meteorological-data.ipynb`.
* Run `merge-pv-data.ipynb`.

The objective is to convert the source collection into consolidated meteorological and PV-generation records that can be joined on time and site context.

### 6.2 Stage 2 — Capacity Mapping and Normalization
* Create the `site_id_ttl`-to-file mapping.
* Add `ratedPowerKW` to PV-generation records.
* Merge meteorological and PV generation data by timestamp.
* Normalize generation by rated PV capacity.

### 6.3 Generation Normalization
The project normalizes generation approximately as:
`normalized_generation = generation(kWh) / rated_power(kW)`

This removes much of the direct scale difference between a small and a large PV installation and gives the model a comparable generation target.

### 6.4 Stage 3 — Model-Ready Preparation
* Run `pretrain_preprocessing.ipynb`.
* Convert timestamps into temporal fields.
* Create fixed-length output/prepared records.
* Separate training and testing data using a year-based approach.

### 6.5 Time-Based Evaluation
The repository documentation describes training as records before 2023 and testing as records after 2022. The model notebook additionally uses a 2022 validation period and a 2023 test set for the current XGBoost experiment.

## 7. Feature Engineering and Feature Rationale

### 7.1 Final XGBoost Feature Set

| Feature group | Features |
| :--- | :--- |
| **Weather** | `irradiance_wm2`, `rainfall_mm`, `relative_humidity_pct`, `sea_level_pressure_hpa`, `temperature_c`, `visibility_km`, `wind_speed_ms` |
| **Cyclical time** | `hour_sin`, `hour_cos`, `month_sin`, `month_cos` |
| **Calendar** | `day` |
| **Site** | `site_id_ttl` |

### 7.2 Why Irradiance?
Irradiance is the strongest direct physical predictor in the current correlation analysis. The XGBoost notebook reports a correlation of approximately 0.948 with normalized generation in the inspected correlation matrix. It therefore provides the model with direct information about available solar energy.

### 7.3 Why Temperature?
Temperature captures the thermal operating environment of the PV system and also contains information about the broader weather state. The project README identifies air temperature among important predictors.

### 7.4 Why Humidity, Rainfall, Pressure, Visibility and Wind?
These variables complement irradiance by describing atmospheric and weather conditions. They may not individually determine generation, but together they help the model distinguish weather regimes associated with different solar-output conditions.

### 7.5 Why Time Features?
PV generation follows strong daily and seasonal patterns. Raw hour and month values have a discontinuity problem: for example, 23:00 and 00:00 are numerically far apart even though they are adjacent in time. The project therefore represents hour and month using sine/cosine cyclical encodings.

The encodings are:
* `hour_sin = sin(2π × hour / 24)`
* `hour_cos = cos(2π × hour / 24)`
* `month_sin = sin(2π × month / 12)`
* `month_cos = cos(2π × month / 12)`

### 7.6 Why Site ID?
Different PV sites can have different capacity, calibration and operating characteristics. The current XGBoost implementation explicitly treats `site_id_ttl` as a categorical feature so the model can distinguish site-specific behavior.

## 8. Exploratory Data Analysis
The repository README describes histogram-based distribution analysis and correlation analysis as part of EDA. The current XGBoost notebook contains a correlation matrix over temporal, weather and generation variables.

### 8.1 Correlation Findings

| Variable | Observed correlation with `normalized_generation` in current notebook |
| :--- | :--- |
| **Irradiance** | 0.948255 |
| **Relative humidity** | -0.479466 |
| **Temperature** | 0.420811 |
| **Visibility** | 0.202425 |
| **Sea-level pressure** | -0.088724 |
| **Rainfall** | -0.046598 |
| **Wind speed** | 0.034257 |

Correlation is descriptive rather than a complete feature-selection criterion. A tree-based model can exploit nonlinear effects and interactions that a simple pairwise correlation coefficient does not capture.

## 9. Machine Learning Models
The project evaluates multiple regression algorithms rather than selecting XGBoost without comparison. The model comparison is central to the selection of the final forecasting approach.

| Model | Purpose in the experiment | Strength |
| :--- | :--- | :--- |
| **Linear Regression** | Simple baseline | Interpretable and computationally inexpensive |
| **Decision Tree Regressor** | Nonlinear baseline | Captures threshold relationships |
| **Random Forest Regressor** | Ensemble model | Reduces variance through multiple trees |
| **XGBoost** | Boosted-tree model | Strong nonlinear/tabular learning capability |

### 9.1 Linear Regression
Linear Regression models the target as a weighted combination of input variables. Its role is to establish a straightforward baseline against which more flexible models can be measured.

### 9.2 Decision Tree Regressor
A Decision Tree learns threshold-based partitions of the feature space. It can model nonlinear relationships and interactions but is more sensitive to the particular training sample than an ensemble.

### 9.3 Random Forest Regressor
Random Forest combines many decision trees and aggregates their predictions. The project trains and evaluates it as the second major ensemble approach and reports it as the second-best model.

### 9.4 XGBoost
XGBoost is a gradient-boosted decision-tree algorithm. Instead of independently averaging trees, it builds trees sequentially so later trees can correct residual errors from earlier trees. This makes it well suited to structured tabular data containing nonlinear relationships and interactions.

## 10. Training and Evaluation Methodology

### 10.1 Dataset Split
The current XGBoost notebook loads `training_data.csv` and `test_data.csv`. A validation mask is applied within the training period, with the latest approximately three months of 2022 used for validation and 2023 retained for the final test evaluation.

### 10.2 Current XGBoost Experiment

| Set | Rows | Period |
| :--- | :--- | :--- |
| **Training** | 213,312 | Pre-validation training records |
| **Validation** | 2,184 | 2022 |
| **Test** | 19,084 | 2023 |

### 10.3 Forecast Horizon
The notebook defines a 15-minute native interval, four forecast steps and a one-hour forecast delta. The final target construction should remain synchronized with this definition when the project is frozen.

### 10.4 Evaluation Metrics

| Metric | Interpretation |
| :--- | :--- |
| **R²** | Proportion of target variance explained by the model relative to a constant baseline. |
| **MSE** | Mean squared error; strongly penalizes large errors. |
| **RMSE** | Square root of MSE; expresses error in the same scale as the target. |
| **MAE** | Mean absolute error; average absolute deviation of predictions from observations. |

## 11. Model Performance and Selection

*Figure 2. Reported R² comparison.*
*Figure 3. Reported RMSE comparison.*
*Figure 4. Reported MAE comparison.*

| Model | R² | MSE | RMSE | MAE |
| :--- | :--- | :--- | :--- | :--- |
| **Linear Regression** | 0.553262 | 0.0013 | 0.0364 | 0.0182 |
| **Decision Tree** | 0.622105 | 0.0011 | 0.0328 | 0.0178 |
| **Random Forest** | 0.732888 | 0.0008 | 0.0276 | 0.0163 |
| **XGBoost** | 0.815073 | 0.0006 | 0.0252 | 0.0141 |

### 11.1 Selection of XGBoost
XGBoost is selected because it has the highest reported R² and the lowest reported MSE, RMSE and MAE among the four compared models. The result provides an empirical basis for selecting XGBoost as the principal forecasting model.

### 11.2 Random Forest as the Secondary Model
Random Forest is the second-best reported model. The application therefore retains both XGBoost and Random Forest as selectable models, which also makes the application useful for model-to-model comparison.

## 12. XGBoost Configuration

| Parameter | Current value |
| :--- | :--- |
| `n_estimators` | 3000 |
| `learning_rate` | 0.02 |
| `max_depth` | 7 |
| `subsample` | 0.8 |
| `colsample_bytree` | 0.8 |
| `min_child_weight` | 1 |
| `early_stopping_rounds` | 150 |
| `enable_categorical` | True |
| `random_state` | 42 |

### 12.1 Early Stopping
The model is allowed up to 3000 boosting rounds, but early stopping prevents unnecessary continuation when validation performance stops improving. The current notebook reports best iteration 291.

### 12.2 Current Test Result

| Metric | Current XGBoost result |
| :--- | :--- |
| **Best iteration** | 291 |
| **RMSE** | 0.0252459483 |
| **MAE** | 0.0141268555 |
| **R²** | 0.8150735230 |

### 12.3 Model Persistence
The notebook saves an XGBoost-native model file and a Joblib serialized model. The repository also contains backend model artifacts and prediction code for application inference.

## 13. Application Architecture

*Figure 5. Current URJA application architecture.*

### 13.1 Frontend
The frontend is implemented with React and Vite. The current project provides controls for model selection and forecasting, displays generated prediction results, and exposes prediction history, CSV export and clear-history functionality.

### 13.2 Backend
FastAPI provides the application API. The repository contains `main.py`, `predict.py`, `graph.py` and `db.py`, together with prepared stage-3 data and model artifacts.

### 13.3 Database
SQLite/SQLAlchemy are used to persist prediction runs and row-level forecast information. This enables history to survive beyond a single frontend session.

## 14. Prediction Workflow
1. User opens the URJA web interface.
2. User selects a forecasting mode and model.
3. User specifies the requested forecast period.
4. Frontend sends the request to the FastAPI backend.
5. Backend validates the request and invokes the prediction engine.
6. Prediction engine loads the selected model and prepared data.
7. Model produces generation predictions.
8. The system generates a visualization comparing actual and predicted values where actual values are available.
9. The prediction run and associated forecast rows are stored in the database.
10. The frontend refreshes Prediction History.
11. Results can be exported to CSV or history can be cleared.

### 14.1 Forecast Visualization
The current prediction implementation generates a graph for the selected prediction window. The visualization is intended to make the forecast behavior inspectable rather than presenting only a single numerical value.

## 15. Prediction History and CSV Export

### 15.1 Prediction History — Implemented Feature
Prediction History is implemented as a persistent application feature. Prediction records are stored in the backend database and can be retrieved from the frontend rather than existing only as temporary browser state.

### 15.2 What is Stored

| Stored information | Purpose |
| :--- | :--- |
| **Prediction ID** | Unique identifier for each run |
| **Forecast mode** | Records the selected forecasting mode |
| **Number of days** | Requested prediction duration |
| **Plot date** | Date/window associated with the result |
| **Peak actual** | Peak observed value when available |
| **Peak predicted** | Peak forecast value |
| **Image path** | Generated visualization |
| **Creation time** | Timestamp of the prediction run |

### 15.3 Row-Level Forecast Information
Forecast rows retain the detailed time/site/weather information associated with a stored prediction, together with actual and predicted generation values where available.

### 15.4 CSV Export
The backend exposes CSV export functionality so prediction results can be downloaded and independently inspected. This supports the project's challenge requirement to make prediction outputs verifiable outside the application.

### 15.5 Clear History
A Clear History control is implemented to remove stored prediction history. The database relationship is designed so associated row-level records are removed with their parent prediction record.

*PPT-ready challenge-card statement:* Database-backed prediction history with CSV export and clear-history controls.

## 16. Low-Generation Indicator
The prediction visualization includes a low-generation reference threshold. In the current application implementation, a threshold of `normalized_generation = 0.01` is used as a visual indicator.
This should be described as a rule-based warning/indicator rather than a separately trained classification model.

## 17. Value Proposition
**PREDICT THE SUN. PLAN THE POWER!**
URJA combines a scientifically documented rooftop-PV dataset, structured preprocessing, comparative machine learning, model evaluation and a usable application layer.
* Forecast solar generation using weather and temporal information.
* Compare multiple regression models objectively.
* Use XGBoost as the strongest reported model.
* Visualize predicted versus observed generation.
* Retain prediction history for later inspection.
* Export prediction results as CSV.
* Provide a low-generation indicator.

## 18. Limitations and Current Development Status

### 18.1 Geographic Coverage
The reference dataset is collected from rooftop PV stations on the HKUST campus in Hong Kong. The source therefore provides rich site-specific data but does not by itself establish generalization to every climate or geography.

### 18.2 Extreme Weather
Rare or extreme weather conditions can be difficult for a model to learn when they are underrepresented in historical data.

### 18.3 Real-Time Weather
The current repository is based on prepared datasets and saved model artifacts. Continuous live weather ingestion and automatic online retraining are not yet documented as completed features.

### 18.4 Active Development
The GitHub repository is still changing. The documentation, README and final presentation should be synchronized with the final commit before submission.

## 19. Reproducibility and Project Setup

### 19.1 Software Stack

| Component | Technology |
| :--- | :--- |
| **Language** | Python 3.10+ |
| **ML** | scikit-learn, XGBoost |
| **Data processing** | pandas, NumPy |
| **Visualization** | Matplotlib |
| **Backend** | FastAPI |
| **Persistence** | SQLite / SQLAlchemy |
| **Frontend** | React + Vite |
| **Serialization** | Joblib / XGBoost model format |

### 19.2 Backend
1. Open a terminal and navigate to `Backend`.
2. Activate the project virtual environment.
3. Run: `uvicorn main:app --reload`
4. Backend is served at `localhost:8000`.

### 19.3 Frontend
1. Open a second terminal and navigate to `Frontend`.
2. Run `npm install` when required.
3. Run `npm run dev`.
4. Frontend is served at `localhost:5173`.

### 19.4 Reproducibility Record to Freeze
* Final Git commit hash.
* Exact final dataset/prepared-file version.
* Final sample count.
* Final train/validation/test row counts.
* Final feature list and feature order.
* Final model hyperparameters.
* Final MAE, RMSE, MSE and R².
* Final forecast horizon definition.

## 20. Conclusion
URJA presents an end-to-end approach to solar power generation forecasting using a high-resolution rooftop PV dataset. The project moves from scientific source data through metadata handling, PV/weather consolidation, capacity normalization, temporal feature engineering, model comparison and web application delivery.

The current reported model comparison shows a clear progression from Linear Regression and Decision Tree to the ensemble approaches, with XGBoost achieving the strongest reported performance (R² 0.815073, RMSE 0.0252459, MAE 0.0141269). Random Forest is the second-best reported model.

The application layer extends the ML work into a practical workflow by providing model selection, forecasting, visualization, database-backed Prediction History, CSV export and Clear History.

The remaining work is primarily finalization and synchronization: freeze the final dataset and experiment, verify the forecast-target construction, synchronize the README/PPT/documentation, and validate the complete frontend-to-model workflow.

## Appendix A. Feature Dictionary

| Feature | Description | Role |
| :--- | :--- | :--- |
| `irradiance_wm2` | Solar irradiance in W/m² | Weather input |
| `rainfall_mm` | Rainfall measurement in mm | Weather input |
| `relative_humidity_pct` | Relative humidity percentage | Weather input |
| `sea_level_pressure_hpa` | Sea-level atmospheric pressure | Weather input |
| `temperature_c` | Temperature in °C | Weather input |
| `visibility_km` | Visibility in km | Weather input |
| `wind_speed_ms` | Wind speed in m/s | Weather input |
| `hour_sin` / `hour_cos` | Cyclical representation of hour | Temporal input |
| `month_sin` / `month_cos` | Cyclical representation of month | Seasonal input |
| `day` | Day of month | Temporal input |
| `site_id_ttl` | PV station identifier | Categorical input |
| `normalized_generation` | Capacity-adjusted PV generation | Target |

## Appendix B. Metric Definitions
For actual values yᵢ, predictions ŷᵢ, mean actual value ȳ and n evaluated samples:
* **MAE**: MAE = (1/n) Σ \|yᵢ − ŷᵢ\|
* **MSE**: MSE = (1/n) Σ (yᵢ − ŷᵢ)²
* **RMSE**: RMSE = √MSE
* **R²**: R² = 1 − [Σ(yᵢ − ŷᵢ)² / Σ(yᵢ − ȳ)²]

Lower MAE/RMSE/MSE indicate smaller prediction errors. Higher R² indicates that the model explains more variance relative to a constant-mean baseline.

## References
1. Lin, Zinan; Zhou, Qi; Wang, Zhe; et al. (2024). A high-resolution three-year dataset supporting rooftop photovoltaics (PV) generation analytics [Dataset]. Dryad. https://doi.org/10.5061/dryad.m37pvmd99
2. URJA-TEZHACK2026-ML08 project repository. https://github.com/kisxo/URJA-TEZHACK2026-ML08
