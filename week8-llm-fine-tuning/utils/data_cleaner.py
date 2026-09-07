from pathlib import Path
import json
import re
import random

import matplotlib.pyplot as plt
import numpy as np
from transformers import AutoTokenizer


# ---------------------------------------------------------
# PATH CONFIGURATION
# ---------------------------------------------------------

BASE_DIR = Path(__file__).resolve().parents[1]

RAW_DATA_PATH = (
    BASE_DIR
    / "data"
    / "raw"
    / "coding_instruction_dataset_1200.jsonl"
)

TRAIN_DATA_PATH = (
    BASE_DIR
    / "data"
    / "train.jsonl"
)

VAL_DATA_PATH = (
    BASE_DIR
    / "data"
    / "val.jsonl"
)

OUTLIER_DATA_PATH = (
    BASE_DIR
    / "data"
    / "outliers.jsonl"
)

REPORTS_DIR = (
    BASE_DIR
    / "reports"
)

TOKEN_DISTRIBUTION_PATH = (
    REPORTS_DIR
    / "token_length_distribution.png"
)


# ---------------------------------------------------------
# MODEL CONFIGURATION
# ---------------------------------------------------------

MODEL_NAME = "Qwen/Qwen2.5-1.5B-Instruct"


# ---------------------------------------------------------
# TRAIN / VALIDATION CONFIGURATION
# ---------------------------------------------------------

VALIDATION_RATIO = 0.10

RANDOM_SEED = 42


# ---------------------------------------------------------
# LOAD JSONL DATASET
# ---------------------------------------------------------

def load_jsonl(file_path):
    """
    Loads a JSONL file line by line.

    Each line should contain one valid JSON object.
    """

    records = []

    invalid_json_count = 0

    with open(
        file_path,
        "r",
        encoding="utf-8",
    ) as file:

        for line_number, line in enumerate(
            file,
            start=1,
        ):

            line = line.strip()

            # Skip empty lines
            if not line:
                continue

            try:

                record = json.loads(
                    line
                )

                records.append(
                    record
                )

            except json.JSONDecodeError as error:

                invalid_json_count += 1

                print(
                    f"Invalid JSON at line "
                    f"{line_number}: {error}"
                )

    return records, invalid_json_count


# ---------------------------------------------------------
# VALIDATE REQUIRED FIELDS
# ---------------------------------------------------------

def validate_records(records):
    """
    Checks that every record:

    - is a JSON object
    - contains instruction
    - contains input
    - contains output
    """

    required_fields = {
        "instruction",
        "input",
        "output",
    }

    valid_records = []

    invalid_records = []

    for index, record in enumerate(
        records
    ):

        # ---------------------------------------------
        # CHECK RECORD TYPE
        # ---------------------------------------------

        if not isinstance(
            record,
            dict,
        ):

            invalid_records.append(
                {
                    "index": index,
                    "reason": (
                        "Record is not a JSON object"
                    ),
                    "record": record,
                }
            )

            continue


        # ---------------------------------------------
        # CHECK REQUIRED FIELDS
        # ---------------------------------------------

        record_fields = set(
            record.keys()
        )

        if not required_fields.issubset(
            record_fields
        ):

            invalid_records.append(
                {
                    "index": index,
                    "reason": (
                        "Missing required field"
                    ),
                    "record": record,
                }
            )

            continue


        valid_records.append(
            record
        )

    return (
        valid_records,
        invalid_records,
    )


# ---------------------------------------------------------
# CLEAN TEXT
# ---------------------------------------------------------

def clean_text(text):
    """
    Cleans textual content.

    Operations:

    - Remove leading spaces
    - Remove trailing spaces
    - Replace repeated whitespace
    - Remove unnecessary newlines
    - Remove unnecessary tabs
    """

    text = text.strip()

    text = re.sub(
        r"\s+",
        " ",
        text,
    )

    return text


# ---------------------------------------------------------
# CLEAN RECORDS
# ---------------------------------------------------------

