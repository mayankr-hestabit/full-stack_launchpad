import json
import pickle
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import shap

from pathlib import Path


# ---------------------------------------------------------
# Paths
# ---------------------------------------------------------

BASE_DIR = Path(__file__).resolve().parents[1]

ARTIFACT_DIR = BASE_DIR / "features" / "artifacts"
FEATURE_DIR = BASE_DIR / "features"
MODEL_DIR = BASE_DIR / "models"
EVALUATION_DIR = BASE_DIR / "evaluation"

EVALUATION_DIR.mkdir(parents=True, exist_ok=True)


# ---------------------------------------------------------
# Load model, data and feature names
# ---------------------------------------------------------

def load_resources():

    # Load tuned Logistic Regression model
    with open(
        MODEL_DIR / "tuned_model.pkl",
        "rb"
    ) as file:
        model = pickle.load(file)

    # Load selected training and testing features
    X_train = np.load(
        ARTIFACT_DIR / "X_train_selected.npy"
    )

    X_test = np.load(
        ARTIFACT_DIR / "X_test_selected.npy"
    )

    # Load targets
    y_train = np.load(
        ARTIFACT_DIR / "y_train.npy"
    )

    y_test = np.load(
        ARTIFACT_DIR / "y_test.npy"
    )

    # Load final selected feature names
    with open(
        FEATURE_DIR / "selected_feature_list.json",
        "r",
        encoding="utf-8"
    ) as file:
        feature_names = json.load(file)

    return (
        model,
        X_train,
        X_test,
        y_train,
        y_test,
        feature_names
    )


# ---------------------------------------------------------
# Feature importance
# ---------------------------------------------------------

def generate_feature_importance(
    model,
    feature_names
):

    coefficients = model.coef_[0]

    importance_df = pd.DataFrame({
        "feature": feature_names,
        "coefficient": coefficients,
        "importance": np.abs(coefficients)
    })

    importance_df = importance_df.sort_values(
        "importance",
        ascending=True
    )

    plt.figure(figsize=(10, 7))

    plt.barh(
        importance_df["feature"],
        importance_df["importance"]
    )

    plt.xlabel(
        "Absolute Logistic Regression Coefficient"
    )

    plt.ylabel("Feature")

    plt.title(
        "Tuned Model Feature Importance"
    )

    plt.tight_layout()

    output_path = (
        EVALUATION_DIR /
        "feature_importance.png"
    )

    plt.savefig(
        output_path,
        dpi=300
    )

    plt.close()

    # Save values as CSV too
    importance_df.sort_values(
        "importance",
        ascending=False
    ).to_csv(
        EVALUATION_DIR /
        "feature_importance.csv",
        index=False
    )

    print(
        "Feature importance saved to:",
        output_path
    )


# ---------------------------------------------------------
# SHAP analysis
# ---------------------------------------------------------

def generate_shap_analysis(
    model,
    X_train,
    X_test,
    feature_names
):

    X_train_df = pd.DataFrame(
        X_train,
        columns=feature_names
    )

    X_test_df = pd.DataFrame(
        X_test,
        columns=feature_names
    )

    # LinearExplainer is suitable for
    # Logistic Regression
    explainer = shap.LinearExplainer(
        model,
        X_train_df
    )

    shap_values = explainer(
        X_test_df
    )

    # -----------------------------------------------------
    # SHAP summary plot
    # -----------------------------------------------------

    shap.summary_plot(
        shap_values.values,
        X_test_df,
        feature_names=feature_names,
        show=False
    )

    plt.tight_layout()

    output_path = (
        EVALUATION_DIR /
        "shap_summary.png"
    )

    plt.savefig(
        output_path,
        dpi=300,
        bbox_inches="tight"
    )

    plt.close()

    print(
        "SHAP summary plot saved to:",
        output_path
    )

    # -----------------------------------------------------
    # SHAP global importance
    # -----------------------------------------------------

    mean_abs_shap = np.abs(
        shap_values.values
    ).mean(axis=0)

    shap_importance_df = pd.DataFrame({
        "feature": feature_names,
        "mean_absolute_shap":
            mean_abs_shap
    })

    shap_importance_df = (
        shap_importance_df
        .sort_values(
            "mean_absolute_shap",
            ascending=False
        )
    )

    shap_importance_df.to_csv(
        EVALUATION_DIR /
        "shap_feature_importance.csv",
        index=False
    )


# ---------------------------------------------------------
# Error analysis heatmap
# ---------------------------------------------------------

