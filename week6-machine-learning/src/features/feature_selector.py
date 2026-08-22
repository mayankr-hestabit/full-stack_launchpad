import json
import joblib
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from pathlib import Path

from sklearn.feature_selection import (
    mutual_info_classif,
    RFE
)
from sklearn.linear_model import LogisticRegression


# ---------------------------------------------------------
# Paths
# ---------------------------------------------------------

BASE_DIR = Path(__file__).resolve().parents[1]

FEATURE_DIR = BASE_DIR / "features"
ARTIFACT_DIR = FEATURE_DIR / "artifacts"

FEATURE_LIST_PATH = FEATURE_DIR / "feature_list.json"


# ---------------------------------------------------------
# Load processed feature data
# ---------------------------------------------------------

def load_feature_data():
    """Load processed train/test arrays and feature names."""

    X_train = np.load(
        ARTIFACT_DIR / "X_train.npy"
    )

    X_test = np.load(
        ARTIFACT_DIR / "X_test.npy"
    )

    y_train = np.load(
        ARTIFACT_DIR / "y_train.npy"
    )

    y_test = np.load(
        ARTIFACT_DIR / "y_test.npy"
    )

    with open(
        FEATURE_LIST_PATH,
        "r",
        encoding="utf-8"
    ) as file:
        feature_names = json.load(file)

    return (
        X_train,
        X_test,
        y_train,
        y_test,
        feature_names
    )


# ---------------------------------------------------------
# Correlation threshold
# ---------------------------------------------------------

def correlation_selection(
    X_train,
    feature_names,
    threshold=0.95
):
    """
    Remove highly correlated features.

    Correlation is calculated using the training data only.
    """

    df = pd.DataFrame(
        X_train,
        columns=feature_names
    )

    correlation_matrix = df.corr().abs()

    upper_triangle = correlation_matrix.where(
        np.triu(
            np.ones(
                correlation_matrix.shape
            ),
            k=1
        ).astype(bool)
    )

    features_to_drop = [
        column
        for column in upper_triangle.columns
        if any(
            upper_triangle[column] > threshold
        )
    ]

    selected_features = [
        feature
        for feature in feature_names
        if feature not in features_to_drop
    ]

    return (
        selected_features,
        features_to_drop
    )


# ---------------------------------------------------------
# Mutual Information
# ---------------------------------------------------------

def mutual_information_selection(
    X_train,
    y_train,
    feature_names,
    top_k=20
):
    """
    Select the top features according to
    mutual information with the target.
    """

    mi_scores = mutual_info_classif(
        X_train,
        y_train,
        random_state=42
    )

    mi_df = pd.DataFrame({
        "feature": feature_names,
        "mutual_information": mi_scores
    })

    mi_df = mi_df.sort_values(
        by="mutual_information",
        ascending=False
    ).reset_index(drop=True)

    selected_features = (
        mi_df.head(top_k)["feature"]
        .tolist()
    )

    return (
        selected_features,
        mi_df
    )


# ---------------------------------------------------------
# RFE
# ---------------------------------------------------------

def rfe_selection(
    X_train,
    y_train,
    feature_names,
    n_features=15
):
    """
    Select features using Recursive Feature Elimination.
    """

    estimator = LogisticRegression(
        max_iter=2000,
        random_state=42
    )

    selector = RFE(
        estimator=estimator,
        n_features_to_select=n_features,
        step=1
    )

    selector.fit(
        X_train,
        y_train
    )

    selected_features = [
        feature_names[index]
        for index, selected
        in enumerate(selector.support_)
        if selected
    ]

    ranking_df = pd.DataFrame({
        "feature": feature_names,
        "rfe_rank": selector.ranking_,
        "selected": selector.support_
    }).sort_values(
        by="rfe_rank"
    )

    return (
        selected_features,
        ranking_df,
        selector
    )


# ---------------------------------------------------------
# Feature importance
# ---------------------------------------------------------

def plot_feature_importance(
    ranking_df,
    output_path,
    top_n=15
):
    """
    Plot RFE feature ranking.
    Lower RFE rank means greater importance.
    """

    selected = (
        ranking_df[
            ranking_df["selected"]
        ]
        .sort_values(
            by="rfe_rank"
        )
        .head(top_n)
        .sort_values(
            by="rfe_rank",
            ascending=True
        )
    )

    plt.figure(figsize=(10, 7))

    plt.barh(
        selected["feature"],
        selected["rfe_rank"]
    )

    plt.xlabel("RFE Rank")
    plt.ylabel("Feature")
    plt.title(
        "Selected Feature Importance — RFE"
    )

    plt.tight_layout()
    plt.savefig(output_path)
    plt.close()


