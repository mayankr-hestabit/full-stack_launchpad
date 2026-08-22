# Model Comparison Report

## Week 6 — Day 3: Model Building and Advanced Training Pipeline

## 1. Objective

The objective of Day 3 was to build a unified machine-learning training pipeline capable of:

* Training multiple classification models
* Performing 5-fold cross-validation
* Comparing models using multiple evaluation metrics
* Selecting the best model automatically
* Saving the final trained model
* Saving evaluation metrics
* Generating a confusion matrix

The customer churn dataset prepared during Day 2 was used for model training and evaluation.

---

# 2. Input Data

The training pipeline uses the selected features generated during the Day 2 feature-selection process.

Final input shapes:

```text
X_train: 1195 × 15
X_test:   299 × 15

y_train: 1195
y_test:   299
```

The 15 features were obtained after:

```text
33 processed features
        ↓
Correlation threshold
        ↓
28 features
        ↓
Mutual Information
        ↓
20 features
        ↓
Recursive Feature Elimination
        ↓
15 final features
```

---

# 3. Models Trained

The following four models were included in the unified training pipeline:

1. Logistic Regression
2. Random Forest
3. XGBoost
4. Neural Network

These models represent different categories of machine-learning algorithms.

---

## 3.1 Logistic Regression

Logistic Regression is a linear classification algorithm that estimates the probability of a binary outcome.

It provides a simple and interpretable baseline model for the churn-classification problem.

---

## 3.2 Random Forest

Random Forest is an ensemble model consisting of multiple decision trees.

It can capture nonlinear relationships and feature interactions that may not be captured by linear models.

Class weighting was used to help account for the imbalance between churned and non-churned customers.

---

## 3.3 XGBoost

XGBoost is a gradient-boosted decision-tree algorithm.

Unlike Random Forest, where trees are built largely independently, boosting builds trees sequentially so that later trees attempt to correct errors made by earlier trees.

---

## 3.4 Neural Network

A Multi-Layer Perceptron classifier was used as the neural-network model.

The model contains hidden layers that allow it to learn nonlinear relationships between the selected input features and the churn target.

---

# 4. Cross-Validation Strategy

Each model was evaluated using:

```text
5-Fold Stratified Cross-Validation
```

The training dataset was divided into five folds.

For every iteration:

```text
4 folds → model training
1 fold  → validation
```

This process was repeated five times so every fold served as the validation set once.

Stratified cross-validation was used to preserve the approximate churn-class distribution in every fold.

The test dataset was not used during cross-validation.

---

# 5. Evaluation Metrics

Five evaluation metrics were calculated for each model.

## Accuracy

Accuracy represents the proportion of all predictions that were correct.

```text
Accuracy =
Correct Predictions / Total Predictions
```

---

## Precision

Precision measures how many customers predicted to churn actually churned.

```text
Precision =
True Positives /
(True Positives + False Positives)
```

---

## Recall

Recall measures how many actual churn customers were successfully identified.

```text
Recall =
True Positives /
(True Positives + False Negatives)
```

---

## F1 Score

F1 Score is the harmonic mean of precision and recall.

It is particularly useful when classes are imbalanced.

---

## ROC-AUC

ROC-AUC measures how effectively a classifier separates the positive and negative classes across different probability thresholds.

A higher ROC-AUC generally indicates stronger ranking and discrimination ability.

---

# 6. Cross-Validation Results

The average results from 5-fold cross-validation were:

| Model               | Accuracy | Precision |     Recall |   F1 Score |    ROC-AUC |
| ------------------- | -------: | --------: | ---------: | ---------: | ---------: |
| Logistic Regression |   0.7640 |    0.6421 |     0.2943 |     0.3954 | **0.7436** |
| Random Forest       |   0.7063 |    0.4481 | **0.4177** | **0.4296** |     0.7001 |
| XGBoost             |   0.7280 |    0.4958 |     0.2563 |     0.3320 |     0.7027 |
| Neural Network      |   0.6820 |    0.3944 |     0.3546 |     0.3711 |     0.6425 |

---

# 7. Model Comparison

## Logistic Regression

Cross-validation results:

```text
Accuracy:   0.7640
Precision:  0.6421
Recall:     0.2943
F1 Score:   0.3954
ROC-AUC:    0.7436
```

Logistic Regression achieved:

* The highest cross-validation accuracy
* The highest precision
* The highest ROC-AUC

Its recall was lower than Random Forest and the Neural Network.

---

## Random Forest

Cross-validation results:

```text
Accuracy:   0.7063
Precision:  0.4481
Recall:     0.4177
F1 Score:   0.4296
ROC-AUC:    0.7001
```

Random Forest achieved:

* The highest recall
* The highest F1 score

This indicates that it detected more churn cases than Logistic Regression.

However, its precision and ROC-AUC were lower.

---

## XGBoost

Cross-validation results:

```text
Accuracy:   0.7280
Precision:  0.4958
Recall:     0.2563
F1 Score:   0.3320
ROC-AUC:    0.7027
```

XGBoost produced reasonable accuracy and ROC-AUC but did not outperform Logistic Regression in this dataset.

---

## Neural Network

Cross-validation results:

```text
Accuracy:   0.6820
Precision:  0.3944
Recall:     0.3546
F1 Score:   0.3711
ROC-AUC:    0.6425
```

The Neural Network had the lowest ROC-AUC among the evaluated models.

The available dataset is relatively small, which may limit the advantage of a neural-network architecture.

---

# 8. Best Model Selection

The best model was selected automatically using:

```text
Mean 5-Fold Cross-Validation ROC-AUC
```

The highest ROC-AUC was:

```text
Logistic Regression
ROC-AUC = 0.7436
```

