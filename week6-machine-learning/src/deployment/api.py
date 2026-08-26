import csv
import json
import os
import pickle
import uuid

from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pandas as pd

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field


# ---------------------------------------------------------
# Paths
# ---------------------------------------------------------

BASE_DIR = Path(__file__).resolve().parents[1]
PROJECT_ROOT = BASE_DIR.parent

FEATURE_DIR = BASE_DIR / "features"
ARTIFACT_DIR = FEATURE_DIR / "artifacts"
MODEL_DIR = BASE_DIR / "models"

PREDICTION_LOG_PATH = (
    PROJECT_ROOT / "prediction_logs.csv"
)


# ---------------------------------------------------------
# Model version
# ---------------------------------------------------------

MODEL_VERSION = os.getenv(
    "MODEL_VERSION",
    "v1"
)

MODEL_PATH = (
    MODEL_DIR /
    f"tuned_model_{MODEL_VERSION}.pkl"
)


# ---------------------------------------------------------
# FastAPI application
# ---------------------------------------------------------

app = FastAPI(
    title="Customer Churn Prediction API",
    description=(
        "Week 6 Day 5 ML deployment API "
        "for customer churn prediction."
    ),
    version="1.0.0"
)


# ---------------------------------------------------------
# Input validation schema
# ---------------------------------------------------------

class CustomerInput(BaseModel):

    age: float = Field(
        gt=0,
        le=120
    )

    income: float = Field(
        ge=0
    )

    tenure_years: float = Field(
        ge=0
    )

    monthly_spend: float = Field(
        ge=0
    )

    support_calls: float = Field(
        ge=0
    )

    satisfaction_score: float = Field(
        ge=0
    )

    login_frequency: float = Field(
        ge=0
    )

    contract_months: float = Field(
        ge=0
    )

    city: str = Field(
        min_length=1
    )

    plan: str = Field(
        min_length=1
    )

    payment_method: str = Field(
        min_length=1
    )


# ---------------------------------------------------------
# Response schema
# ---------------------------------------------------------

class PredictionResponse(BaseModel):

    request_id: str

    prediction: int

    churn_probability: float

    model_version: str


# ---------------------------------------------------------
# Load model and preprocessing artifacts
# ---------------------------------------------------------

def load_resources():

    if not MODEL_PATH.exists():
        raise FileNotFoundError(
            f"Model not found: {MODEL_PATH}"
        )

    # Load tuned model
    with open(
        MODEL_PATH,
        "rb"
    ) as file:
        model = pickle.load(file)

    # Load preprocessing pipeline
    preprocessor_path = (
        ARTIFACT_DIR /
        "preprocessor.joblib"
    )

    import joblib

    preprocessor = joblib.load(
        preprocessor_path
    )

    # Load selected feature names
    selected_feature_path = (
        FEATURE_DIR /
        "selected_feature_list.json"
    )

    with open(
        selected_feature_path,
        "r",
        encoding="utf-8"
    ) as file:

        selected_features = json.load(
            file
        )

    return (
        model,
        preprocessor,
        selected_features
    )


# ---------------------------------------------------------
# Load once when API starts
# ---------------------------------------------------------

model, preprocessor, selected_features = (
    load_resources()
)


# ---------------------------------------------------------
# Feature engineering
# ---------------------------------------------------------

def create_engineered_features(df):

    df = df.copy()

    # Polynomial features
    df["age_squared"] = (
        df["age"] ** 2
    )

    df["support_calls_squared"] = (
        df["support_calls"] ** 2
    )

    df["satisfaction_squared"] = (
        df["satisfaction_score"] ** 2
    )

    df["login_frequency_squared"] = (
        df["login_frequency"] ** 2
    )

    df["contract_months_squared"] = (
        df["contract_months"] ** 2
    )

    # Log transformations
    df["income_log"] = np.log1p(
        df["income"]
    )

    df["monthly_spend_log"] = np.log1p(
        df["monthly_spend"]
    )

    # Ratio features
    df["spend_per_tenure"] = (
        df["monthly_spend"]
        /
        df["tenure_years"].replace(
            0,
            np.nan
        )
    )

    df["support_calls_per_tenure"] = (
        df["support_calls"]
        /
        df["tenure_years"].replace(
            0,
            np.nan
        )
    )

    df["login_per_contract"] = (
        df["login_frequency"]
        /
        df["contract_months"].replace(
            0,
            np.nan
        )
    )

    df["income_per_age"] = (
        df["income"]
        /
        df["age"].replace(
            0,
            np.nan
        )
    )

    df["spend_per_login"] = (
        df["monthly_spend"]
        /
        df["login_frequency"].replace(
            0,
            np.nan
        )
    )

    # Handle invalid division results
    df = df.replace(
        [np.inf, -np.inf],
        np.nan
    )

    df = df.fillna(0)

    return df


