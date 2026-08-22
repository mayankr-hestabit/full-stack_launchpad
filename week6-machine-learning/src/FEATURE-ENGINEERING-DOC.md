# Feature Engineering Documentation

## Week 6 — Day 2: Feature Engineering and Feature Selection

## 1. Objective

The objective of Day 2 was to build a reusable feature-engineering and feature-selection pipeline that converts the cleaned customer churn dataset produced during Day 1 into model-ready training and testing data.

The pipeline performs:

* Categorical feature encoding
* Numerical feature normalization
* Creation of 10+ engineered features
* Train/test splitting
* Correlation-based feature filtering
* Mutual Information feature selection
* Recursive Feature Elimination (RFE)
* Feature-importance visualization
* Persistence of preprocessing and feature artifacts

---

## 2. Input Dataset

The pipeline uses the cleaned dataset generated during Day 1:

```text
src/data/processed/final.csv
```

Dataset shape:

```text
1494 rows × 13 columns
```

### Dataset Columns

```text
customer_id
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
churn
```

The target variable is:

```text
churn
```

The identifier column is:

```text
customer_id
```

`customer_id` was removed before model preprocessing because it uniquely identifies customers and does not represent a meaningful behavioral or demographic feature for prediction.

---

## 3. Feature Categories

### Numerical Features

The original numerical features are:

```text
age
income
tenure_years
monthly_spend
support_calls
satisfaction_score
login_frequency
contract_months
```

### Categorical Features

The categorical features are:

```text
city
plan
payment_method
```

### Target Feature

```text
churn
```

The target contains two classes:

```text
0 = Customer did not churn
1 = Customer churned
```

The cleaned dataset contained:

```text
Class 0: 1099
Class 1: 395
```

This indicates moderate class imbalance.

---

# 4. Feature Engineering

Feature engineering was performed to create additional information from the existing variables.

The pipeline generates 12 new numerical features.

## 4.1 Polynomial Features

Polynomial transformations were used to represent possible nonlinear relationships.

### Age Squared

```text
age_squared = age²
```

This allows models to capture nonlinear effects associated with customer age.

### Support Calls Squared

```text
support_calls_squared = support_calls²
```

This can capture situations where a high number of support calls has a disproportionately large relationship with churn.

### Satisfaction Squared

```text
satisfaction_squared = satisfaction_score²
```

This represents possible nonlinear effects associated with customer satisfaction.

### Login Frequency Squared

```text
login_frequency_squared = login_frequency²
```

This allows nonlinear customer-engagement patterns to be represented.

### Contract Months Squared

```text
contract_months_squared = contract_months²
```

This can represent nonlinear relationships between contract duration and customer churn.

---

## 4.2 Log Transformations

Log transformations reduce the effect of large values and can help transform skewed numerical distributions.

### Income Log

```text
income_log = log(1 + income)
```

`log1p()` was used to safely calculate the logarithm.

### Monthly Spend Log

```text
monthly_spend_log = log(1 + monthly_spend)
```

This reduces the effect of extreme spending values.

---

## 4.3 Ratio Features

Ratio features were created to represent relationships between customer behavior and customer characteristics.

### Spend Per Tenure

```text
spend_per_tenure =
monthly_spend / tenure_years
```

This represents customer spending relative to tenure.

### Support Calls Per Tenure

```text
support_calls_per_tenure =
support_calls / tenure_years
```

This represents the frequency of support interactions relative to customer tenure.

### Login Per Contract

```text
login_per_contract =
login_frequency / contract_months
```

This represents login activity relative to contract duration.

### Income Per Age

```text
income_per_age =
income / age
```

This creates a relative income indicator.

### Spend Per Login

```text
spend_per_login =
monthly_spend / login_frequency
```

This represents spending relative to customer engagement.

Division-by-zero cases are handled by temporarily replacing zero denominators with missing values and subsequently handling resulting invalid values safely.

---

# 5. Train/Test Splitting

The dataset was divided into training and testing sets using:

```text
80% training
20% testing
```

The resulting shapes before categorical encoding were:

```text
X_train: 1195 × 23
X_test:   299 × 23
```

The split uses:

```text
random_state = 42
```

for reproducibility.

The `stratify` option was applied using the churn target.

This ensures that approximately the same churn/non-churn class distribution is maintained in both training and testing datasets.

---

# 6. Prevention of Data Leakage

The dataset was split into training and testing sets before fitting preprocessing transformations.

The preprocessing pipeline was fitted using:

```text
X_train
```

The fitted pipeline was then used to transform:

```text
X_train
X_test
```

Therefore, information from the test dataset does not influence the fitted preprocessing parameters.

This is important for obtaining reliable model evaluation results.

---

# 7. Categorical Feature Encoding

Categorical variables were transformed using:

```text
OneHotEncoder
```

The encoded columns include categories derived from:

```text
city
plan
payment_method
```

One-hot encoding creates independent binary columns for categorical values.

The encoder was configured with:

```text
handle_unknown = "ignore"
```

This prevents errors when previously unseen categories appear during future transformations.

---

# 8. Numerical Feature Normalization

Numerical features were normalized using:

```text
StandardScaler
```

StandardScaler transforms numerical variables approximately according to:

```text
z = (x - mean) / standard deviation
```

This produces features centered around zero with comparable scales.

Scaling is particularly useful for algorithms that are sensitive to feature magnitude.

The scaler was fitted only on the training dataset.

---

# 9. Processed Feature Dataset

After feature engineering, categorical encoding, and numerical scaling, the datasets contained:

```text
X_train: 1195 × 33
X_test:   299 × 33
```

Therefore, the preprocessing pipeline produced:

```text
33 model-ready features
```

before feature selection.

---

# 10. Feature Selection

