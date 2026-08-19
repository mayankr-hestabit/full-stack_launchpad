# Data Report — Week 6, Day 1
**Project:** Customer Churn Prediction (Binary Classification)
**Source script:** `pipelines/data_pipeline.py`
**Raw dataset:** `data/raw/customer_churn_raw.csv`
**Cleaned dataset:** `data/processed/final.csv`

---

## 1. Dataset Overview

| Property | Value |
|---|---|
| Raw rows | 1,512 |
| Raw columns | 13 |
| Target column | `churn` (0 = retained, 1 = churned) |
| ID column | `customer_id` |
| Final rows (after cleaning) | 1,494 |
| Final target balance | 1,099 retained (73.56%) / 395 churned (26.44%) |

**Features:**
- **Numerical (8):** `age`, `income`, `tenure_years`, `monthly_spend`, `support_calls`, `satisfaction_score`, `login_frequency`, `contract_months`
- **Categorical (2, used for EDA):** `city`, `payment_method` (a third categorical column, `plan`, exists in the raw data but wasn't included in the categorical EDA loop)

The target is **moderately imbalanced** (~26% positive class). Accuracy alone will be a misleading metric for Day 3 model evaluation — precision/recall/F1/ROC-AUC and class weighting (or SMOTE) should be prioritized instead.

---

## 2. Missing Values (raw data, before cleaning)

| Column | Missing Count | Missing % |
|---|---|---|
| `age` | 25 | 1.65% |
| `income` | 20 | 1.32% |
| `satisfaction_score` | 22 | 1.46% |
| `city` | 18 | 1.19% |
| `payment_method` | 15 | 0.99% |

All other columns had zero missing values. Missingness is low across the board (<2% per column) — consistent with scattered data-entry gaps rather than a systematic collection problem (visually confirmed in `missing_value_heatmap.png`).

**Handling:**
- Numerical columns (`age`, `income`, `satisfaction_score`) imputed with **median** — chosen over mean because `income` in particular is right-skewed with outliers that would distort a mean.
- Categorical columns (`city`, `payment_method`) imputed with **mode** (most frequent value).

---

## 3. Outlier Detection

Both **IQR (1.5× rule)** and **Z-score (|z| > 3)** methods were computed on all 8 numerical columns:

| Column | IQR Lower | IQR Upper | IQR Outliers | Z-score Outliers |
|---|---|---|---|---|
| age | -4.50 | 87.50 | 0 | 0 |
| income | -11,594.72 | 130,278.64 | 54 | 18 |
| tenure_years | -8.00 | 24.00 | 0 | 0 |
| monthly_spend | -17.37 | 190.09 | 28 | 4 |
| support_calls | -2.00 | 6.00 | 18 | 5 |
| satisfaction_score | 2.93 | 11.52 | 3 | 1 |
| login_frequency | 1.80 | 34.26 | 12 | 0 |
| contract_months | -21.00 | 51.00 | 0 | 0 |

**Observation:** `income` and `monthly_spend` show the largest gap between IQR and Z-score counts — both are right-skewed, so IQR flags many points that Z-score (which assumes rough normality) doesn't catch.

**Removal policy:** Rather than dropping every IQR-flagged point (54 rows on `income` alone — too aggressive, and many are likely legitimate high earners), the pipeline only removes values beyond **3× the IQR upper bound** on the three columns with the most implausible-looking spikes:

| Column | 3× IQR Upper Bound Threshold | Rows Beyond Threshold |
|---|---|---|
| `income` | 390,835.93 | 2 |
| `monthly_spend` | 570.28 | 2 |
| `support_calls` | 18.00 | 2 |

**Result: 6 rows removed** (0.4% of the dataset) — clear data-entry errors (e.g. income of ₹420,000–₹500,000, monthly spend of ₹900–₹1,100, 22–25 support calls in a period where the typical range is under 6) without discarding legitimate variance in the rest of the distribution.

---

## 4. Duplicates

**12 duplicate rows removed** via `df.drop_duplicates()` after outlier cleaning and imputation.

---

## 5. Correlation with Target

| Feature | Correlation with `churn` |
|---|---|
| `age` | **+0.262** |
| `satisfaction_score` | **−0.219** |
| `income` | −0.149 |
| `login_frequency` | −0.095 |
| `contract_months` | −0.072 |
| `support_calls` | +0.042 |
| `tenure_years` | −0.026 |
| `monthly_spend` | −0.003 |

**Key takeaways:**
- `age` and `satisfaction_score` are the strongest signals — older customers and less-satisfied customers churn more — but even these are weak (|r| < 0.3).
- All correlations are weak overall. This is a noisy, realistic dataset — no single feature dominates, so **non-linear models (Random Forest, XGBoost) and engineered features will matter more than raw linear relationships** going into Day 3.
- `monthly_spend` and `tenure_years` show almost no linear relationship with churn on their own — worth checking for interaction effects (e.g. spend relative to tenure) in Day 2 feature engineering rather than assuming they're unimportant.

Full matrix saved to `correlation_heatmap.png`.

---

## 6. Categorical Feature Patterns

**Churn rate by city:**

| City | Churn Rate |
|---|---|
| Hyderabad | 31.39% |
| Mumbai | 30.00% |
| Bengaluru | 25.10% |
| Delhi | 24.52% |
| Pune | 24.47% |
| Jaipur | 23.35% |

**Churn rate by payment method:**

| Payment Method | Churn Rate |
|---|---|
| NetBanking | 28.78% |
| Card | 26.30% |
| UPI | 25.91% |
| Wallet | 24.84% |

Hyderabad and Mumbai run noticeably higher churn than the other cities (~7-8 points above Jaipur/Pune); NetBanking users churn somewhat more than Wallet users. These gaps are worth testing for statistical significance before treating them as strong signals, given the moderate sample sizes per group.

Full breakdown saved to `city_churn_rate.png` and `payment_method_churn_rate.png`.

---

## 7. Cleaning Summary

| Step | Rows Removed | Rows Remaining |
|---|---|---|
| Raw data | — | 1,512 |
| Extreme outlier removal (3× IQR) | 6 | 1,506 |
| Duplicate removal | 12 | 1,494 |
| **Final cleaned dataset** | **18 total** | **1,494** |

Cleaned data saved to: **`data/processed/final.csv`**

---

## 8. Train / Validation / Test Split

A **stratified 70/15/15 split** on `churn` (via the custom `stratified_split()` function) to preserve the ~26% churn rate across all three sets:

| Split | Rows | Churn % |
|---|---|---|
| Train | 1,045 | 26.41% |
| Validation | 224 | 26.34% |
| Test | 225 | 26.67% |

Saved to `data/processed/train.csv`, `val.csv`, `test.csv`.

---

## 9. Files Generated by `data_pipeline.py`

```
data/processed/
├── final.csv                         # Full cleaned dataset
├── train.csv / val.csv / test.csv    # Stratified splits
├── {age,income,tenure_years,monthly_spend,support_calls,
│    satisfaction_score,login_frequency,contract_months}_distribution.png
├── {age,income,tenure_years,monthly_spend,support_calls,
│    satisfaction_score,login_frequency,contract_months}_boxplot.png
├── correlation_heatmap.png
├── missing_value_heatmap.png
├── city_churn_rate.png
└── payment_method_churn_rate.png
```

---