import json
import pickle
import numpy as np

from pathlib import Path

from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import (
    GridSearchCV,
    StratifiedKFold
)
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    roc_auc_score
)


# ---------------------------------------------------------
# Paths
# ---------------------------------------------------------

BASE_DIR = Path(__file__).resolve().parents[1]

ARTIFACT_DIR = BASE_DIR / "features" / "artifacts"
MODEL_DIR = BASE_DIR / "models"
TUNING_DIR = BASE_DIR / "tuning"

MODEL_DIR.mkdir(parents=True, exist_ok=True)
TUNING_DIR.mkdir(parents=True, exist_ok=True)


# ---------------------------------------------------------
# Day 3 baseline
# ---------------------------------------------------------

BASELINE_CV_ROC_AUC = 0.7435822510822511

BASELINE_TEST_METRICS = {
    "accuracy": 0.7692307692307693,
    "precision": 0.6923076923076923,
    "recall": 0.22784810126582278,
    "f1": 0.34285714285714286,
    "roc_auc": 0.7643843498273878
}


# ---------------------------------------------------------
# Load Day 2 selected data
# ---------------------------------------------------------

def load_data():

    X_train = np.load(
        ARTIFACT_DIR / "X_train_selected.npy"
    )

    X_test = np.load(
        ARTIFACT_DIR / "X_test_selected.npy"
    )

    y_train = np.load(
        ARTIFACT_DIR / "y_train.npy"
    )

    y_test = np.load(
        ARTIFACT_DIR / "y_test.npy"
    )

    return X_train, X_test, y_train, y_test


# ---------------------------------------------------------
# Hyperparameter tuning
# ---------------------------------------------------------

def tune_model(X_train, y_train):

    model = LogisticRegression(
        max_iter=2000,
        random_state=42,
        solver="liblinear"
    )

    param_grid = {
        "C": [0.01, 0.1, 1, 10, 100],
        "l1_ratio": [0, 1]
    }

    cv = StratifiedKFold(
        n_splits=5,
        shuffle=True,
        random_state=42
    )

    grid_search = GridSearchCV(
        estimator=model,
        param_grid=param_grid,
        scoring="roc_auc",
        cv=cv,
        n_jobs=-1,
        verbose=1
    )

    grid_search.fit(
        X_train,
        y_train
    )

    return grid_search


# ---------------------------------------------------------
# Evaluate tuned model
# ---------------------------------------------------------

def evaluate_model(
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

    metrics = {
        "accuracy": float(
            accuracy_score(
                y_test,
                predictions
            )
        ),

        "precision": float(
            precision_score(
                y_test,
                predictions,
                zero_division=0
            )
        ),

        "recall": float(
            recall_score(
                y_test,
                predictions,
                zero_division=0
            )
        ),

        "f1": float(
            f1_score(
                y_test,
                predictions,
                zero_division=0
            )
        ),

        "roc_auc": float(
            roc_auc_score(
                y_test,
                probabilities
            )
        )
    }

    return metrics


# ---------------------------------------------------------
# Main
# ---------------------------------------------------------

def main():

    print(
        "========== DAY 4 HYPERPARAMETER TUNING =========="
    )

    X_train, X_test, y_train, y_test = (
        load_data()
    )

    print("\nDataset loaded.")

    print(
        "Training shape:",
        X_train.shape
    )

    print(
        "Testing shape:",
        X_test.shape
    )

    print(
        "\nBaseline CV ROC-AUC:",
        round(
            BASELINE_CV_ROC_AUC,
            4
        )
    )

    # -----------------------------------------------------
    # GridSearchCV
    # -----------------------------------------------------

    print(
        "\nStarting GridSearchCV..."
    )

    grid_search = tune_model(
        X_train,
        y_train
    )

    best_model = (
        grid_search.best_estimator_
    )

    best_cv_score = float(
        grid_search.best_score_
    )

    print(
        "\n========== TUNING RESULTS =========="
    )

    print(
        "Best parameters:",
        grid_search.best_params_
    )

    print(
        "Best CV ROC-AUC:",
        round(
            best_cv_score,
            4
        )
    )

    # -----------------------------------------------------
    # Test evaluation
    # -----------------------------------------------------

    test_metrics = evaluate_model(
        best_model,
        X_test,
        y_test
    )

    print(
        "\n========== TEST RESULTS =========="
    )

    for metric, value in (
        test_metrics.items()
    ):
        print(
            f"{metric}: {value:.4f}"
        )

    # -----------------------------------------------------
    # Compare baseline vs tuned model
    # -----------------------------------------------------

    improvement = (
        best_cv_score
        - BASELINE_CV_ROC_AUC
    )

    print(
        "\n========== BASELINE COMPARISON =========="
    )

    print(
        "Baseline CV ROC-AUC:",
        round(
            BASELINE_CV_ROC_AUC,
            4
        )
    )

    print(
        "Tuned CV ROC-AUC:",
        round(
            best_cv_score,
            4
        )
    )

    print(
        "Difference:",
        round(
            improvement,
            4
        )
    )

    improved = (
        best_cv_score
        > BASELINE_CV_ROC_AUC
    )

    print(
        "Improved:",
        improved
    )

    # -----------------------------------------------------
    # Save tuned model
    # -----------------------------------------------------

    model_path = (
        MODEL_DIR /
        "tuned_model.pkl"
    )

    with open(
        model_path,
        "wb"
    ) as file:

        pickle.dump(
            best_model,
            file
        )

    # -----------------------------------------------------
    # Save tuning results
    # -----------------------------------------------------

    results = {
        "baseline": {
            "cv_roc_auc":
                BASELINE_CV_ROC_AUC,

            "test_metrics":
                BASELINE_TEST_METRICS
        },

        "tuning": {
            "method":
                "GridSearchCV",

            "cv_folds":
                5,

            "scoring":
                "roc_auc",

            "best_parameters":
                grid_search.best_params_,

            "best_cv_roc_auc":
                best_cv_score
        },

        "tuned_test_metrics":
            test_metrics,

        "comparison": {
            "cv_roc_auc_difference":
                float(improvement),

            "improved":
                bool(improved)
        }
    }

    results_path = (
        TUNING_DIR /
        "results.json"
    )

    with open(
        results_path,
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            results,
            file,
            indent=4
        )

    print(
        "\nTuned model saved to:",
        model_path
    )

    print(
        "Tuning results saved to:",
        results_path
    )

    print(
        "\nHyperparameter tuning completed."
    )


if __name__ == "__main__":
    main()