def clean_records(records):
    """
    Cleans instruction, input and output.

    Rejects records where:

    - any field is not a string
    - instruction is empty
    - output is empty

    Input is allowed to be empty.
    """

    cleaned_records = []

    rejected_records = []

    for index, record in enumerate(
        records
    ):

        instruction = record[
            "instruction"
        ]

        input_text = record[
            "input"
        ]

        output = record[
            "output"
        ]


        # ---------------------------------------------
        # CHECK DATA TYPES
        # ---------------------------------------------

        if not all(
            isinstance(value, str)
            for value in [
                instruction,
                input_text,
                output,
            ]
        ):

            rejected_records.append(
                {
                    "index": index,
                    "reason": (
                        "Non-string field detected"
                    ),
                    "record": record,
                }
            )

            continue


        # ---------------------------------------------
        # CLEAN TEXT
        # ---------------------------------------------

        instruction = clean_text(
            instruction
        )

        input_text = clean_text(
            input_text
        )

        output = clean_text(
            output
        )


        # ---------------------------------------------
        # EMPTY INSTRUCTION CHECK
        # ---------------------------------------------

        if not instruction:

            rejected_records.append(
                {
                    "index": index,
                    "reason": (
                        "Empty instruction"
                    ),
                    "record": record,
                }
            )

            continue


        # ---------------------------------------------
        # EMPTY OUTPUT CHECK
        # ---------------------------------------------

        if not output:

            rejected_records.append(
                {
                    "index": index,
                    "reason": (
                        "Empty output"
                    ),
                    "record": record,
                }
            )

            continue


        # ---------------------------------------------
        # CREATE CLEAN RECORD
        # ---------------------------------------------

        cleaned_record = {
            "instruction": instruction,
            "input": input_text,
            "output": output,
        }

        cleaned_records.append(
            cleaned_record
        )

    return (
        cleaned_records,
        rejected_records,
    )


# ---------------------------------------------------------
# REMOVE DUPLICATES
# ---------------------------------------------------------

def remove_duplicates(records):
    """
    Removes exact duplicate records.

    A duplicate means:

    instruction
    input
    output

    are all exactly identical.
    """

    unique_records = []

    seen = set()

    duplicate_count = 0

    for record in records:

        key = (
            record["instruction"],
            record["input"],
            record["output"],
        )

        if key in seen:

            duplicate_count += 1

            continue

        seen.add(
            key
        )

        unique_records.append(
            record
        )

    return (
        unique_records,
        duplicate_count,
    )


# ---------------------------------------------------------
# LOAD TOKENIZER
# ---------------------------------------------------------

def load_tokenizer():
    """
    Loads the tokenizer for the model that will
    later be fine-tuned.

    Token analysis should ideally use the same
    tokenizer as the Day 2 model.
    """

    print(
        "\nLoading tokenizer..."
    )

    tokenizer = AutoTokenizer.from_pretrained(
        MODEL_NAME
    )

    print(
        f"Tokenizer loaded successfully: "
        f"{MODEL_NAME}"
    )

    return tokenizer


# ---------------------------------------------------------
# BUILD TRAINING TEXT
# ---------------------------------------------------------

def build_training_text(record):
    """
    Converts an instruction-tuning record into
    a single text sequence for token counting.
    """

    instruction = record[
        "instruction"
    ]

    input_text = record[
        "input"
    ]

    output = record[
        "output"
    ]


    if input_text:

        text = (
            f"Instruction: {instruction}\n"
            f"Input: {input_text}\n"
            f"Output: {output}"
        )

    else:

        text = (
            f"Instruction: {instruction}\n"
            f"Output: {output}"
        )

    return text


# ---------------------------------------------------------
# CALCULATE TOKEN LENGTHS
# ---------------------------------------------------------

def calculate_token_lengths(
    records,
    tokenizer,
):
    """
    Calculates token length for every record.
    """

    token_lengths = []

    for record in records:

        training_text = build_training_text(
            record
        )

        token_ids = tokenizer.encode(
            training_text,
            add_special_tokens=True,
        )

        token_length = len(
            token_ids
        )

        token_lengths.append(
            token_length
        )

    return token_lengths


# ---------------------------------------------------------
# TOKEN STATISTICS
# ---------------------------------------------------------

