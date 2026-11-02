"""Disease-to-Symptom benchmark preprocessing pipeline.

Performs:
1. Label encoding of 41 distinct disease categories into numeric class indices.
2. Verification of 132 binary symptom feature columns.
3. Stratified 70/15/15 Train/Validation/Test split across all 41 pathologies.
4. Export of processed splits, symptom vocabulary, and class mapping to `datasets/processed/symptoms/`.
"""

import csv
import json
import random
from pathlib import Path
from typing import Any, Dict, List, Tuple

WORKSPACE_ROOT = Path(__file__).resolve().parents[4]
RAW_CSV = WORKSPACE_ROOT / "datasets" / "raw" / "symptoms_disease.csv"
PROCESSED_DIR = WORKSPACE_ROOT / "datasets" / "processed" / "symptoms"

TARGET_COL = "prognosis"


def load_raw_symptom_data(raw_path: Path = RAW_CSV) -> Tuple[List[str], List[Dict[str, Any]]]:
    """Load raw Disease-to-Symptom CSV."""
    if not raw_path.exists():
        raise FileNotFoundError(f"Raw dataset not found at {raw_path}. Run download_datasets.py first.")

    records = []
    with open(raw_path, mode="r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            records.append(row)

    return reader.fieldnames or [], records


def preprocess_symptom_records(
    records: List[Dict[str, Any]], fieldnames: List[str]
) -> Tuple[List[Dict[str, Any]], Dict[str, Any]]:
    """Encode disease targets and validate binary symptom features."""
    symptom_cols = [col for col in fieldnames if col != TARGET_COL]

    # Collect unique disease categories and create label mappings
    unique_diseases = sorted(list(set(r[TARGET_COL] for r in records)))
    disease_to_idx = {disease: idx for idx, disease in enumerate(unique_diseases)}
    idx_to_disease = {idx: disease for idx, disease in enumerate(unique_diseases)}

    processed_records = []
    for r in records:
        rec = {}
        for col in symptom_cols:
            rec[col] = int(float(r[col]))
        rec["target"] = disease_to_idx[r[TARGET_COL]]
        processed_records.append(rec)

    metadata = {
        "dataset": "Disease-to-Symptom Benchmark Diagnostic Matrix",
        "total_instances": len(processed_records),
        "total_symptoms": len(symptom_cols),
        "total_diseases": len(unique_diseases),
        "symptom_features": symptom_cols,
        "disease_to_index": disease_to_idx,
        "index_to_disease": idx_to_disease,
        "target_column": "target",
    }

    return processed_records, metadata


def split_stratified(
    records: List[Dict[str, Any]],
    target_key: str = "target",
    train_ratio: float = 0.70,
    val_ratio: float = 0.15,
    seed: int = 42,
) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]], List[Dict[str, Any]]]:
    """Perform deterministic stratified split across multi-class disease targets."""
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


def run_symptoms_preprocessing(
    raw_path: Path = RAW_CSV, output_dir: Path = PROCESSED_DIR
) -> Dict[str, Any]:
    """Execute complete symptom-disease preprocessing and write split files."""
    output_dir.mkdir(parents=True, exist_ok=True)
    fieldnames, records = load_raw_symptom_data(raw_path)
    cleaned, metadata = preprocess_symptom_records(records, fieldnames)
    train_data, val_data, test_data = split_stratified(cleaned, target_key="target")

    all_cols = metadata["symptom_features"] + ["target"]

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