# ---------------------------------------------------------
# Prepare model input
# ---------------------------------------------------------

def prepare_features(customer):

    # Convert validated request to dictionary
    customer_dict = (
        customer.model_dump()
    )

    # Convert one customer into a DataFrame
    df = pd.DataFrame(
        [customer_dict]
    )

    # Create same engineered features
    # used during Day 2 training
    df = create_engineered_features(df)

    # Apply fitted preprocessing pipeline
    processed_features = (
        preprocessor.transform(df)
    )

    # Names of all 33 processed features
    all_feature_names = (
        preprocessor
        .get_feature_names_out()
        .tolist()
    )

    # Find positions of the 15
    # features selected during Day 2
    selected_indices = [
        all_feature_names.index(feature)
        for feature
        in selected_features
    ]

    # Keep only final selected features
    final_features = (
        processed_features[
            :,
            selected_indices
        ]
    )

    return final_features


# ---------------------------------------------------------
# Prediction logging
# ---------------------------------------------------------

def log_prediction(
    request_id,
    customer,
    prediction,
    probability
):

    file_exists = (
        PREDICTION_LOG_PATH.exists()
    )

    with open(
        PREDICTION_LOG_PATH,
        "a",
        newline="",
        encoding="utf-8"
    ) as file:

        writer = csv.writer(file)

        if not file_exists:

            writer.writerow([
                "timestamp",
                "request_id",
                "model_version",
                "age",
                "income",
                "tenure_years",
                "monthly_spend",
                "support_calls",
                "satisfaction_score",
                "login_frequency",
                "contract_months",
                "city",
                "plan",
                "payment_method",
                "prediction",
                "churn_probability"
            ])

        writer.writerow([
            datetime.now(
                timezone.utc
            ).isoformat(),

            request_id,

            MODEL_VERSION,

            customer.age,
            customer.income,
            customer.tenure_years,
            customer.monthly_spend,
            customer.support_calls,
            customer.satisfaction_score,
            customer.login_frequency,
            customer.contract_months,
            customer.city,
            customer.plan,
            customer.payment_method,
            prediction,
            probability
        ])


# ---------------------------------------------------------
# Health endpoint
# ---------------------------------------------------------

@app.get("/health")
def health():

    return {
        "status": "healthy",
        "model_version": MODEL_VERSION
    }


# ---------------------------------------------------------
# Prediction endpoint
# ---------------------------------------------------------

@app.post(
    "/predict",
    response_model=PredictionResponse
)
def predict(customer: CustomerInput):

    # Generate unique request ID
    request_id = str(
        uuid.uuid4()
    )

    try:

        # Prepare 15 model-ready features
        final_features = (
            prepare_features(customer)
        )

        # Generate prediction
        prediction = int(
            model.predict(
                final_features
            )[0]
        )

        # Generate churn probability
        probability = float(
            model.predict_proba(
                final_features
            )[0][1]
        )

        # Save request and prediction
        log_prediction(
            request_id,
            customer,
            prediction,
            probability
        )

        return PredictionResponse(
            request_id=request_id,
            prediction=prediction,
            churn_probability=round(
                probability,
                6
            ),
            model_version=MODEL_VERSION
        )

    except Exception as error:

        raise HTTPException(
            status_code=500,
            detail=str(error)
        )

'''
POST /predict
      ↓
Pydantic validation
      ↓
Raw customer fields
      ↓
12 engineered features
      ↓
preprocessor.joblib
      ↓
33 processed features
      ↓
selected_feature_list.json
      ↓
15 selected features
      ↓
tuned_model_v1.pkl
      ↓
prediction + probability
      ↓
prediction_logs.csv
'''