def calculate_token_statistics(
    token_lengths,
):
    """
    Calculates token-length statistics.
    """

    if not token_lengths:
        return {}

    lengths = np.array(
        token_lengths
    )

    statistics = {
        "count": len(lengths),
        "minimum": int(
            np.min(lengths)
        ),
        "maximum": int(
            np.max(lengths)
        ),
        "average": float(
            np.mean(lengths)
        ),
        "median": float(
            np.median(lengths)
        ),
        "q1": float(
            np.percentile(
                lengths,
                25,
            )
        ),
        "q3": float(
            np.percentile(
                lengths,
                75,
            )
        ),
    }

    return statistics


# ---------------------------------------------------------
# PRINT TOKEN STATISTICS
# ---------------------------------------------------------

def print_token_statistics(
    statistics,
):
    """
    Prints token-length statistics.
    """

    if not statistics:

        print(
            "No token statistics available."
        )

        return


    print(
        "\nToken Length Statistics"
    )

    print(
        f"Samples analyzed: "
        f"{statistics['count']}"
    )

    print(
        f"Minimum tokens: "
        f"{statistics['minimum']}"
    )

    print(
        f"Maximum tokens: "
        f"{statistics['maximum']}"
    )

    print(
        f"Average tokens: "
        f"{statistics['average']:.2f}"
    )

    print(
        f"Median tokens: "
        f"{statistics['median']:.2f}"
    )

    print(
        f"Q1: "
        f"{statistics['q1']:.2f}"
    )

    print(
        f"Q3: "
        f"{statistics['q3']:.2f}"
    )


# ---------------------------------------------------------
# PLOT TOKEN DISTRIBUTION
# ---------------------------------------------------------

def plot_token_distribution(
    token_lengths,
):
    """
    Creates a histogram showing token-length
    distribution across the dataset.
    """

    REPORTS_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    plt.figure(
        figsize=(10, 6)
    )

    plt.hist(
        token_lengths,
        bins=20,
        edgecolor="black",
    )

    plt.title(
        "Token Length Distribution"
    )

    plt.xlabel(
        "Number of Tokens"
    )

    plt.ylabel(
        "Number of Samples"
    )

    plt.grid(
        axis="y",
        alpha=0.3,
    )

    plt.tight_layout()

    plt.savefig(
        TOKEN_DISTRIBUTION_PATH,
        dpi=300,
    )

    plt.close()

    print(
        "\nToken distribution graph saved:"
    )

    print(
        TOKEN_DISTRIBUTION_PATH
    )


# ---------------------------------------------------------
# DETECT AND REMOVE OUTLIERS
# ---------------------------------------------------------

def remove_token_outliers(
    records,
    token_lengths,
):
    """
    Detects token-length outliers using
    the IQR method.

    Formula:

    IQR = Q3 - Q1

    Lower Bound =
    Q1 - 1.5 * IQR

    Upper Bound =
    Q3 + 1.5 * IQR
    """

    lengths_array = np.array(
        token_lengths
    )

    q1 = np.percentile(
        lengths_array,
        25,
    )

    q3 = np.percentile(
        lengths_array,
        75,
    )

    iqr = q3 - q1

    lower_bound = (
        q1
        - 1.5 * iqr
    )

    upper_bound = (
        q3
        + 1.5 * iqr
    )


    filtered_records = []

    filtered_lengths = []

    outlier_records = []


    for record, token_length in zip(
        records,
        token_lengths,
    ):

        is_outlier = (
            token_length < lower_bound
            or
            token_length > upper_bound
        )


        if is_outlier:

            outlier_records.append(
                {
                    "instruction": (
                        record["instruction"]
                    ),
                    "input": (
                        record["input"]
                    ),
                    "output": (
                        record["output"]
                    ),
                    "token_length": (
                        token_length
                    ),
                }
            )

        else:

            filtered_records.append(
                record
            )

            filtered_lengths.append(
                token_length
            )


    statistics = {
        "q1": float(q1),
        "q3": float(q3),
        "iqr": float(iqr),
        "lower_bound": float(
            lower_bound
        ),
        "upper_bound": float(
            upper_bound
        ),
    }


    return (
        filtered_records,
        filtered_lengths,
        outlier_records,
        statistics,
    )


