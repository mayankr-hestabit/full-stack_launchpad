import json
import pickle
import numpy as np
import matplotlib.pyplot as plt

from pathlib import Path

from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.neural_network import MLPClassifier

from sklearn.model_selection import StratifiedKFold, cross_validate

from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    roc_auc_score,
    confusion_matrix,
    ConfusionMatrixDisplay
)

from xgboost import XGBClassifier


# ---------------------------------------------------------
# Paths
# ---------------------------------------------------------

BASE_DIR = Path(__file__).resolve().parents[1]

ARTIFACT_DIR = BASE_DIR / "features" / "artifacts"
MODEL_DIR = BASE_DIR / "models"
EVALUATION_DIR = BASE_DIR / "evaluation"

MODEL_DIR.mkdir(parents=True, exist_ok=True)
EVALUATION_DIR.mkdir(parents=True, exist_ok=True)


# ---------------------------------------------------------
# Load feature data
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
# Define models
# ---------------------------------------------------------

def get_models():

    models = {
        "Logistic Regression": LogisticRegression(
            max_iter=2000,
            random_state=42
        ),

        "Random Forest": RandomForestClassifier(
            n_estimators=200,
            random_state=42,
            class_weight="balanced"
        ),

        "XGBoost": XGBClassifier(
            n_estimators=200,
            learning_rate=0.05,
            max_depth=4,
            random_state=42,
            eval_metric="logloss"
        ),

        "Neural Network": MLPClassifier(
            hidden_layer_sizes=(64, 32),
            max_iter=1000,
            random_state=42
        )
    }

    return models


# ---------------------------------------------------------
# Cross-validation
# ---------------------------------------------------------

def evaluate_with_cross_validation(
    model,
    X_train,
    y_train
):

    cv = StratifiedKFold(
        n_splits=5,
        shuffle=True,
        random_state=42
    )

    scoring = {
        "accuracy": "accuracy",
        "precision": "precision",
        "recall": "recall",
        "f1": "f1",
        "roc_auc": "roc_auc"
    }

    results = cross_validate(
        model,
        X_train,
        y_train,
        cv=cv,
        scoring=scoring,
        n_jobs=-1
    )

    metrics = {
        "accuracy": float(
            np.mean(results["test_accuracy"])
        ),
        "precision": float(
            np.mean(results["test_precision"])
        ),
        "recall": float(
            np.mean(results["test_recall"])
        ),
        "f1": float(
            np.mean(results["test_f1"])
        ),
        "roc_auc": float(
            np.mean(results["test_roc_auc"])
        )
    }

    return metrics


# ---------------------------------------------------------
# Test evaluation
# ---------------------------------------------------------

def evaluate_on_test(
    model,
    X_test,
    y_test
):

    predictions = model.predict(X_test)

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

    return metrics, predictions


# ---------------------------------------------------------
# Plot confusion matrix
# ---------------------------------------------------------

def save_confusion_matrix(
    y_test,
    predictions,
    model_name
):

    cm = confusion_matrix(
        y_test,
        predictions
    )

    display = ConfusionMatrixDisplay(
        confusion_matrix=cm
    )

    display.plot()

    plt.title(
        f"Confusion Matrix - {model_name}"
    )

    plt.tight_layout()

    output_path = (
        EVALUATION_DIR /
        "confusion_matrix.png"
    )

    plt.savefig(output_path)

    plt.close()

    print(
        "Confusion matrix saved to:",
        output_path
    )


# ---------------------------------------------------------
# Main training pipeline
# ---------------------------------------------------------

def train_models():

    (
        X_train,
        X_test,
        y_train,
        y_test
    ) = load_data()

    print("Training data loaded.")

    print(
        "X_train shape:",
        X_train.shape
    )

    print(
        "X_test shape:",
        X_test.shape
    )

    models = get_models()

    all_metrics = {}

    best_model_name = None
    best_model = None

    best_cv_roc_auc = -1

    # -----------------------------------------------------
    # Train and evaluate every model
    # -----------------------------------------------------

    for model_name, model in models.items():

        print(
            f"\n========== {model_name} =========="
        )

        cv_metrics = (
            evaluate_with_cross_validation(
                model,
                X_train,
                y_train
            )
        )

        print(
            "5-Fold CV Results:"
        )

        for metric, value in cv_metrics.items():
            print(
                f"{metric}: {value:.4f}"
            )

        # Select best model using CV ROC-AUC
        if (
            cv_metrics["roc_auc"]
            > best_cv_roc_auc
        ):

            best_cv_roc_auc = (
                cv_metrics["roc_auc"]
            )

            best_model_name = model_name
            best_model = model

        all_metrics[model_name] = {
            "cross_validation": cv_metrics
        }

    # -----------------------------------------------------
    # Train best model on entire training set
    # -----------------------------------------------------

    print(
        "\n========== BEST MODEL =========="
    )

    print(
        "Selected model:",
        best_model_name
    )

    print(
        "Best CV ROC-AUC:",
        round(
            best_cv_roc_auc,
            4
        )
    )

    best_model.fit(
        X_train,
        y_train
    )

    # -----------------------------------------------------
    # Evaluate best model on test set
    # -----------------------------------------------------

    (
        test_metrics,
        predictions
    ) = evaluate_on_test(
        best_model,
        X_test,
        y_test
    )

    print(
        "\nTest Results:"
    )

    for metric, value in test_metrics.items():
        print(
            f"{metric}: {value:.4f}"
        )

    all_metrics[
        best_model_name
    ]["test_metrics"] = test_metrics

    # -----------------------------------------------------
    # Save best model
    # -----------------------------------------------------

    model_path = (
        MODEL_DIR /
        "best_model.pkl"
    )

    with open(
        model_path,
        "wb"
    ) as file:

        pickle.dump(
            best_model,
            file
        )

    print(
        "\nBest model saved to:",
        model_path
    )

    # -----------------------------------------------------
    # Save metrics
    # -----------------------------------------------------

    all_metrics["best_model"] = {
        "name": best_model_name,
        "selection_metric":
            "5-fold CV ROC-AUC",
        "cv_roc_auc":
            best_cv_roc_auc,
        "test_metrics":
            test_metrics
    }

    metrics_path = (
        EVALUATION_DIR /
        "metrics.json"
    )

    with open(
        metrics_path,
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            all_metrics,
            file,
            indent=4
        )

    print(
        "Metrics saved to:",
        metrics_path
    )

    # -----------------------------------------------------
    # Confusion matrix
    # -----------------------------------------------------

    save_confusion_matrix(
        y_test,
        predictions,
        best_model_name
    )

    print(
        "\nTraining pipeline completed."
    )


# ---------------------------------------------------------
# Entry point
# ---------------------------------------------------------

if __name__ == "__main__":
    train_models()