def generate_error_analysis(
    model,
    X_test,
    y_test
):

    predictions = model.predict(
        X_test
    )

    probabilities = model.predict_proba(
        X_test
    )[:, 1]

    error_df = pd.DataFrame({
        "actual": y_test,
        "predicted": predictions,
        "probability": probabilities
    })

    # 1 if prediction is wrong
    error_df["error"] = (
        error_df["actual"]
        != error_df["predicted"]
    ).astype(int)

    # Group probabilities into ranges
    bins = [
        0.0,
        0.2,
        0.4,
        0.6,
        0.8,
        1.0
    ]

    labels = [
        "0.0-0.2",
        "0.2-0.4",
        "0.4-0.6",
        "0.6-0.8",
        "0.8-1.0"
    ]

    error_df["probability_range"] = pd.cut(
        error_df["probability"],
        bins=bins,
        labels=labels,
        include_lowest=True
    )

    # Calculate error rate for
    # each actual class and probability range
    heatmap_data = error_df.pivot_table(
        values="error",
        index="actual",
        columns="probability_range",
        observed=False,
        aggfunc="mean"
    )

    heatmap_data = (
        heatmap_data
        .reindex(
            index=[0, 1],
            columns=labels
        )
        .fillna(0)
    )

    plt.figure(figsize=(10, 5))

    image = plt.imshow(
        heatmap_data.values,
        aspect="auto"
    )

    plt.colorbar(
        image,
        label="Error Rate"
    )

    plt.xticks(
        range(len(labels)),
        labels
    )

    plt.yticks(
        [0, 1],
        [
            "Actual No Churn (0)",
            "Actual Churn (1)"
        ]
    )

    plt.xlabel(
        "Predicted Churn Probability"
    )

    plt.ylabel(
        "Actual Class"
    )

    plt.title(
        "Error Analysis Heatmap"
    )

    # Add values inside cells
    for row in range(
        heatmap_data.shape[0]
    ):
        for column in range(
            heatmap_data.shape[1]
        ):

            value = (
                heatmap_data.iloc[
                    row,
                    column
                ]
            )

            plt.text(
                column,
                row,
                f"{value:.2f}",
                ha="center",
                va="center"
            )

    plt.tight_layout()

    output_path = (
        EVALUATION_DIR /
        "error_analysis_heatmap.png"
    )

    plt.savefig(
        output_path,
        dpi=300
    )

    plt.close()

    print(
        "Error analysis heatmap saved to:",
        output_path
    )

    # -----------------------------------------------------
    # Save detailed prediction errors
    # -----------------------------------------------------

    error_df.to_csv(
        EVALUATION_DIR /
        "error_analysis.csv",
        index=False
    )

    # Print summary
    total_errors = int(
        error_df["error"].sum()
    )

    total_predictions = len(
        error_df
    )

    error_rate = (
        total_errors /
        total_predictions
    )

    false_positives = int(
        (
            (error_df["actual"] == 0)
            &
            (error_df["predicted"] == 1)
        ).sum()
    )

    false_negatives = int(
        (
            (error_df["actual"] == 1)
            &
            (error_df["predicted"] == 0)
        ).sum()
    )

    print(
        "\n========== ERROR ANALYSIS =========="
    )

    print(
        "Total predictions:",
        total_predictions
    )

    print(
        "Total errors:",
        total_errors
    )

    print(
        "Error rate:",
        round(
            error_rate,
            4
        )
    )

    print(
        "False positives:",
        false_positives
    )

    print(
        "False negatives:",
        false_negatives
    )


# ---------------------------------------------------------
# Main
# ---------------------------------------------------------

def main():

    print(
        "========== DAY 4 MODEL EXPLAINABILITY =========="
    )

    (
        model,
        X_train,
        X_test,
        y_train,
        y_test,
        feature_names
    ) = load_resources()

    print("\nResources loaded.")

    print(
        "Training shape:",
        X_train.shape
    )

    print(
        "Testing shape:",
        X_test.shape
    )

    print(
        "Selected features:",
        len(feature_names)
    )

    print(
        "\nGenerating feature importance..."
    )

    generate_feature_importance(
        model,
        feature_names
    )

    print(
        "\nGenerating SHAP analysis..."
    )

    generate_shap_analysis(
        model,
        X_train,
        X_test,
        feature_names
    )

    print(
        "\nGenerating error analysis..."
    )

    generate_error_analysis(
        model,
        X_test,
        y_test
    )

    print(
        "\nModel explainability analysis completed."
    )


if __name__ == "__main__":
    main()