# ---------------------------------------------------------
# SPLIT TRAIN AND VALIDATION DATA
# ---------------------------------------------------------

def split_dataset(
    records,
    validation_ratio=VALIDATION_RATIO,
    random_seed=RANDOM_SEED,
):
    """
    Splits the cleaned dataset into:

    training data
    validation data

    Default split:

    90% train
    10% validation
    """

    shuffled_records = records.copy()

    random.seed(
        random_seed
    )

    random.shuffle(
        shuffled_records
    )

    validation_size = int(
        len(shuffled_records)
        * validation_ratio
    )


    validation_records = (
        shuffled_records[
            :validation_size
        ]
    )

    train_records = (
        shuffled_records[
            validation_size:
        ]
    )


    return (
        train_records,
        validation_records,
    )


# ---------------------------------------------------------
# SAVE JSONL FILE
# ---------------------------------------------------------

def save_jsonl(
    records,
    file_path,
):
    """
    Saves records into JSONL format.
    """

    file_path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    with open(
        file_path,
        "w",
        encoding="utf-8",
    ) as file:

        for record in records:

            json_line = json.dumps(
                record,
                ensure_ascii=False,
            )

            file.write(
                json_line + "\n"
            )


# ---------------------------------------------------------
# MAIN PIPELINE
# ---------------------------------------------------------

