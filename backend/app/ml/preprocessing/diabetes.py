"""PIMA Indians Diabetes preprocessing pipeline.

Performs:
1. Imputation of physiologically impossible 0 values (Glucose, BloodPressure, SkinThickness,
   Insulin, BMI) using median values of non-zero observations.
2. Feature standardization (z-score scaling for continuous metabolic indicators).
3. Stratified 70/15/15 Train/Validation/Test split.
4. Export of processed splits and scaler metadata to `datasets/processed/diabetes/`.
"""

import csv
import json
import math
import random
from pathlib import Path
from typing import Any, Dict, List, Tuple

WORKSPACE_ROOT = Path(__file__).resolve().parents[4]
RAW_CSV = WORKSPACE_ROOT / "datasets" / "raw" / "diabetes_pima.csv"
PROCESSED_DIR = WORKSPACE_ROOT / "datasets" / "processed" / "diabetes"

IMPUTATION_COLS = ["Glucose", "BloodPressure", "SkinThickness", "Insulin", "BMI"]
FEATURE_COLS = [
    "Pregnancies", "Glucose", "BloodPressure", "SkinThickness",
    "Insulin", "BMI", "DiabetesPedigreeFunction", "Age"
]
TARGET_COL = "Outcome"


def _compute_median(values: List[float]) -> float:
    """Compute mathematical median of a list of floats."""
    if not values:
        return 0.0
    sorted_vals = sorted(values)
    n = len(sorted_vals)
    mid = n // 2
    if n % 2 == 1:
        return sorted_vals[mid]
    return (sorted_vals[mid - 1] + sorted_vals[mid]) / 2.0


def load_raw_diabetes_data(raw_path: Path = RAW_CSV) -> Tuple[List[str], List[Dict[str, Any]]]:
    """Load raw PIMA Diabetes CSV."""
    if not raw_path.exists():
        raise FileNotFoundError(f"Raw dataset not found at {raw_path}. Run download_datasets.py first.")

    records = []
    with open(raw_path, mode="r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            records.append(row)

    return reader.fieldnames or [], records


def preprocess_diabetes_records(
    records: List[Dict[str, Any]]
) -> Tuple[List[Dict[str, Any]], Dict[str, Any]]:
    """Impute biologically impossible zeroes and calculate feature scaling parameters."""
    # Step 1: Calculate medians for features where 0 represents missingness
    feature_medians: Dict[str, float] = {}
    for col in IMPUTATION_COLS:
        non_zero_vals = [float(r[col]) for r in records if float(r[col]) > 0.0]
        feature_medians[col] = round(_compute_median(non_zero_vals), 2)

    cleaned_records = []
    for r in records:
        rec = {}
        for col in FEATURE_COLS:
            val = float(r[col])
            # If feature is in imputation list and value is 0, replace with median
            if col in IMPUTATION_COLS and val == 0.0:
                val = feature_medians[col]
            rec[col] = val

        rec[TARGET_COL] = int(float(r[TARGET_COL]))
        cleaned_records.append(rec)

    # Step 2: Compute mean and std for continuous feature normalization
    scaler_params = {}
    for col in FEATURE_COLS:
        vals = [r[col] for r in cleaned_records]
        mean_val = sum(vals) / len(vals)
        variance = sum((v - mean_val) ** 2 for v in vals) / len(vals)
        std_val = math.sqrt(variance) if variance > 1e-9 else 1.0
        scaler_params[col] = {"mean": round(mean_val, 4), "std": round(std_val, 4)}

    # Apply z-score scaling
    for r in cleaned_records:
        for col in FEATURE_COLS:
            m = scaler_params[col]["mean"]
            s = scaler_params[col]["std"]
            r[col] = round((r[col] - m) / s, 4)

    metadata = {
        "dataset": "PIMA Indians Diabetes (NIDDK)",
        "total_instances": len(cleaned_records),
        "imputed_medians": feature_medians,
        "scaler_params": scaler_params,
        "feature_columns": FEATURE_COLS,
        "target_column": TARGET_COL,
    }

    return cleaned_records, metadata


def split_stratified(
    records: List[Dict[str, Any]],
    target_key: str = TARGET_COL,
    train_ratio: float = 0.70,
    val_ratio: float = 0.15,
    seed: int = 42,
) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]], List[Dict[str, Any]]]:
    """Perform deterministic stratified split."""
    rng = random.Random(seed)
    class_buckets: Dict[Any, List[Dict[str, Any]]] = {}
    for r in records:
        label = r[target_key]
        class_buckets.setdefault(label, []).append(r)

    train_set, val_set, test_set = [], [], []
    for label, items in class_buckets.items():
        shuffled = list(items)
        rng.shuffle(shuffled)
        n = len(shuffled)
        n_train = int(n * train_ratio)
        n_val = int(n * val_ratio)

        train_set.extend(shuffled[:n_train])
        val_set.extend(shuffled[n_train : n_train + n_val])
        test_set.extend(shuffled[n_train + n_val :])

    rng.shuffle(train_set)
    rng.shuffle(val_set)
    rng.shuffle(test_set)

    return train_set, val_set, test_set


def run_diabetes_preprocessing(
    raw_path: Path = RAW_CSV, output_dir: Path = PROCESSED_DIR
) -> Dict[str, Any]:
    """Execute complete diabetes preprocessing and write split files."""
    output_dir.mkdir(parents=True, exist_ok=True)
    _, records = load_raw_diabetes_data(raw_path)
    cleaned, metadata = preprocess_diabetes_records(records)
    train_data, val_data, test_data = split_stratified(cleaned, target_key=TARGET_COL)

    all_cols = FEATURE_COLS + [TARGET_COL]

    for name, subset in [("train", train_data), ("val", val_data), ("test", test_data)]:
        file_path = output_dir / f"{name}.csv"
        with open(file_path, mode="w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=all_cols)
            writer.writeheader()
            writer.writerows(subset)

    metadata["split_counts"] = {
        "train": len(train_data),
        "val": len(val_data),
        "test": len(test_data),
    }

    meta_file = output_dir / "metadata.json"
    with open(meta_file, mode="w", encoding="utf-8") as f:
        json.dump(metadata, f, indent=2)

    return metadata
