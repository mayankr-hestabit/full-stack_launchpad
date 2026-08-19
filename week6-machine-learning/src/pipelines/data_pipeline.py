import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

'''
1. Load dataset
2. Basic inspection
  - shape
  - columns
  - dtypes
  - info
  - describe

3. Missing-value analysis
4. Outlier analysis
  - IQR
  - Z-score

5. Remove confirmed artificial outliers
6. Missing-value imputation
  - numerical -> median
  - categorical -> mode

7. Duplicate analysis
8. Remove Duplicates
9. Save the dataset
10. Train/Validation/Test split      <-- NEW
'''

# Load the raw CSV dataset
def load_data(file_path):
    return pd.read_csv(file_path)


# Detect outliers using the IQR method
def detect_iqr_outliers(df, column):
    Q1 = df[column].quantile(0.25)
    Q3 = df[column].quantile(0.75)

    IQR = Q3 - Q1

    lower_bound = Q1 - 1.5 * IQR
    upper_bound = Q3 + 1.5 * IQR

    outliers = (
        (df[column] < lower_bound) |
        (df[column] > upper_bound)
    )

    return outliers, lower_bound, upper_bound


# Calculate Z-score based outliers
def detect_zscore_outliers(df, column):
    z_scores = (
        (df[column] - df[column].mean())
        / df[column].std()
    )

    return np.abs(z_scores) > 3


# NEW: stratified train/val/test split, kept as a plain function
# (same style as your other helpers) rather than pulling in sklearn.
def stratified_split(df, target_col, train_size=0.70, val_size=0.15,
                      test_size=0.15, random_state=42):
    assert abs(train_size + val_size + test_size - 1.0) < 1e-6

    train_frames, val_frames, test_frames = [], [], []

    for cls, group in df.groupby(target_col):
        group = group.sample(frac=1.0, random_state=random_state)
        n = len(group)
        n_train = int(round(n * train_size))
        n_val = int(round(n * val_size))

        train_frames.append(group.iloc[:n_train])
        val_frames.append(group.iloc[n_train:n_train + n_val])
        test_frames.append(group.iloc[n_train + n_val:])

    train_df = pd.concat(train_frames).sample(frac=1.0, random_state=random_state).reset_index(drop=True)
    val_df = pd.concat(val_frames).sample(frac=1.0, random_state=random_state).reset_index(drop=True)
    test_df = pd.concat(test_frames).sample(frac=1.0, random_state=random_state).reset_index(drop=True)

    return train_df, val_df, test_df