def main():

    print(
        "\n======================================"
    )

    print(
        "WEEK 8 - DAY 1 DATASET PIPELINE"
    )

    print(
        "======================================"
    )


    # -----------------------------------------------------
    # STEP 1: LOAD DATA
    # -----------------------------------------------------

    print(
        "\n[STEP 1] Loading dataset..."
    )

    records, invalid_json_count = load_jsonl(
        RAW_DATA_PATH
    )

    print(
        f"Total records loaded: "
        f"{len(records)}"
    )

    print(
        f"Invalid JSON lines: "
        f"{invalid_json_count}"
    )


    # -----------------------------------------------------
    # STEP 2: VALIDATE RECORDS
    # -----------------------------------------------------

    print(
        "\n[STEP 2] Validating records..."
    )

    (
        valid_records,
        invalid_records,
    ) = validate_records(
        records
    )

    print(
        f"Valid records: "
        f"{len(valid_records)}"
    )

    print(
        f"Invalid records: "
        f"{len(invalid_records)}"
    )


    # -----------------------------------------------------
    # STEP 3: CLEAN RECORDS
    # -----------------------------------------------------

    print(
        "\n[STEP 3] Cleaning records..."
    )

    (
        cleaned_records,
        rejected_records,
    ) = clean_records(
        valid_records
    )

    print(
        f"Records after cleaning: "
        f"{len(cleaned_records)}"
    )

    print(
        f"Rejected during cleaning: "
        f"{len(rejected_records)}"
    )


    # -----------------------------------------------------
    # STEP 4: REMOVE DUPLICATES
    # -----------------------------------------------------

    print(
        "\n[STEP 4] Removing duplicates..."
    )

    (
        unique_records,
        duplicate_count,
    ) = remove_duplicates(
        cleaned_records
    )

    print(
        f"Duplicates removed: "
        f"{duplicate_count}"
    )

    print(
        f"Unique records: "
        f"{len(unique_records)}"
    )


    # -----------------------------------------------------
    # STEP 5: LOAD TOKENIZER
    # -----------------------------------------------------

    print(
        "\n[STEP 5] Preparing tokenizer..."
    )

    tokenizer = load_tokenizer()


    # -----------------------------------------------------
    # STEP 6: TOKEN ANALYSIS
    # -----------------------------------------------------

    print(
        "\n[STEP 6] Analyzing token lengths..."
    )

    token_lengths = calculate_token_lengths(
        unique_records,
        tokenizer,
    )

    token_statistics = (
        calculate_token_statistics(
            token_lengths
        )
    )

    print_token_statistics(
        token_statistics
    )


    # -----------------------------------------------------
    # STEP 7: DISTRIBUTION GRAPH
    # -----------------------------------------------------

    print(
        "\n[STEP 7] Creating distribution graph..."
    )

    plot_token_distribution(
        token_lengths
    )


    # -----------------------------------------------------
    # STEP 8: OUTLIER DETECTION
    # -----------------------------------------------------

    print(
        "\n[STEP 8] Detecting token outliers..."
    )

    (
        filtered_records,
        filtered_token_lengths,
        outlier_records,
        outlier_statistics,
    ) = remove_token_outliers(
        unique_records,
        token_lengths,
    )


    print(
        f"Q1: "
        f"{outlier_statistics['q1']:.2f}"
    )

    print(
        f"Q3: "
        f"{outlier_statistics['q3']:.2f}"
    )

    print(
        f"IQR: "
        f"{outlier_statistics['iqr']:.2f}"
    )

    print(
        f"Lower bound: "
        f"{outlier_statistics['lower_bound']:.2f}"
    )

    print(
        f"Upper bound: "
        f"{outlier_statistics['upper_bound']:.2f}"
    )

    print(
        f"Outliers detected: "
        f"{len(outlier_records)}"
    )

    print(
        f"Records after outlier removal: "
        f"{len(filtered_records)}"
    )


    # -----------------------------------------------------
    # SAVE OUTLIERS
    # -----------------------------------------------------

    if outlier_records:

        save_jsonl(
            outlier_records,
            OUTLIER_DATA_PATH,
        )

        print(
            f"Outlier records saved to: "
            f"{OUTLIER_DATA_PATH}"
        )


    # -----------------------------------------------------
    # STEP 9: TRAIN / VALIDATION SPLIT
    # -----------------------------------------------------

    print(
        "\n[STEP 9] Creating train/validation split..."
    )

    (
        train_records,
        validation_records,
    ) = split_dataset(
        filtered_records
    )


    print(
        f"Training samples: "
        f"{len(train_records)}"
    )

    print(
        f"Validation samples: "
        f"{len(validation_records)}"
    )


    # -----------------------------------------------------
    # STEP 10: SAVE DATASETS
    # -----------------------------------------------------

    print(
        "\n[STEP 10] Saving final datasets..."
    )

    save_jsonl(
        train_records,
        TRAIN_DATA_PATH,
    )

    save_jsonl(
        validation_records,
        VAL_DATA_PATH,
    )


    print(
        f"Training dataset saved:"
        f"\n{TRAIN_DATA_PATH}"
    )

    print(
        f"\nValidation dataset saved:"
        f"\n{VAL_DATA_PATH}"
    )


    # -----------------------------------------------------
    # FINAL SUMMARY
    # -----------------------------------------------------

    print(
        "\n======================================"
    )

    print(
        "DAY 1 DATASET PIPELINE COMPLETED"
    )

    print(
        "======================================"
    )

    print(
        f"\nRaw records: "
        f"{len(records)}"
    )

    print(
        f"Invalid JSON: "
        f"{invalid_json_count}"
    )

    print(
        f"Invalid records: "
        f"{len(invalid_records)}"
    )

    print(
        f"Rejected during cleaning: "
        f"{len(rejected_records)}"
    )

    print(
        f"Duplicates removed: "
        f"{duplicate_count}"
    )

    print(
        f"Outliers removed: "
        f"{len(outlier_records)}"
    )

    print(
        f"Final usable samples: "
        f"{len(filtered_records)}"
    )

    print(
        f"Train samples: "
        f"{len(train_records)}"
    )

    print(
        f"Validation samples: "
        f"{len(validation_records)}"
    )

    print(
        "\nGenerated files:"
    )

    print(
        f"1. {TRAIN_DATA_PATH}"
    )

    print(
        f"2. {VAL_DATA_PATH}"
    )

    print(
        f"3. {TOKEN_DISTRIBUTION_PATH}"
    )

    if outlier_records:

        print(
            f"4. {OUTLIER_DATA_PATH}"
        )


# ---------------------------------------------------------
# ENTRY POINT
# ---------------------------------------------------------

if __name__ == "__main__":
    main()