Three feature-selection techniques were applied:

1. Correlation threshold
2. Mutual Information
3. Recursive Feature Elimination

The feature-selection process was performed using training data to prevent test-data leakage.

---

## 10.1 Correlation Threshold

Highly correlated features can provide redundant information and may unnecessarily increase model complexity.

A correlation threshold of:

```text
0.95
```

was used.

Features with absolute correlation greater than the threshold were removed.

Before correlation filtering:

```text
33 features
```

Highly correlated features removed:

```text
5 features
```

The removed features were:

```text
numerical__age_squared
numerical__satisfaction_squared
numerical__login_frequency_squared
numerical__contract_months_squared
numerical__monthly_spend_log
```

After correlation filtering:

```text
28 features
```

This step reduces feature redundancy.

---

# 11. Mutual Information

Mutual Information measures how much information a feature provides about the target variable.

Unlike simple correlation, Mutual Information can detect some nonlinear dependencies.

The pipeline calculated Mutual Information between each remaining feature and:

```text
churn
```

The top:

```text
20 features
```

were retained.

Some of the highest Mutual Information scores were observed for:

```text
income_per_age
satisfaction_score
income
income_log
age
spend_per_tenure
contract_months
tenure_years
```

For example:

```text
income_per_age        ≈ 0.0374
satisfaction_score    ≈ 0.0332
income                ≈ 0.0310
income_log            ≈ 0.0294
age                   ≈ 0.0190
```

After Mutual Information selection:

```text
20 features remained
```

---

# 12. Recursive Feature Elimination (RFE)

The final feature-selection stage uses:

```text
Recursive Feature Elimination (RFE)
```

RFE repeatedly trains an estimator and removes less useful features until the desired number of features remains.

A Logistic Regression estimator was used with RFE.

The final number of selected features was:

```text
15
```

---

# 13. Final Selected Features

The final selected features were:

```text
numerical__income_per_age
numerical__satisfaction_score
numerical__income
numerical__income_log
numerical__age
numerical__spend_per_tenure
numerical__contract_months
numerical__tenure_years
categorical__plan_Standard
categorical__plan_Premium
categorical__city_Jaipur
numerical__support_calls
numerical__login_frequency
categorical__city_Bengaluru
categorical__city_Delhi
```

These features represent a combination of:

* Original numerical variables
* Engineered numerical variables
* Encoded categorical variables

---

# 14. Final Feature Dataset

The complete feature-selection process reduced the feature space as follows:

```text
33 original processed features
        ↓
Correlation filtering
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

Final dataset shapes:

```text
X_train_selected: 1195 × 15
X_test_selected:   299 × 15
```

The corresponding targets remain:

```text
y_train: 1195 records
y_test:   299 records
```

These datasets are ready for the model-training stage.

---

# 15. Feature Importance

A feature-selection visualization was generated during the RFE process.

The output is stored as:

```text
src/features/feature_importance.png
```

This provides a visual representation associated with the feature-selection process.

---

# 16. Saved Pipeline and Artifacts

The preprocessing pipeline was persisted using Joblib:

```text
src/features/artifacts/preprocessor.joblib
```

This allows the exact same fitted transformations to be reused later during training, evaluation, and inference.

Additional generated artifacts include:

```text
X_train.npy
X_test.npy
y_train.npy
y_test.npy
X_train_selected.npy
X_test_selected.npy
rfe_ranking.csv
```

The processed feature names are stored in:

```text
src/features/feature_list.json
```

The final RFE-selected feature names are stored in:

```text
src/features/selected_feature_list.json
```

---

# 17. Day 2 Deliverables

The required Day 2 deliverables are:

```text
src/features/
├── build_features.py
├── feature_selector.py
└── feature_list.json

FEATURE-ENGINEERING-DOC.md
```

Additional generated artifacts include:

```text
src/features/
├── selected_feature_list.json
├── feature_importance.png
│
└── artifacts/
    ├── preprocessor.joblib
    ├── X_train.npy
    ├── X_test.npy
    ├── y_train.npy
    ├── y_test.npy
    ├── X_train_selected.npy
    ├── X_test_selected.npy
    └── rfe_ranking.csv
```

---

# 18. Final Pipeline Architecture

The complete Day 2 pipeline follows:

```text
Day 1 final.csv
        ↓
Load Dataset
        ↓
Separate Target
        ↓
Remove customer_id
        ↓
Create 12 Engineered Features
        ↓
Train/Test Split
        ↓
┌──────────────────────────────┐
│                              │
Numerical Features       Categorical Features
│                              │
StandardScaler             OneHotEncoder
│                              │
└──────────────┬───────────────┘
               ↓
       33 Processed Features
               ↓
      Correlation Threshold
               ↓
          28 Features
               ↓
       Mutual Information
               ↓
          20 Features
               ↓
              RFE
               ↓
       15 Selected Features
               ↓
      X_train / X_test
      y_train / y_test
               ↓
       Ready for Training
```

---

# 19. Conclusion

The Day 2 feature-engineering pipeline successfully converts the cleaned customer churn dataset into a model-ready representation.

The pipeline:

* Encodes categorical variables
* Standardizes numerical variables
* Generates more than 10 engineered features
* Uses stratified train/test splitting
* Prevents preprocessing leakage
* Removes highly correlated features
* Uses Mutual Information for relevance-based selection
* Uses RFE for final feature selection
* Reduces 33 processed features to 15 selected features
* Produces `X_train`, `X_test`, `y_train`, and `y_test`
* Saves the fitted preprocessing pipeline
* Saves feature metadata and selected datasets
* Generates a feature-selection visualization

The resulting selected feature datasets are ready to be used in the subsequent model-training and evaluation stages of the machine-learning project.