# Main execution
if __name__ == "__main__":

    # Define the path to the raw dataset
    file_path = "data/raw/raw_dataset.csv"

    # Load the dataset
    df = load_data(file_path)

    # FIX: keep an untouched copy of the raw data right here, instead of
    # re-reading the CSV from disk later just for the missing-value heatmap.
    raw_df = df.copy()

    # Display the first five rows
    print("\nFirst 5 rows:")
    print(df.head())

    # Display dataset shape
    print("\nShape:")
    print(df.shape)

    # Display column names
    print("\nColumns:")
    print(df.columns)

    # Display data types
    print("\nData Types:")
    print(df.dtypes)

    # Display detailed DataFrame information
    print("\nInfo:")
    df.info()

    # Display descriptive statistics
    print("\nStatistics:")
    print(df.describe())

    # Display missing-value counts
    print("\nMissing values:")
    print(df.isnull().sum())

    # Display missing-value percentages
    print("\nMissing-value percentage:")
    print(df.isnull().mean() * 100)

    # Define numerical columns for outlier analysis
    numerical_columns = [
        "age",
        "income",
        "tenure_years",
        "monthly_spend",
        "support_calls",
        "satisfaction_score",
        "login_frequency",
        "contract_months"
    ]

    # Perform IQR and Z-score analysis
    print("\n========== OUTLIER ANALYSIS ==========")

    # FIX: store the bounds per column so we can reuse them below instead
    # of hardcoding literal outlier values.
    iqr_bounds = {}

    for column in numerical_columns:

        iqr_outliers, lower_bound, upper_bound = (
            detect_iqr_outliers(df, column)
        )

        zscore_outliers = detect_zscore_outliers(df, column)

        iqr_bounds[column] = (lower_bound, upper_bound)

        print(f"\nColumn: {column}")
        print(f"IQR Lower Bound: {lower_bound:.2f}")
        print(f"IQR Upper Bound: {upper_bound:.2f}")
        print(f"IQR Outliers: {iqr_outliers.sum()}")
        print(f"Z-score Outliers: {zscore_outliers.sum()}")

    # Display all IQR outlier values before removing anything
    print("\n========== ALL IQR OUTLIERS ==========")

    for column in numerical_columns:

        outliers, _, _ = detect_iqr_outliers(df, column)

        print(f"\n{column}:")
        print(df.loc[outliers, column].sort_values().to_list())

    # FIX: instead of hardcoding exact values you eyeballed from one run
    # (df["income"].isin([350000, 420000, 500000]) etc.), flag anything
    # beyond 3x the IQR upper bound on the columns that had the worst
    # artificial-looking spikes. This uses the bounds we already computed
    # above, so it keeps working if the raw data changes.
    print("\n========== CONFIRMED OUTLIERS (3x IQR upper bound) ==========")

    income_extreme = df["income"] > (iqr_bounds["income"][1] * 3)
    spend_extreme = df["monthly_spend"] > (iqr_bounds["monthly_spend"][1] * 3)
    calls_extreme = df["support_calls"] > (iqr_bounds["support_calls"][1] * 3)

    print("\nIncome:")
    print(df[income_extreme])

    print("\nMonthly Spend:")
    print(df[spend_extreme])

    print("\nSupport Calls:")
    print(df[calls_extreme])

    # Store the original number of rows
    original_rows = len(df)

    # Remove confirmed artificial outliers
    df = df[
        ~income_extreme &
        ~spend_extreme &
        ~calls_extreme
    ]

    # Reset the DataFrame index
    df = df.reset_index(drop=True)

    # Calculate the number of removed rows
    removed_rows = original_rows - len(df)

    # Display the final shape
    print("\n========== OUTLIER CLEANING RESULT ==========")
    print("Original rows:", original_rows)
    print("Removed rows:", removed_rows)
    print("Remaining rows:", len(df))

    # Display missing values after outlier cleaning
    print("\nMissing values after outlier handling:")
    print(df.isnull().sum())

    # Display missing-value percentages after outlier cleaning
    print("\nMissing-value percentages:")
    print(df.isnull().mean() * 100)

    # Fill missing numerical values with their column median
    df["age"] = df["age"].fillna(df["age"].median())
    df["income"] = df["income"].fillna(df["income"].median())
    df["satisfaction_score"] = df["satisfaction_score"].fillna(
        df["satisfaction_score"].median()
    )

    # Fill missing categorical values with the most frequent value
    df["city"] = df["city"].fillna(df["city"].mode()[0])
    df["payment_method"] = df["payment_method"].fillna(
        df["payment_method"].mode()[0]
    )

    # Verify that no missing values remain
    print("\nMissing values after imputation:")
    print(df.isnull().sum())

    # Count completely duplicated rows
    print("\nNumber of duplicate rows:")
    print(df.duplicated().sum())

    # Display duplicated rows
    print("\nDuplicate rows:")
    print(df[df.duplicated()])

    # Remove completely duplicated rows
    df = df.drop_duplicates()

    # Reset index after removing duplicates
    df = df.reset_index(drop=True)

    # Verify that no duplicate rows remain
    print("\nDuplicates after cleaning:")
    print(df.duplicated().sum())

    # Display final dataset shape
    print("\nShape after duplicate removal:")
    print(df.shape)

    # Save the cleaned dataset as processed data
    df.to_csv("data/processed/final.csv", index=False)
    print("dataset saved as processed data")

    '''
    EDA sequence

    1. Target Distribution
    2. Class Imbalance

    3. Feature Distribution
    4. Correlation Matrix

    5. Missing Value Heatmap
    6. Outlier Visualization

    7. Categorical Feature Analysis
    8. EDA Conclusions
    '''

    # Display the number of customers in each churn class
    print("\nTarget distribution:")
    print(df["churn"].value_counts())

    # Display the percentage of customers in each churn class
    print("\nTarget percentage:")
    print(df["churn"].value_counts(normalize=True) * 100)

    # Plot the distribution of each numerical feature
    for column in numerical_columns:
        df[column].hist(bins=30)
        plt.title(f"Distribution of {column}")
        plt.xlabel(column)
        plt.ylabel("Frequency")
        # Save the feature distribution plot
        plt.savefig(f"data/processed/{column}_distribution.png")
        plt.close()

    # Calculate the correlation matrix for numerical features
    correlation_matrix = df[numerical_columns + ["churn"]].corr()

    # Display the correlation matrix
    print("\nCorrelation Matrix:")
    print(correlation_matrix)

    # Create a heatmap of the correlation matrix
    plt.figure(figsize=(10, 8))
    plt.imshow(correlation_matrix, cmap="coolwarm", aspect="auto")
    plt.colorbar()

    # Add feature names to the axes
    plt.xticks(range(len(correlation_matrix.columns)),
            correlation_matrix.columns,
            rotation=45,
            ha="right")
    plt.yticks(range(len(correlation_matrix.columns)),
            correlation_matrix.columns)

    # Add correlation values inside the cells
    for i in range(len(correlation_matrix)):
        for j in range(len(correlation_matrix)):
            plt.text(j, i, f"{correlation_matrix.iloc[i, j]:.2f}",
                    ha="center", va="center")

    # Add title and save the heatmap
    plt.title("Correlation Matrix")
    plt.tight_layout()
    plt.savefig("data/processed/correlation_heatmap.png")
    plt.close()

    # FIX: no longer re-reading the CSV from disk here -- reuse the
    # raw_df copy we saved right after load_data() at the top.
    plt.figure(figsize=(10, 6))
    plt.imshow(raw_df.isnull(), aspect="auto")

    plt.title("Missing Value Heatmap")
    plt.xlabel("Columns")
    plt.ylabel("Rows")

    plt.xticks(
        range(len(raw_df.columns)),
        raw_df.columns,
        rotation=45,
        ha="right"
    )

    plt.tight_layout()
    plt.savefig("data/processed/missing_value_heatmap.png")
    plt.close()

    # Outlier Visualization
    for column in numerical_columns:
        plt.figure(figsize=(8, 5))

        plt.boxplot(raw_df[column].dropna())

        plt.title(f"Boxplot of {column}")
        plt.ylabel(column)

        plt.tight_layout()
        plt.savefig(f"data/processed/{column}_boxplot.png")
        plt.close()

    # Categorical feature analysis
    categorical_columns = [
        "city",
        "payment_method"
    ]

    # Visualizing categorical feature
    for column in categorical_columns:
        print(f"\nChurn by {column}:")
        print(
            pd.crosstab(
                df[column],
                df["churn"],
                normalize="index"
            ) * 100
        )
    for column in categorical_columns:
        churn_rate = (
            df.groupby(column)["churn"]
            .mean()
            .sort_values(ascending=False)
        )

        churn_rate.plot(kind="bar")

        plt.title(f"Churn Rate by {column}")
        plt.xlabel(column)
        plt.ylabel("Churn Rate")

        plt.tight_layout()
        plt.savefig(f"data/processed/{column}_churn_rate.png")
        plt.close()

    # NEW: Train / Validation / Test split (stratified on churn so the
    # ~26% churn rate is preserved in every split).
    print("\n========== TRAIN / VAL / TEST SPLIT ==========")

    train_df, val_df, test_df = stratified_split(
        df, target_col="churn",
        train_size=0.70, val_size=0.15, test_size=0.15
    )

    print("Train shape:", train_df.shape)
    print("Val shape:", val_df.shape)
    print("Test shape:", test_df.shape)

    print("\nTrain churn %:")
    print(train_df["churn"].value_counts(normalize=True) * 100)
    print("\nVal churn %:")
    print(val_df["churn"].value_counts(normalize=True) * 100)
    print("\nTest churn %:")
    print(test_df["churn"].value_counts(normalize=True) * 100)

    train_df.to_csv("data/processed/train.csv", index=False)
    val_df.to_csv("data/processed/val.csv", index=False)
    test_df.to_csv("data/processed/test.csv", index=False)
    print("\ntrain/val/test splits saved to data/processed/")