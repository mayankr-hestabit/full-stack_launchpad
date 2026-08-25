MODEL INTERPRETATION REPORT

Week 6 --- Day 4

Hyperparameter Tuning, Explainability and Error Analysis

1. Objective

The objective of Day 4 was to improve the machine-learning model
selected during Day 3 and understand how the model makes its
predictions.

The main tasks performed were:

Hyperparameter tuning

Comparison with the Day 3 baseline model

Feature importance analysis

SHAP-based model explainability

Error analysis

Error visualization

Bias and variance consideration

The Logistic Regression model selected as the best model during Day 3
was used as the baseline model.

2. Baseline Model

During Day 3, four classification models were trained and compared:

Logistic Regression

Random Forest

XGBoost

Neural Network

The models were evaluated using 5-fold stratified cross-validation.

Logistic Regression achieved the highest cross-validation ROC-AUC and
was therefore selected as the best model.

Baseline Performance

Metric              Value

CV ROC-AUC         0.7436
Test Accuracy      0.7692
Test Precision     0.6923
Test Recall        0.2278
Test F1 Score      0.3429
Test ROC-AUC       0.7644

The baseline CV ROC-AUC of 0.7436 was used as the primary reference
for Day 4 tuning.

3. Hyperparameter Tuning

Hyperparameters are model settings configured before training. Unlike
model parameters, hyperparameters are not directly learned from the
training data.

The Day 4 pipeline used GridSearchCV for hyperparameter tuning.

GridSearchCV systematically evaluates predefined hyperparameter
combinations. Each configuration is evaluated using cross-validation.

The tuning process used:

5-fold stratified cross-validation

ROC-AUC as the optimization metric

Multiple regularization strengths

L1 and L2 regularization alternatives

4. Regularization

Regularization helps control model complexity.

Logistic Regression learns coefficients for its input features. Without
sufficient regularization, a model may assign unnecessarily large
coefficients to certain features and become too sensitive to patterns
present specifically in the training data.

Conceptually:

Prediction Loss + Regularization Penalty = Total Loss

The model attempts to minimize the total loss, encouraging a balance
between fitting the training data and maintaining controlled model
complexity.

The C hyperparameter controls regularization strength in Logistic
Regression:

Smaller C → stronger regularization

Larger C → weaker regularization

The best configuration selected during tuning was:

C = 0.01
Regularization = L2

The small value of C indicates that stronger regularization produced
slightly better cross-validation performance for this dataset.

5. Tuning Results

The Day 3 baseline model achieved:

Baseline CV ROC-AUC = 0.7436

After hyperparameter tuning:

Tuned CV ROC-AUC = 0.7472

Therefore:

Improvement ≈ 0.0036

Baseline vs Tuned CV Performance

Model                            CV ROC-AUC

Baseline Logistic Regression         0.7436
Tuned Logistic Regression            0.7472

The tuned Logistic Regression model was used for the remaining
explainability and error-analysis tasks.

6. Tuned Model Test Performance

Metric        Baseline    Tuned

Accuracy        0.7692   0.7692
Precision       0.6923   0.7273
Recall          0.2278   0.2025
F1 Score        0.3429   0.3168
ROC-AUC         0.7644   0.7645

The tuning process slightly improved cross-validation ROC-AUC and test
ROC-AUC. Precision also increased, while recall and F1 score decreased.

This demonstrates that hyperparameter tuning does not necessarily
improve every evaluation metric simultaneously. GridSearchCV selected
the configuration based on ROC-AUC because ROC-AUC was the specified
optimization metric.

7. Model Explainability

Training a model is only one part of a machine-learning system. It is
also useful to understand:

Which features influence predictions

Which features the model considers important

How individual features push predictions

Where the model makes mistakes

Two explainability approaches were used:

Logistic Regression coefficient-based feature importance

SHAP analysis

8. Feature Importance

Logistic Regression learns one coefficient for each input feature. The
coefficient represents how the feature contributes to the model's
internal prediction score.