Therefore, the selected model was:

```text
BEST MODEL:
Logistic Regression
```

Using cross-validation performance instead of test-set performance for model selection helps keep the test dataset independent.

---

# 9. Final Test Evaluation

After selecting Logistic Regression, it was trained on the complete training dataset and evaluated on the independent test dataset.

Test results:

```text
Accuracy:   0.7692
Precision:  0.6923
Recall:     0.2278
F1 Score:   0.3429
ROC-AUC:    0.7644
```

---

# 10. Test Result Interpretation

## Accuracy

```text
76.92%
```

Approximately 77% of all test predictions were correct.

However, accuracy should not be used alone because the dataset contains more non-churn customers than churn customers.

---

## Precision

```text
69.23%
```

When the model predicted that a customer would churn, approximately 69% of those predictions were correct.

This is relatively strong precision.

---

## Recall

```text
22.78%
```

The recall is comparatively low.

This means the model identified only about 23% of the actual churn customers at the default decision threshold.

Therefore, many churn cases were classified as non-churn.

This is an important limitation for a churn-prediction application, where identifying customers at risk of leaving may be especially important.

---

## F1 Score

```text
34.29%
```

The F1 score is reduced mainly because of the low recall.

---

## ROC-AUC

```text
0.7644
```

The test ROC-AUC indicates that Logistic Regression provides a reasonable ability to distinguish between churn and non-churn customers.

---

# 11. Cross-Validation vs Test Performance

For Logistic Regression:

```text
Cross-validation ROC-AUC: 0.7436
Test ROC-AUC:             0.7644
```

These results are relatively close.

This suggests that the model's test performance is reasonably consistent with its cross-validation performance and does not show an obvious large generalization gap.

---

# 12. Overfitting and Underfitting Considerations

Overfitting occurs when a model learns the training data too closely and performs poorly on unseen data.

Underfitting occurs when a model is too simple to capture meaningful patterns.

In this experiment, Logistic Regression achieved:

```text
CV ROC-AUC:   0.7436
Test ROC-AUC: 0.7644
```

Since the two values are reasonably close, there is no strong indication of severe overfitting based on these results.

The lower recall suggests that future improvement should focus more on class handling and decision thresholds rather than simply increasing model complexity.

---

# 13. Regularization

Logistic Regression uses regularization to control model complexity.

Regularization helps:

* Reduce overfitting
* Prevent excessively large coefficients
* Improve generalization

The current implementation uses the default L2 regularization provided by scikit-learn's Logistic Regression.

Future experiments could compare:

```text
L1 regularization
L2 regularization
Different regularization strengths
```

---

# 14. Class Imbalance Consideration

The target distribution contains substantially more non-churn customers than churn customers.

This affects metrics such as accuracy and recall.

The selected Logistic Regression model has good precision but relatively low recall.

Future improvements could explore:

* Class weights
* SMOTE
* Probability-threshold tuning
* Precision-recall curve analysis
* Cost-sensitive classification

These techniques could improve detection of churn customers.

---

# 15. Confusion Matrix

A confusion matrix was generated for the selected Logistic Regression model.

It is saved as:

```text
src/evaluation/confusion_matrix.png
```

The confusion matrix visualizes:

* True negatives
* False positives
* False negatives
* True positives

It helps identify which types of classification errors the model makes.

---

# 16. Saved Best Model

The selected Logistic Regression model was serialized and stored at:

```text
src/models/best_model.pkl
```

This saved model can be loaded later without retraining.

It can be used during:

* Evaluation
* Deployment
* API inference
* Monitoring

---

# 17. Metrics Output

All model-comparison results were saved to:

```text
src/evaluation/metrics.json
```

The file contains cross-validation metrics for all four models and final test metrics for the selected model.

---

# 18. Day 3 Pipeline Architecture

```text
Day 2 Selected Features
          ↓
X_train / y_train
          ↓
┌───────────────────────────────┐
│                               │
│  Logistic Regression          │
│  Random Forest                │
│  XGBoost                      │
│  Neural Network               │
│                               │
└───────────────┬───────────────┘
                ↓
      5-Fold Stratified CV
                ↓
      Calculate Metrics
                ↓
 Accuracy / Precision / Recall
      F1 Score / ROC-AUC
                ↓
        Compare Models
                ↓
 Select Highest CV ROC-AUC
                ↓
      Logistic Regression
                ↓
 Train Using Full Training Set
                ↓
     Evaluate on Test Set
                ↓
       Confusion Matrix
                ↓
      Save Best Model
                ↓
      best_model.pkl
```

---

# 19. Day 3 Deliverables

The required deliverables were:

```text
src/training/
└── train.py

src/models/
└── best_model.pkl

src/evaluation/
└── metrics.json

MODEL-COMPARISON.md
```

Additional generated output:

```text
src/evaluation/
└── confusion_matrix.png
```

---

# 20. Final Conclusion

A unified model-training pipeline was successfully implemented for customer churn prediction.

Four classification algorithms were trained and evaluated using 5-fold stratified cross-validation:

```text
Logistic Regression
Random Forest
XGBoost
Neural Network
```

The best model was selected automatically using mean cross-validation ROC-AUC.

The final selected model was:

```text
Logistic Regression
```

with:

```text
Cross-validation ROC-AUC: 0.7436
Test ROC-AUC:             0.7644
Test Accuracy:            0.7692
Test Precision:           0.6923
Test Recall:              0.2278
Test F1 Score:            0.3429
```

The model provides reasonable overall discrimination and relatively strong precision, although recall remains an area for improvement.

The trained model, metrics, and confusion matrix were successfully persisted, completing the core requirements of Week 6 Day 3.
