import json
import joblib
import numpy as np
import pandas as pd

from pathlib import Path
from sklearn.compose import ColumnTransformer
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler


# ---------------------------------------------------------
# Paths
# ---------------------------------------------------------

BASE_DIR = Path(__file__).resolve().parents[1]

DATA_PATH = BASE_DIR / "data" / "processed" / "final.csv"
FEATURE_DIR = BASE_DIR / "features"
ARTIFACT_DIR = FEATURE_DIR / "artifacts"

FEATURE_DIR.mkdir(parents=True, exist_ok=True)
ARTIFACT_DIR.mkdir(parents=True, exist_ok=True)


# ---------------------------------------------------------
# Load dataset
# ---------------------------------------------------------

def load_data(file_path):
    """Load the cleaned dataset."""
    return pd.read_csv(file_path)


# ---------------------------------------------------------
# Feature engineering
# ---------------------------------------------------------

def create_engineered_features(df):
    """
    Create meaningful numerical features from the
    existing customer attributes.
    """

    df = df.copy()

    # Polynomial features
    df["age_squared"] = df["age"] ** 2

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
    df["income_log"] = np.log1p(df["income"])

    df["monthly_spend_log"] = np.log1p(
        df["monthly_spend"]
    )

    # Ratio features
    df["spend_per_tenure"] = (
        df["monthly_spend"]
        / df["tenure_years"].replace(0, np.nan)
    )

    df["support_calls_per_tenure"] = (
        df["support_calls"]
        / df["tenure_years"].replace(0, np.nan)
    )

    df["login_per_contract"] = (
        df["login_frequency"]
        / df["contract_months"].replace(0, np.nan)
    )

    df["income_per_age"] = (
        df["income"]
        / df["age"].replace(0, np.nan)
    )

    df["spend_per_login"] = (
        df["monthly_spend"]
        / df["login_frequency"].replace(0, np.nan)
    )

    # Replace any division-by-zero results
    # with zero.
    df = df.replace(
        [np.inf, -np.inf],
        np.nan
    )

    df = df.fillna(0)

    return df


# ---------------------------------------------------------
# Main pipeline
# ---------------------------------------------------------

def build_feature_pipeline():

    # Load data
    df = load_data(DATA_PATH)

    print("Dataset loaded")
    print("Original shape:", df.shape)

    # Separate target
    y = df["churn"]

    # Remove target and identifier
    X = df.drop(
        columns=["churn", "customer_id"]
    )

    # Create engineered features
    X = create_engineered_features(X)

    print(
        "\nShape after feature engineering:",
        X.shape
    )

    # Identify feature types
    numerical_columns = X.select_dtypes(
        include=["int64", "float64"]
    ).columns.tolist()

    categorical_columns = X.select_dtypes(
        include=["object", "string"]
    ).columns.tolist()

    print("\nNumerical features:")
    print(numerical_columns)

    print("\nCategorical features:")
    print(categorical_columns)

    # Train/test split
    X_train, X_test, y_train, y_test = (
        train_test_split(
            X,
            y,
            test_size=0.20,
            random_state=42,
            stratify=y
        )
    )

    print("\nTrain shape:", X_train.shape)
    print("Test shape:", X_test.shape)

    # Numerical preprocessing
    numerical_pipeline = Pipeline(
        steps=[
            (
                "scaler",
                StandardScaler()
            )
        ]
    )

    # Categorical preprocessing
    categorical_pipeline = Pipeline(
        steps=[
            (
                "encoder",
                OneHotEncoder(
                    handle_unknown="ignore",
                    sparse_output=False
                )
            )
        ]
    )

    # Combine preprocessing
    preprocessor = ColumnTransformer(
        transformers=[
            (
                "numerical",
                numerical_pipeline,
                numerical_columns
            ),
            (
                "categorical",
                categorical_pipeline,
                categorical_columns
            )
        ]
    )

    # IMPORTANT:
    # Fit preprocessing only on training data.
    X_train_processed = preprocessor.fit_transform(
        X_train
    )

    X_test_processed = preprocessor.transform(
        X_test
    )

    # Retrieve generated feature names
    feature_names = (
        preprocessor.get_feature_names_out()
        .tolist()
    )

    print(
        "\nProcessed training shape:",
        X_train_processed.shape
    )

    print(
        "Processed testing shape:",
        X_test_processed.shape
    )

    print(
        "\nNumber of generated features:",
        len(feature_names)
    )

    # Save feature names
    feature_list_path = (
        FEATURE_DIR / "feature_list.json"
    )

    with open(
        feature_list_path,
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            feature_names,
            file,
            indent=4
        )

    # Save preprocessing pipeline
    pipeline_path = (
        ARTIFACT_DIR / "preprocessor.joblib"
    )

    joblib.dump(
        preprocessor,
        pipeline_path
    )

    # Save processed train/test data
    np.save(
        ARTIFACT_DIR / "X_train.npy",
        X_train_processed
    )

    np.save(
        ARTIFACT_DIR / "X_test.npy",
        X_test_processed
    )

    np.save(
        ARTIFACT_DIR / "y_train.npy",
        y_train.to_numpy()
    )

    np.save(
        ARTIFACT_DIR / "y_test.npy",
        y_test.to_numpy()
    )

    print("\nFeature pipeline completed.")

    print(
        "Feature list saved to:",
        feature_list_path
    )

    print(
        "Preprocessor saved to:",
        pipeline_path
    )

    return (
        X_train_processed,
        X_test_processed,
        y_train,
        y_test,
        feature_names
    )


# ---------------------------------------------------------
# Entry point
# ---------------------------------------------------------

if __name__ == "__main__":
    build_feature_pipeline()