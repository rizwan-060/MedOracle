"""UCI Heart Disease preprocessing pipeline.

Performs:
1. Cleaning of missing values in `ca` and `thal` (mode imputation).
2. Target binarization (target > 0 -> 1, target == 0 -> 0).
3. Feature standardization (z-score scaling for age, trestbps, chol, thalach, oldpeak).
4. Stratified 70/15/15 Train/Validation/Test split.
5. Export of processed splits and scaler metadata to `datasets/processed/heart/`.
"""

import csv
import json
import math
import random
from pathlib import Path
from typing import Any, Dict, List, Tuple

WORKSPACE_ROOT = Path(__file__).resolve().parents[4]
RAW_CSV = WORKSPACE_ROOT / "datasets" / "raw" / "heart_disease_uci.csv"
PROCESSED_DIR = WORKSPACE_ROOT / "datasets" / "processed" / "heart"

NUMERICAL_COLS = ["age", "trestbps", "chol", "thalach", "oldpeak"]
CATEGORICAL_COLS = ["sex", "cp", "fbs", "restecg", "exang", "slope", "ca", "thal"]
FEATURE_COLS = [
    "age", "sex", "cp", "trestbps", "chol", "fbs", "restecg",
    "thalach", "exang", "oldpeak", "slope", "ca", "thal"
]


def load_raw_heart_data(raw_path: Path = RAW_CSV) -> Tuple[List[str], List[Dict[str, Any]]]:
    """Load raw UCI Heart CSV and parse typed fields."""
    if not raw_path.exists():
        raise FileNotFoundError(f"Raw dataset not found at {raw_path}. Run download_datasets.py first.")

    records = []
    with open(raw_path, mode="r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            records.append(row)

    return reader.fieldnames or [], records


def preprocess_heart_records(
    records: List[Dict[str, Any]]
) -> Tuple[List[Dict[str, Any]], Dict[str, Any]]:
    """Clean missing values, binarize target, and fit scaler parameters."""
    # Step 1: Identify modes for ca and thal
    ca_vals = [r["ca"] for r in records if r["ca"] and r["ca"] != "?"]
    thal_vals = [r["thal"] for r in records if r["thal"] and r["thal"] != "?"]

    # Mode calculation
    mode_ca = max(set(ca_vals), key=ca_vals.count) if ca_vals else "0.0"
    mode_thal = max(set(thal_vals), key=thal_vals.count) if thal_vals else "3.0"

    cleaned_records = []
    for r in records:
        rec = {}
        # Clean ca and thal
        ca_val = float(mode_ca) if not r["ca"] or r["ca"] == "?" else float(r["ca"])
        thal_val = float(mode_thal) if not r["thal"] or r["thal"] == "?" else float(r["thal"])

        rec["age"] = float(r["age"])
        rec["sex"] = float(r["sex"])
        rec["cp"] = float(r["cp"])
        rec["trestbps"] = float(r["trestbps"])
        rec["chol"] = float(r["chol"])
        rec["fbs"] = float(r["fbs"])
        rec["restecg"] = float(r["restecg"])
        rec["thalach"] = float(r["thalach"])
        rec["exang"] = float(r["exang"])
        rec["oldpeak"] = float(r["oldpeak"])
        rec["slope"] = float(r["slope"])
        rec["ca"] = ca_val
        rec["thal"] = thal_val

        # Binarize target: 0 = healthy, >0 = heart disease
        raw_target = int(float(r["target"]))
        rec["target"] = 1 if raw_target > 0 else 0

        cleaned_records.append(rec)

    # Step 2: Compute mean and std for numerical features
    scaler_params = {}
    for col in NUMERICAL_COLS:
        vals = [r[col] for r in cleaned_records]
        mean_val = sum(vals) / len(vals)
        variance = sum((v - mean_val) ** 2 for v in vals) / len(vals)
        std_val = math.sqrt(variance) if variance > 1e-9 else 1.0
        scaler_params[col] = {"mean": round(mean_val, 4), "std": round(std_val, 4)}

    # Apply z-score scaling
    for r in cleaned_records:
        for col in NUMERICAL_COLS:
            m = scaler_params[col]["mean"]
            s = scaler_params[col]["std"]
            r[col] = round((r[col] - m) / s, 4)

    metadata = {
        "dataset": "UCI Heart Disease (Cleveland)",
        "total_instances": len(cleaned_records),
        "imputed_modes": {"ca": float(mode_ca), "thal": float(mode_thal)},
        "scaler_params": scaler_params,
        "feature_columns": FEATURE_COLS,
        "target_column": "target",
    }

    return cleaned_records, metadata


def split_stratified(
    records: List[Dict[str, Any]],
    target_key: str = "target",
    train_ratio: float = 0.70,
    val_ratio: float = 0.15,
    seed: int = 42,
) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]], List[Dict[str, Any]]]:
    """Perform deterministic stratified split into train, validation, and test subsets."""
    rng = random.Random(seed)

    # Group by class label
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

    # Final deterministic shuffle
    rng.shuffle(train_set)
    rng.shuffle(val_set)
    rng.shuffle(test_set)

    return train_set, val_set, test_set


def run_heart_preprocessing(
    raw_path: Path = RAW_CSV, output_dir: Path = PROCESSED_DIR
) -> Dict[str, Any]:
    """Execute complete heart disease preprocessing and write split files."""
    output_dir.mkdir(parents=True, exist_ok=True)
    _, records = load_raw_heart_data(raw_path)
    cleaned, metadata = preprocess_heart_records(records)
    train_data, val_data, test_data = split_stratified(cleaned, target_key="target")

    all_cols = FEATURE_COLS + ["target"]

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