# ---------------------------------------------------------
# Main feature-selection pipeline
# ---------------------------------------------------------

def run_feature_selection():

    (
        X_train,
        X_test,
        y_train,
        y_test,
        feature_names
    ) = load_feature_data()

    print("Feature selection started.")

    print(
        "Training feature shape:",
        X_train.shape
    )

    print(
        "Testing feature shape:",
        X_test.shape
    )

    # -----------------------------------------------------
    # 1. Correlation threshold
    # -----------------------------------------------------

    (
        correlation_features,
        dropped_features
    ) = correlation_selection(
        X_train,
        feature_names,
        threshold=0.95
    )

    print(
        "\n========== CORRELATION SELECTION =========="
    )

    print(
        "Features before:",
        len(feature_names)
    )

    print(
        "Highly correlated features removed:",
        len(dropped_features)
    )

    print(
        "Features remaining:",
        len(correlation_features)
    )

    if dropped_features:
        print("\nDropped features:")
        for feature in dropped_features:
            print("-", feature)

    # Create data after correlation selection
    correlation_indices = [
        feature_names.index(feature)
        for feature in correlation_features
    ]

    X_train_corr = X_train[
        :, correlation_indices
    ]

    X_test_corr = X_test[
        :, correlation_indices
    ]

    # -----------------------------------------------------
    # 2. Mutual Information
    # -----------------------------------------------------

    (
        mi_features,
        mi_scores
    ) = mutual_information_selection(
        X_train_corr,
        y_train,
        correlation_features,
        top_k=min(
            20,
            len(correlation_features)
        )
    )

    print(
        "\n========== MUTUAL INFORMATION =========="
    )

    print(
        mi_scores.to_string(index=False)
    )

    print(
        "\nFeatures selected by MI:",
        len(mi_features)
    )

    # Keep only MI-selected columns
    mi_indices = [
        correlation_features.index(feature)
        for feature in mi_features
    ]

    X_train_mi = X_train_corr[
        :, mi_indices
    ]

    X_test_mi = X_test_corr[
        :, mi_indices
    ]

    # -----------------------------------------------------
    # 3. RFE
    # -----------------------------------------------------

    rfe_count = min(
        15,
        X_train_mi.shape[1]
    )

    (
        rfe_features,
        rfe_ranking,
        rfe_selector
    ) = rfe_selection(
        X_train_mi,
        y_train,
        mi_features,
        n_features=rfe_count
    )

    print(
        "\n========== RFE =========="
    )

    print(
        "Features selected by RFE:",
        len(rfe_features)
    )

    for feature in rfe_features:
        print("-", feature)

    # Final selected indices
    final_indices = [
        mi_features.index(feature)
        for feature in rfe_features
    ]

    X_train_selected = X_train_mi[
        :, final_indices
    ]

    X_test_selected = X_test_mi[
        :, final_indices
    ]

    # -----------------------------------------------------
    # Save final selected features
    # -----------------------------------------------------

    selected_feature_path = (
        FEATURE_DIR /
        "selected_feature_list.json"
    )

    with open(
        selected_feature_path,
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            rfe_features,
            file,
            indent=4
        )

    # Save selected train/test arrays
    np.save(
        ARTIFACT_DIR /
        "X_train_selected.npy",
        X_train_selected
    )

    np.save(
        ARTIFACT_DIR /
        "X_test_selected.npy",
        X_test_selected
    )

    # Save ranking information
    rfe_ranking.to_csv(
        ARTIFACT_DIR /
        "rfe_ranking.csv",
        index=False
    )

    # -----------------------------------------------------
    # Feature importance plot
    # -----------------------------------------------------

    plot_feature_importance(
        rfe_ranking,
        FEATURE_DIR /
        "feature_importance.png"
    )

    # -----------------------------------------------------
    # Final summary
    # -----------------------------------------------------

    print(
        "\n========== FINAL FEATURE SELECTION =========="
    )

    print(
        "Original features:",
        len(feature_names)
    )

    print(
        "After correlation:",
        len(correlation_features)
    )

    print(
        "After mutual information:",
        len(mi_features)
    )

    print(
        "Final selected features:",
        len(rfe_features)
    )

    print(
        "\nFinal training shape:",
        X_train_selected.shape
    )

    print(
        "Final testing shape:",
        X_test_selected.shape
    )

    print(
        "\nSelected features:"
    )

    for feature in rfe_features:
        print("-", feature)

    print(
        "\nFeature selection completed."
    )


# ---------------------------------------------------------
# Entry point
# ---------------------------------------------------------

if __name__ == "__main__":
    run_feature_selection()