The absolute magnitude of a coefficient can be used as an indication of
its influence when features are appropriately transformed and scaled.

The feature importance chart was saved as:

src/evaluation/feature_importance.png

The corresponding values were saved as:

src/evaluation/feature_importance.csv

A positive Logistic Regression coefficient pushes the prediction toward
the positive class (churn = 1), while a negative coefficient pushes
the prediction toward churn = 0.

9. SHAP Explainability

SHAP stands for SHapley Additive exPlanations.

SHAP estimates how individual feature values contribute to model
predictions relative to a baseline.

For a particular prediction, some features may push the model toward
churn while other features may push the model toward non-churn.

The SHAP summary plot was generated and saved as:

src/evaluation/shap_summary.png

The plot provides a global view of feature influence across evaluated
samples and helps identify features with larger overall contributions
and the direction of their effects.

The mean absolute SHAP contribution for each feature was also calculated
and saved as:

src/evaluation/shap_feature_importance.csv

During SHAP analysis, the training dataset contained 1,195 samples. SHAP
automatically subsampled the background dataset to 100 samples for
computational efficiency. The summary plot was generated successfully.

10. Error Analysis

The tuned model was evaluated using 299 test observations.

The results were:

Total predictions: 299
Correct predictions: 230
Total errors: 69
Error rate: 0.2308
False positives: 6
False negatives: 63

Approximately 23.08% of test predictions were incorrect.

False Positives

A false positive occurs when:

Actual value = 0
Predicted value = 1

In this project, this means the model predicted that a customer would
churn, but the customer actually did not churn.

The tuned model produced 6 false positives.

False Negatives

A false negative occurs when:

Actual value = 1
Predicted value = 0

In this project, this means the model predicted that a customer would
stay, but the customer actually churned.

The tuned model produced 63 false negatives.

Most of the model's errors were therefore false negatives.

11. Precision and Recall Interpretation

The tuned model achieved:

Precision ≈ 0.7273
Recall ≈ 0.2025

Precision answers:

Of the customers predicted as churners, how many were actually
churners?

The relatively small number of false positives helps explain the model's
comparatively strong precision.

Recall answers:

Of all customers who actually churned, how many did the model
successfully detect?

The large number of false negatives explains the low recall.

This is an important limitation for a churn-prediction application
because many actual churners are not being identified.

12. Precision-Recall Trade-Off

The tuned model demonstrates a precision-recall trade-off.

It has relatively higher precision, meaning that when it predicts churn
it is often correct. However, its recall is low, meaning that it misses
many customers who actually churn.

Future improvements could investigate decision-threshold tuning if
identifying more churners is considered more important than avoiding
false churn alerts.

13. Error Analysis Heatmap

An error-analysis heatmap was generated and saved as:

src/evaluation/error_analysis_heatmap.png

Predictions were grouped according to predicted churn-probability
ranges.

The heatmap allows error rates to be inspected visually for actual churn
and non-churn classes across different prediction-confidence ranges.

Detailed prediction information was also saved as:

src/evaluation/error_analysis.csv

The file contains:

Actual class

Predicted class

Predicted churn probability

Error indicator

Probability range

14. Bias and Variance

Bias and variance describe two important sources of model error.

High Bias

High bias occurs when a model is too restricted or simple to capture
important relationships in the data. It is commonly associated with
underfitting.

Typical behavior:

Training performance   → poor
Validation performance → poor

High Variance

High variance occurs when a model becomes too dependent on the training
data and does not generalize well to unseen observations. It is commonly
associated with overfitting.

Typical behavior:

Training performance   → very strong
Validation performance → significantly worse

For the current model:

Day 3 CV ROC-AUC   = 0.7436
Day 3 Test ROC-AUC = 0.7644

Tuned CV ROC-AUC   ≈ 0.7472
Tuned Test ROC-AUC ≈ 0.7645

There is no large deterioration from cross-validation performance to
test performance, so these results do not show an obvious severe
generalization gap.

