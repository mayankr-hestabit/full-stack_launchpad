# DEPLOYMENT NOTES

## Week 6 --- Day 5: Model Deployment, Monitoring and MLOps Concepts

## 1. Objective

Day 5 converts the trained churn model into a production-style
machine-learning service.

The implementation covers:

-   FastAPI model serving
-   `POST /predict`
-   Input validation
-   Request ID tracking
-   Prediction logging
-   Versioned model loading
-   Reuse of the trained preprocessing pipeline
-   Data drift monitoring
-   Docker deployment preparation
-   Environment configuration

------------------------------------------------------------------------

## 2. Deployment Architecture

``` text
Client
  |
  v
POST /predict
  |
  v
FastAPI + Pydantic Validation
  |
  v
Raw Customer Features
  |
  v
Feature Engineering
  |
  v
preprocessor.joblib
  |
  v
33 Processed Features
  |
  v
15 Selected Features
  |
  v
tuned_model_v1.pkl
  |
  v
Prediction + Churn Probability
  |
  +---------------------+
  |                     |
  v                     v
API Response      prediction_logs.csv
                        |
                        v
                 drift_checker.py
```

## 3. FastAPI Application

The API is implemented in:

``` text
src/deployment/api.py
```

It can be started from the project root with:

``` bash
uvicorn src.deployment.api:app --reload
```

The application serves the model on port `8000`.

FastAPI also provides interactive Swagger documentation for testing the
endpoints.

## 4. Prediction Endpoint

The primary endpoint is:

``` text
POST /predict
```

Example request:

``` json
{
  "age": 45,
  "income": 55000,
  "tenure_years": 5,
  "monthly_spend": 70,
  "support_calls": 3,
  "satisfaction_score": 6,
  "login_frequency": 20,
  "contract_months": 12,
  "city": "Jaipur",
  "plan": "Premium",
  "payment_method": "UPI"
}
```

A successful test returned:

``` json
{
  "request_id": "833b8e58-e0bc-4a7a-aaf7-4dd6848a276",
  "prediction": 0,
  "churn_probability": 0.401657,
  "model_version": "v1"
}
```

Prediction meaning:

``` text
0 = predicted not to churn
1 = predicted to churn
```

The API therefore successfully performs end-to-end inference and returns
both the predicted class and churn probability.

## 5. Health Endpoint

A health endpoint is also available:

``` text
GET /health
```

It reports whether the API is running and which model version is
configured.

Example:

``` json
{
  "status": "healthy",
  "model_version": "v1"
}
```

## 6. Input Validation

Pydantic is used to validate incoming customer data before inference.

Validated fields include:

-   age
-   income
-   tenure_years
-   monthly_spend
-   support_calls
-   satisfaction_score
-   login_frequency
-   contract_months
-   city
-   plan
-   payment_method

Basic constraints prevent obviously invalid values, such as negative
income or an invalid age.

Invalid input is rejected before it reaches the model.

## 7. Production Feature Engineering

The model cannot directly consume the raw API request because training
included feature engineering.

The API recreates the same engineered features used during Day 2,
including:

``` text
age_squared
support_calls_squared
satisfaction_squared
login_frequency_squared
contract_months_squared
income_log
monthly_spend_log
spend_per_tenure
support_calls_per_tenure
login_per_contract
income_per_age
spend_per_login
```

This maintains consistency between model training and production
inference.

## 8. Saved Preprocessor and Feature Selection

The fitted preprocessing pipeline is loaded from:

``` text
src/features/artifacts/preprocessor.joblib
```

After preprocessing, the request is represented using the transformed
feature space.

The final selected feature names are loaded from:

``` text
src/features/selected_feature_list.json
```

The deployment pipeline keeps the same 15 features selected during Day 2
before sending the input to the tuned model.

``` text
Raw Input
   |
   v
Feature Engineering
   |
   v
Saved Preprocessor
   |
   v
33 Processed Features
   |
   v
15 Selected Features
   |
   v
Tuned Model
```

## 9. Model Loading and Versioning

The production model is stored as:

``` text
src/models/tuned_model_v1.pkl
```

The API reads the model version from:

``` text
MODEL_VERSION
```

The default is:

``` text
v1
```

The filename is constructed as:

``` text
tuned_model_<MODEL_VERSION>.pkl
```

Therefore:

``` text
MODEL_VERSION=v1 -> tuned_model_v1.pkl
MODEL_VERSION=v2 -> tuned_model_v2.pkl
MODEL_VERSION=v3 -> tuned_model_v3.pkl
```

Changing the environment variable selects which existing model file is
loaded.

Model versioning does not automatically generate `v2` or `v3`. A new
versioned file must be created when a new model is trained, evaluated
and approved.

## 10. Environment Configuration

The project contains:

``` text
.env.example
```

with:

``` env
MODEL_VERSION=v1
```

This documents the environment variable used by the deployment
application.

The API reads actual environment variables through `os.getenv()` and
falls back to `v1` if `MODEL_VERSION` is not supplied.

## 11. Request ID Tracking

Every prediction receives a unique UUID.

The request ID is:

-   Returned to the client
-   Written into the prediction log
-   Useful for tracing individual requests
-   Useful for debugging and auditing predictions

This makes each inference request identifiable.

## 12. Prediction Logging

Every successful prediction is appended to:

``` text
prediction_logs.csv
```

The log stores:

``` text
timestamp
request_id
model_version
age
income
tenure_years
monthly_spend
support_calls
satisfaction_score
login_frequency
contract_months
city
plan
payment_method
prediction
churn_probability
```

Prediction logging provides data for future monitoring, debugging and
auditing.

## 13. Data Drift

Data drift means that production input data begins to differ from the
data used to train the model.

Example:

``` text
Training Data        Production Data

Average age: 42      Average age: 25
Income: 55,000       Income: 120,000
Spend: 65            Spend: 150
```

Large distribution changes can reduce model reliability because the
model begins receiving data unlike the data it learned from.

## 14. Drift Checker

Drift monitoring is implemented in:

``` text
src/monitoring/drift_checker.py
```

It compares the reference dataset:

``` text
src/data/processed/final.csv
```

against production inputs stored in:

``` text
prediction_logs.csv
```

The script is executed using:

``` bash
python src/monitoring/drift_checker.py
```

It generates:

``` text
src/monitoring/drift_report.json
```

## 15. Numerical Drift

Numerical features are checked using Population Stability Index (PSI).

The project interprets PSI approximately as:

``` text
PSI < 0.10       -> no significant drift
PSI 0.10 - 0.25  -> moderate drift
PSI > 0.25       -> significant drift
```

The numerical features monitored are:

``` text
age
income
tenure_years
monthly_spend
support_calls
satisfaction_score
login_frequency
contract_months
```

## 16. Categorical Drift

Categorical drift is checked by comparing category proportions in the
reference and production datasets.

The monitored categorical features are:

``` text
city
plan
payment_method
```

The maximum absolute distribution difference is used as a simple drift
indicator.

## 17. Current Drift Test

The initial drift test used:

``` text
Reference samples: 1494
Production samples: 1
```

The checker reported significant drift, but it also correctly produced
the warning:

``` text
Only 1 production predictions available.
Drift results are not reliable yet.
```

The large drift values are not meaningful with only one production
observation.

The important result is that the drift-monitoring pipeline runs
successfully and generates `drift_report.json`.

Reliable drift interpretation requires a substantially larger production
sample.

## 18. Accuracy Decay

Accuracy decay means that a deployed model's predictive performance
decreases over time.

Unlike input data drift, true accuracy decay requires real production
outcomes.

For example:

``` text
Prediction -> customer will churn
Later      -> actual churn outcome becomes available
```

Once real outcomes are available, production predictions can be compared
with them and metrics such as accuracy, precision, recall and F1 can be
recalculated.

The current project logs predictions but does not yet have future
real-world churn labels, so actual production accuracy decay cannot
currently be measured.

## 19. Docker Deployment

The Dockerfile is located at:

``` text
src/deployment/Dockerfile
```

It uses:

``` text
python:3.12-slim
```

The container:

1.  Creates `/app` as the working directory.
2.  Copies `requirements.txt`.
3.  Installs project dependencies.
4.  Copies the project.
5.  Exposes port `8000`.
6.  Starts FastAPI using Uvicorn.

The container command is:

``` text
uvicorn src.deployment.api:app --host 0.0.0.0 --port 8000
```

## 20. Requirements

The project-level `requirements.txt` contains the main dependencies used
during Week 6:

``` text
pandas
numpy
matplotlib
scikit-learn
xgboost
joblib
shap
fastapi
uvicorn
pydantic
```

They can be installed using:

``` bash
pip install -r requirements.txt
```

## 21. MLOps Concepts Demonstrated

The capstone demonstrates several introductory MLOps practices:

-   Model serialization with pickle
-   Saved preprocessing with joblib
-   Model versioning
-   Environment-based configuration
-   Input validation
-   Request tracking
-   Prediction logging
-   Data drift monitoring
-   Containerization with Docker
-   Production-style API inference

## 22. Day 5 Project Files

``` text
week6-machine-learning/
|
|-- .env.example
|-- requirements.txt
|-- prediction_logs.csv
|-- DEPLOYMENT-NOTES.md
|
`-- src/
    |-- deployment/
    |   |-- api.py
    |   `-- Dockerfile
    |
    |-- monitoring/
    |   |-- drift_checker.py
    |   `-- drift_report.json
    |
    |-- models/
    |   `-- tuned_model_v1.pkl
    |
    `-- features/
        |-- selected_feature_list.json
        `-- artifacts/
            `-- preprocessor.joblib
```

## 23. Exercise Completion

The Day 5 capstone required the following:

  Requirement                   Status
  ----------------------------- -------------------------
  FastAPI/Flask model serving   Completed
  `POST /predict`               Completed
  Input validation              Completed
  Request ID tracking           Completed
  Prediction logging            Completed
  Versioned model loading       Completed
  Data drift monitoring         Completed
  Dockerfile                    Completed
  requirements.txt              Completed
  .env.example                  Completed
  Streamlit dashboard           Optional / not required

## 24. Required Deliverables

The required deliverables are:

``` text
/deployment/api.py
/deployment/Dockerfile
/monitoring/drift_checker.py
/prediction_logs.csv
DEPLOYMENT-NOTES.md
```

Additional supporting artifacts include:

``` text
requirements.txt
.env.example
src/monitoring/drift_report.json
src/models/tuned_model_v1.pkl
```

## 25. Complete Week 6 Workflow

``` text
DAY 1
Data Pipeline + EDA
        |
        v
Cleaned Dataset
        |
        v
DAY 2
Feature Engineering + Selection
        |
        v
Model-ready Features
        |
        v
DAY 3
Multi-model Training + 5-Fold CV
        |
        v
Best Model
        |
        v
DAY 4
Hyperparameter Tuning
        |
        +--> SHAP
        +--> Feature Importance
        `--> Error Analysis
        |
        v
Tuned Model
        |
        v
DAY 5
FastAPI Deployment
        |
        +--> Input Validation
        +--> Request ID Tracking
        +--> Model Versioning
        +--> Prediction Logging
        +--> Drift Monitoring
        `--> Docker Preparation
```

## 26. Final Conclusion

Day 5 converted the churn model into a production-style machine-learning
service.

FastAPI exposes the tuned model through `POST /predict`. Incoming
customer information is validated before being passed through the same
feature-engineering, preprocessing and feature-selection stages used
during training.

The versioned tuned model returns a churn prediction and probability.
Every prediction receives a unique request ID and is recorded in
`prediction_logs.csv`.

The drift checker compares production inputs against the reference
training dataset to identify changes in data distributions. Numerical
features are monitored using PSI, while categorical features are
monitored using category-distribution differences.

The project is also prepared for containerized deployment using Docker,
a requirements file and environment-based model configuration.

This completes the Week 6 Day 5 capstone and connects the complete ML
lifecycle from data preparation and model training to deployment and
monitoring.
