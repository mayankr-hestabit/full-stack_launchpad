import json

import numpy as np
import pandas as pd

from pathlib import Path


# ---------------------------------------------------------
# Paths
# ---------------------------------------------------------

BASE_DIR = Path(__file__).resolve().parents[1]
PROJECT_ROOT = BASE_DIR.parent

REFERENCE_DATA_PATH = (
    BASE_DIR /
    "data" /
    "processed" /
    "final.csv"
)

PREDICTION_LOG_PATH = (
    PROJECT_ROOT /
    "prediction_logs.csv"
)

MONITORING_DIR = (
    BASE_DIR /
    "monitoring"
)

MONITORING_DIR.mkdir(
    parents=True,
    exist_ok=True
)

DRIFT_REPORT_PATH = (
    MONITORING_DIR /
    "drift_report.json"
)


# ---------------------------------------------------------
# Features
# ---------------------------------------------------------

NUMERICAL_FEATURES = [
    "age",
    "income",
    "tenure_years",
    "monthly_spend",
    "support_calls",
    "satisfaction_score",
    "login_frequency",
    "contract_months"
]


CATEGORICAL_FEATURES = [
    "city",
    "plan",
    "payment_method"
]


# ---------------------------------------------------------
# PSI
# ---------------------------------------------------------

def calculate_psi(
    reference,
    current,
    bins=10
):
    """
    Calculate Population Stability Index.

    PSI interpretation:
    < 0.10  -> little/no drift
    0.10-0.25 -> moderate drift
    > 0.25 -> significant drift
    """

    reference = pd.Series(
        reference
    ).dropna()

    current = pd.Series(
        current
    ).dropna()

    if (
        len(reference) == 0
        or len(current) == 0
    ):
        return None

    # Create bin boundaries
    boundaries = np.quantile(
        reference,
        np.linspace(
            0,
            1,
            bins + 1
        )
    )

    # Avoid duplicate boundaries
    boundaries = np.unique(
        boundaries
    )

    if len(boundaries) < 2:
        return 0.0

    reference_counts, _ = (
        np.histogram(
            reference,
            bins=boundaries
        )
    )

    current_counts, _ = (
        np.histogram(
            current,
            bins=boundaries
        )
    )

    reference_percent = (
        reference_counts
        / max(
            reference_counts.sum(),
            1
        )
    )

    current_percent = (
        current_counts
        / max(
            current_counts.sum(),
            1
        )
    )

    # Avoid division by zero
    epsilon = 0.0001

    reference_percent = (
        np.where(
            reference_percent == 0,
            epsilon,
            reference_percent
        )
    )

    current_percent = (
        np.where(
            current_percent == 0,
            epsilon,
            current_percent
        )
    )

    psi = np.sum(
        (
            current_percent
            - reference_percent
        )
        *
        np.log(
            current_percent
            / reference_percent
        )
    )

    return float(psi)


# ---------------------------------------------------------
# PSI interpretation
# ---------------------------------------------------------

def interpret_psi(psi):

    if psi is None:
        return "insufficient_data"

    if psi < 0.10:
        return "no_significant_drift"

    elif psi < 0.25:
        return "moderate_drift"

    else:
        return "significant_drift"


# ---------------------------------------------------------
# Categorical drift
# ---------------------------------------------------------

def categorical_drift(
    reference,
    current
):
    """
    Compare category proportions between
    reference and production data.

    Returns maximum absolute percentage
    difference across categories.
    """

    reference_dist = (
        reference.value_counts(
            normalize=True
        )
    )

    current_dist = (
        current.value_counts(
            normalize=True
        )
    )

    categories = set(
        reference_dist.index
    ).union(
        current_dist.index
    )

    differences = {}

    for category in categories:

        reference_value = float(
            reference_dist.get(
                category,
                0
            )
        )

        current_value = float(
            current_dist.get(
                category,
                0
            )
        )

        difference = abs(
            reference_value
            - current_value
        )

        differences[
            str(category)
        ] = difference

    max_difference = (
        max(
            differences.values()
        )
        if differences
        else 0
    )

    return (
        float(max_difference),
        differences
    )


# ---------------------------------------------------------
# Interpret categorical drift
# ---------------------------------------------------------