The stronger regularization selected during tuning may help control
model complexity. However, the low recall remains an important
predictive limitation.

15. Day 4 Pipeline Architecture

Day 3 Best Model
Logistic Regression
        |
        v
Baseline CV ROC-AUC
0.7436
        |
        v
Hyperparameter Tuning
        |
        v
GridSearchCV
        |
        +-- C values
        +-- Regularization alternatives
        |
        v
5-Fold Cross-Validation
        |
        v
Optimize ROC-AUC
        |
        v
Best Configuration
C = 0.01 + L2
        |
        v
Tuned CV ROC-AUC
≈ 0.7472
        |
        +-----------------------+
        |                       |
        v                       v
Feature Importance          Error Analysis
        |                       |
        v                       +-- False Positives
SHAP Analysis                  +-- False Negatives
        |                       |
        v                       v
SHAP Summary Plot       Error Analysis Heatmap
        |                       |
        +-----------+-----------+
                    |
                    v
             Model Interpretation

16. Generated Artifacts

Hyperparameter Tuning

src/training/tuning.py

Responsible for GridSearchCV, hyperparameter evaluation, baseline
comparison, and tuned model evaluation.

Tuning Results

src/tuning/results.json

Contains baseline metrics, tuning configuration, best hyperparameters,
best CV ROC-AUC, tuned test metrics, and improvement information.

Tuned Model

src/models/tuned_model.pkl

Contains the tuned Logistic Regression model.

Explainability Pipeline

src/evaluation/shap_analysis.py

Responsible for feature importance, SHAP analysis, SHAP summary
plotting, error analysis, and the error heatmap.

Explainability Outputs

src/evaluation/feature_importance.png
src/evaluation/feature_importance.csv
src/evaluation/shap_summary.png
src/evaluation/shap_feature_importance.csv
src/evaluation/error_analysis_heatmap.png
src/evaluation/error_analysis.csv

17. Exercise Completion

The Day 4 exercise required:

Hyperparameter tuning with Optuna/GridSearch --- Completed using
GridSearchCV

SHAP summary plot --- Completed

Feature importance chart --- Completed

Error analysis heatmap --- Completed

Improvement over baseline --- Completed

Explainability added --- Completed

The baseline CV ROC-AUC increased from approximately:

0.7436 → 0.7472

The best tuned configuration used:

C = 0.01
L2 regularization

18. Required Deliverables

The required Day 4 deliverables were:

/training/tuning.py
/evaluation/shap_analysis.py
/tuning/results.json
MODEL-INTERPRETATION.md

All required deliverables were completed.

Additional useful artifacts were generated:

/models/tuned_model.pkl
/evaluation/shap_summary.png
/evaluation/feature_importance.png
/evaluation/error_analysis_heatmap.png
/evaluation/feature_importance.csv
/evaluation/shap_feature_importance.csv
/evaluation/error_analysis.csv

19. Final Conclusion

Day 4 extended the model-building work completed during Day 3 by
introducing model optimization, explainability, and detailed error
analysis.

GridSearchCV was used to tune the Logistic Regression model using 5-fold
cross-validation and ROC-AUC as the optimization metric.

The baseline cross-validation ROC-AUC increased from approximately:

0.7436 → 0.7472

The best configuration used stronger L2 regularization with:

C = 0.01

The tuned model maintained approximately the same test ROC-AUC while
increasing precision but reducing recall.

Feature importance and SHAP analysis were added to make the model's
predictions more interpretable.

The error analysis identified:

69 total errors
6 false positives
63 false negatives

The large number of false negatives explains the model's relatively low
recall and identifies an important area for future improvement.

Overall, the Day 4 pipeline successfully added hyperparameter
optimization, baseline comparison, model explainability, feature
importance analysis, SHAP analysis, error analysis, and bias/variance
consideration.

This completes the required Week 6 Day 4 hyperparameter tuning,
explainability, and error-analysis workflow.