def interpret_categorical_drift(
    max_difference
):

    if max_difference < 0.10:
        return "no_significant_drift"

    elif max_difference < 0.20:
        return "moderate_drift"

    else:
        return "significant_drift"


# ---------------------------------------------------------
# Main drift check
# ---------------------------------------------------------

def check_drift():

    print(
        "========== DATA DRIFT CHECK =========="
    )

    # Load reference training data
    reference_df = pd.read_csv(
        REFERENCE_DATA_PATH
    )

    print(
        "\nReference data loaded:",
        reference_df.shape
    )

    # Check prediction logs
    if not PREDICTION_LOG_PATH.exists():

        print(
            "\nPrediction log file not found."
        )

        print(
            "Generate predictions through "
            "/predict first."
        )

        return

    production_df = pd.read_csv(
        PREDICTION_LOG_PATH
    )

    print(
        "Production data loaded:",
        production_df.shape
    )

    # Very small production samples are
    # unreliable for drift monitoring.
    if len(production_df) < 10:

        print(
            "\nWARNING:"
        )

        print(
            "Only",
            len(production_df),
            "production predictions available."
        )

        print(
            "Drift results are not reliable yet."
        )

    drift_report = {
        "reference_samples":
            int(
                len(reference_df)
            ),

        "production_samples":
            int(
                len(production_df)
            ),

        "numerical_features": {},

        "categorical_features": {}
    }

    # -----------------------------------------------------
    # Numerical drift
    # -----------------------------------------------------

    print(
        "\n========== NUMERICAL DRIFT =========="
    )

    for feature in NUMERICAL_FEATURES:

        if feature not in production_df.columns:
            continue

        psi = calculate_psi(
            reference_df[feature],
            production_df[feature]
        )

        status = interpret_psi(
            psi
        )

        drift_report[
            "numerical_features"
        ][feature] = {
            "psi":
                None
                if psi is None
                else round(
                    psi,
                    6
                ),

            "status":
                status
        }

        print(
            f"{feature}: "
            f"PSI={psi:.4f} "
            f"→ {status}"
            if psi is not None
            else
            f"{feature}: insufficient data"
        )

    # -----------------------------------------------------
    # Categorical drift
    # -----------------------------------------------------

    print(
        "\n========== CATEGORICAL DRIFT =========="
    )

    for feature in CATEGORICAL_FEATURES:

        if feature not in production_df.columns:
            continue

        (
            max_difference,
            category_differences
        ) = categorical_drift(
            reference_df[feature],
            production_df[feature]
        )

        status = (
            interpret_categorical_drift(
                max_difference
            )
        )

        drift_report[
            "categorical_features"
        ][feature] = {

            "max_distribution_difference":
                round(
                    max_difference,
                    6
                ),

            "status":
                status,

            "category_differences": {
                category:
                    round(
                        difference,
                        6
                    )

                for (
                    category,
                    difference
                )
                in category_differences.items()
            }
        }

        print(
            f"{feature}: "
            f"max difference="
            f"{max_difference:.4f} "
            f"→ {status}"
        )

    # -----------------------------------------------------
    # Overall drift status
    # -----------------------------------------------------

    statuses = []

    for result in (
        drift_report[
            "numerical_features"
        ].values()
    ):
        statuses.append(
            result["status"]
        )

    for result in (
        drift_report[
            "categorical_features"
        ].values()
    ):
        statuses.append(
            result["status"]
        )

    if (
        "significant_drift"
        in statuses
    ):
        overall_status = (
            "significant_drift"
        )

    elif (
        "moderate_drift"
        in statuses
    ):
        overall_status = (
            "moderate_drift"
        )

    else:
        overall_status = (
            "no_significant_drift"
        )

    drift_report[
        "overall_status"
    ] = overall_status

    # -----------------------------------------------------
    # Save report
    # -----------------------------------------------------

    with open(
        DRIFT_REPORT_PATH,
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            drift_report,
            file,
            indent=4
        )

    print(
        "\n========== OVERALL STATUS =========="
    )

    print(
        overall_status
    )

    print(
        "\nDrift report saved to:",
        DRIFT_REPORT_PATH
    )


# ---------------------------------------------------------
# Entry point
# ---------------------------------------------------------

if __name__ == "__main__":
    check_drift()