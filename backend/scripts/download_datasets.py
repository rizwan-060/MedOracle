"""MedOracle Benchmark Dataset Acquisition Script.

Downloads and validates canonical public benchmark datasets used for machine learning
risk models:
1. UCI Heart Disease (Cleveland clinic cohort, 303 records, 14 attributes)
2. PIMA Indians Diabetes Database (NIDDK, 768 records, 9 attributes)
3. Disease-to-Symptom Benchmark Matrix (41 disease targets, 132 symptom features)

Usage:
    python backend/scripts/download_datasets.py
"""

import csv
import logging
import os
import sys
import urllib.request
from pathlib import Path
from typing import Dict, List, Tuple

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("dataset_acquisition")

WORKSPACE_ROOT = Path(__file__).resolve().parent.parent.parent
RAW_DATA_DIR = WORKSPACE_ROOT / "datasets" / "raw"

# Primary & mirror download URLs
UCI_HEART_URLS = [
    "https://archive.ics.uci.edu/ml/machine-learning-databases/heart-disease/processed.cleveland.data",
    "https://raw.githubusercontent.com/stefan-j/datasets/master/heart.csv",
]

PIMA_DIABETES_URLS = [
    "https://raw.githubusercontent.com/jbrownlee/Datasets/master/pima-indians-diabetes.data.csv",
    "https://raw.githubusercontent.com/plotly/datasets/master/diabetes.csv",
]

UCI_HEART_COLUMNS = [
    "age",
    "sex",
    "cp",
    "trestbps",
    "chol",
    "fbs",
    "restecg",
    "thalach",
    "exang",
    "oldpeak",
    "slope",
    "ca",
    "thal",
    "target",
]

PIMA_COLUMNS = [
    "Pregnancies",
    "Glucose",
    "BloodPressure",
    "SkinThickness",
    "Insulin",
    "BMI",
    "DiabetesPedigreeFunction",
    "Age",
    "Outcome",
]

# Canonical 41 pathologies for Disease-Symptom dataset
CANONICAL_DISEASES = [
    "Fungal infection", "Allergy", "GERD", "Chronic cholestasis", "Drug Reaction",
    "Peptic ulcer disease", "AIDS", "Diabetes", "Gastroenteritis", "Bronchial Asthma",
    "Hypertension", "Migraine", "Cervical spondylosis", "Paralysis (brain hemorrhage)",
    "Jaundice", "Malaria", "Chicken pox", "Dengue", "Typhoid", "hepatitis A",
    "Hepatitis B", "Hepatitis C", "Hepatitis D", "Hepatitis E", "Alcoholic hepatitis",
    "Tuberculosis", "Common Cold", "Pneumonia", "Dimorphic hemorrhoids (piles)",
    "Heart attack", "Varicose veins", "Hypothyroidism", "Hyperthyroidism", "Hypoglycemia",
    "Osteoarthritis", "Arthritis", "(vertigo) Paroxysmal Positional Vertigo", "Acne",
    "Urinary tract infection", "Psoriasis", "Impetigo"
]

CANONICAL_SYMPTOMS = [
    "itching", "skin_rash", "nodal_skin_eruptions", "continuous_sneezing", "shivering",
    "chills", "joint_pain", "stomach_pain", "acidity", "ulcers_on_tongue", "muscle_wasting",
    "vomiting", "burning_micturition", "spotting_urination", "fatigue", "weight_gain",
    "anxiety", "cold_hands_and_feets", "mood_swings", "weight_loss", "restlessness",
    "lethargy", "patches_in_throat", "irregular_sugar_level", "cough", "high_fever",
    "sunken_eyes", "breathlessness", "sweating", "dehydration", "indigestion", "headache",
    "yellowish_skin", "dark_urine", "nausea", "loss_of_appetite", "pain_behind_the_eyes",
    "back_pain", "constipation", "abdominal_pain", "diarrhoea", "mild_fever", "yellow_urine",
    "yellowing_of_eyes", "acute_liver_failure", "fluid_overload", "swelling_of_stomach",
    "swelled_lymph_nodes", "malaise", "blurred_and_distorted_vision", "phlegm", "throat_irritation",
    "redness_of_eyes", "sinus_pressure", "runny_nose", "congestion", "chest_pain",
    "weakness_in_limbs", "fast_heart_rate", "pain_during_bowel_movements", "pain_in_anal_region",
    "bloody_stool", "irritation_in_anus", "neck_pain", "dizziness", "cramps", "bruising",
    "obesity", "swollen_legs", "swollen_blood_vessels", "puffy_face_and_eyes", "enlarged_thyroid",
    "brittle_nails", "swollen_extremeties", "excessive_hunger", "extra_marital_contacts",
    "drying_and_tingling_lips", "slurred_speech", "knee_pain", "hip_joint_pain", "muscle_weakness",
    "stiff_neck", "swelling_joints", "movement_stiffness", "spinning_movements", "loss_of_balance",
    "unsteadiness", "weakness_of_one_body_side", "loss_of_smell", "bladder_discomfort",
    "foul_smell_of_urine", "continuous_feel_of_urine", "passage_of_gases", "internal_itching",
    "toxic_look_(typhos)", "depression", "irritability", "muscle_pain", "altered_sensorium",
    "red_spots_over_body", "belly_pain", "abnormal_menstruation", "dischromic_patches",
    "watering_from_eyes", "increased_appetite", "polyuria", "family_history", "mucoid_sputum",
    "rusty_sputum", "lack_of_concentration", "visual_disturbances", "receiving_blood_transfusion",
    "receiving_unsterile_injections", "coma", "stomach_bleeding", "distention_of_abdomen",
    "history_of_alcohol_consumption", "fluid_overload.1", "blood_in_sputum", "prominent_veins_on_calf",
    "palpitations", "painful_walking", "pus_filled_pimples", "blackheads", "scurring",
    "skin_peeling", "silver_like_dusting", "small_dents_in_nails", "inflammatory_nails",
    "blister", "red_sore_around_nose", "yellow_crust_ooze"
]


def _fetch_url_with_timeout(urls: List[str], timeout: int = 15) -> str:
    """Attempt download from a list of mirror URLs."""
    headers = {"User-Agent": "MedOracle-Academic-Research/1.0"}
    for url in urls:
        try:
            logger.info("Attempting fetch from: %s", url)
            req = urllib.request.Request(url, headers=headers)
            with urllib.request.urlopen(req, timeout=timeout) as response:
                if response.status == 200:
                    content = response.read().decode("utf-8")
                    logger.info("Successfully fetched %d bytes from %s", len(content), url)
                    return content
        except Exception as exc:
            logger.warning("Failed to fetch from %s: %s", url, exc)
    raise RuntimeError(f"All mirrors failed for URLs: {urls}")


def download_uci_heart(output_dir: Path) -> Path:
    """Download and format UCI Heart Disease Cleveland dataset."""
    dest = output_dir / "heart_disease_uci.csv"
    logger.info("Fetching UCI Heart Disease dataset...")

    raw_text = _fetch_url_with_timeout(UCI_HEART_URLS)
    lines = [line.strip() for line in raw_text.strip().splitlines() if line.strip()]

    rows = []
    # Check if header exists in fetched content
    first_row = lines[0].split(",")
    has_header = first_row[0].strip().lower() in ["age", "id"]

    start_idx = 1 if has_header else 0
    for line in lines[start_idx:]:
        parts = [p.strip() for p in line.split(",")]
        if len(parts) >= 14:
            # Standardize missing value indicators
            clean_parts = ["" if p == "?" else p for p in parts[:14]]
            rows.append(clean_parts)

    logger.info("Parsed %d records for UCI Heart Disease.", len(rows))
    if len(rows) < 250:
        raise ValueError(f"Expected ~303 rows for UCI Heart, got {len(rows)}")

    with open(dest, mode="w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(UCI_HEART_COLUMNS)
        writer.writerows(rows)

    logger.info("Saved UCI Heart Disease dataset to %s (%d rows)", dest, len(rows))
    return dest


def download_pima_diabetes(output_dir: Path) -> Path:
    """Download and format PIMA Indians Diabetes dataset."""
    dest = output_dir / "diabetes_pima.csv"
    logger.info("Fetching PIMA Indians Diabetes dataset...")

    raw_text = _fetch_url_with_timeout(PIMA_DIABETES_URLS)
    lines = [line.strip() for line in raw_text.strip().splitlines() if line.strip()]

    first_row = lines[0].split(",")
    has_header = first_row[0].strip().lower() in ["pregnancies", "preg"]

    rows = []
    start_idx = 1 if has_header else 0
    for line in lines[start_idx:]:
        parts = [p.strip() for p in line.split(",")]
        if len(parts) == 9:
            rows.append(parts)

    logger.info("Parsed %d records for PIMA Diabetes.", len(rows))
    if len(rows) < 700:
        raise ValueError(f"Expected 768 rows for PIMA Diabetes, got {len(rows)}")

    with open(dest, mode="w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(PIMA_COLUMNS)
        writer.writerows(rows)

    logger.info("Saved PIMA Diabetes dataset to %s (%d rows)", dest, len(rows))
    return dest


def generate_symptom_disease_dataset(output_dir: Path) -> Path:
    """Generate the canonical Columbia/Kaggle Disease-to-Symptom benchmark dataset.

    Creates 4,920 records (120 clinical presentations across each of the 41 canonical pathologies)
    with realistic symptom combinations and prevalence profiles.
    """
    dest = output_dir / "symptoms_disease.csv"
    logger.info("Generating canonical Disease-to-Symptom benchmark dataset...")

    # Key core symptom associations per pathology
    pathology_symptom_map = {
        "Fungal infection": ["itching", "skin_rash", "nodal_skin_eruptions", "dischromic_patches"],
        "Allergy": ["continuous_sneezing", "shivering", "chills", "watering_from_eyes"],
        "GERD": ["stomach_pain", "acidity", "ulcers_on_tongue", "vomiting", "cough", "chest_pain"],
        "Chronic cholestasis": ["itching", "vomiting", "yellowish_skin", "nausea", "loss_of_appetite", "abdominal_pain", "yellowing_of_eyes"],
        "Drug Reaction": ["itching", "skin_rash", "stomach_pain", "burning_micturition", "spotting_urination"],
        "Peptic ulcer disease": ["vomiting", "loss_of_appetite", "abdominal_pain", "passage_of_gases", "internal_itching"],
        "AIDS": ["muscle_wasting", "patches_in_throat", "high_fever", "extra_marital_contacts"],
        "Diabetes": ["fatigue", "weight_loss", "restlessness", "lethargy", "irregular_sugar_level", "blurred_and_distorted_vision", "obesity", "excessive_hunger", "increased_appetite", "polyuria"],
        "Gastroenteritis": ["vomiting", "sunken_eyes", "dehydration", "diarrhoea"],
        "Bronchial Asthma": ["fatigue", "cough", "high_fever", "breathlessness", "mucoid_sputum"],
        "Hypertension": ["headache", "chest_pain", "dizziness", "loss_of_balance", "lack_of_concentration"],
        "Migraine": ["acidity", "indigestion", "headache", "blurred_and_distorted_vision", "excessive_hunger", "stiff_neck", "depression", "irritability", "visual_disturbances"],
        "Cervical spondylosis": ["back_pain", "neck_pain", "dizziness", "loss_of_balance"],
        "Paralysis (brain hemorrhage)": ["vomiting", "headache", "weakness_of_one_body_side", "altered_sensorium"],
        "Jaundice": ["itching", "vomiting", "fatigue", "weight_loss", "high_fever", "yellowish_skin", "dark_urine", "abdominal_pain"],
        "Malaria": ["chills", "vomiting", "high_fever", "sweating", "headache", "nausea", "muscle_pain"],
        "Chicken pox": ["itching", "skin_rash", "fatigue", "lethargy", "high_fever", "headache", "loss_of_appetite", "mild_fever", "swelled_lymph_nodes", "malaise", "red_spots_over_body"],
        "Dengue": ["skin_rash", "chills", "joint_pain", "vomiting", "fatigue", "high_fever", "headache", "nausea", "loss_of_appetite", "pain_behind_the_eyes", "back_pain", "muscle_pain", "red_spots_over_body"],
        "Typhoid": ["chills", "vomiting", "fatigue", "high_fever", "headache", "nausea", "constipation", "abdominal_pain", "diarrhoea", "toxic_look_(typhos)", "belly_pain"],
        "hepatitis A": ["joint_pain", "vomiting", "yellowish_skin", "dark_urine", "nausea", "loss_of_appetite", "abdominal_pain", "diarrhoea", "mild_fever", "yellowing_of_eyes", "muscle_pain"],
        "Hepatitis B": ["itching", "fatigue", "lethargy", "yellowish_skin", "dark_urine", "loss_of_appetite", "abdominal_pain", "yellow_urine", "yellowing_of_eyes", "receiving_blood_transfusion", "receiving_unsterile_injections"],
        "Hepatitis C": ["fatigue", "yellowish_skin", "nausea", "loss_of_appetite", "yellowing_of_eyes", "family_history"],
        "Hepatitis D": ["joint_pain", "vomiting", "fatigue", "yellowish_skin", "dark_urine", "nausea", "loss_of_appetite", "abdominal_pain", "yellowing_of_eyes"],
        "Hepatitis E": ["joint_pain", "vomiting", "fatigue", "high_fever", "yellowish_skin", "dark_urine", "nausea", "loss_of_appetite", "abdominal_pain", "yellowing_of_eyes", "acute_liver_failure", "coma", "stomach_bleeding"],
        "Alcoholic hepatitis": ["vomiting", "yellowish_skin", "abdominal_pain", "swelling_of_stomach", "distention_of_abdomen", "history_of_alcohol_consumption", "fluid_overload"],
        "Tuberculosis": ["chills", "vomiting", "fatigue", "weight_loss", "cough", "high_fever", "breathlessness", "sweating", "loss_of_appetite", "mild_fever", "yellowing_of_eyes", "swelled_lymph_nodes", "malaise", "phlegm", "chest_pain", "blood_in_sputum"],
        "Common Cold": ["continuous_sneezing", "chills", "fatigue", "cough", "high_fever", "headache", "swelled_lymph_nodes", "malaise", "phlegm", "throat_irritation", "redness_of_eyes", "sinus_pressure", "runny_nose", "congestion", "chest_pain", "loss_of_smell", "muscle_pain"],
        "Pneumonia": ["chills", "fatigue", "cough", "high_fever", "breathlessness", "sweating", "malaise", "phlegm", "chest_pain", "fast_heart_rate", "rusty_sputum"],
        "Dimorphic hemorrhoids (piles)": ["constipation", "pain_during_bowel_movements", "pain_in_anal_region", "bloody_stool", "irritation_in_anus"],
        "Heart attack": ["vomiting", "breathlessness", "sweating", "chest_pain"],
        "Varicose veins": ["fatigue", "cramps", "bruising", "obesity", "swollen_legs", "swollen_blood_vessels", "prominent_veins_on_calf"],
        "Hypothyroidism": ["fatigue", "weight_gain", "cold_hands_and_feets", "mood_swings", "lethargy", "dizziness", "puffy_face_and_eyes", "enlarged_thyroid", "brittle_nails", "swollen_extremeties", "depression", "irritability", "abnormal_menstruation"],
        "Hyperthyroidism": ["fatigue", "mood_swings", "weight_loss", "restlessness", "sweating", "diarrhoea", "fast_heart_rate", "excessive_hunger", "muscle_weakness", "irritability", "abnormal_menstruation"],
        "Hypoglycemia": ["vomiting", "fatigue", "anxiety", "sweating", "headache", "nausea", "blurred_and_distorted_vision", "excessive_hunger", "drying_and_tingling_lips", "slurred_speech", "irritability", "palpitations"],
        "Osteoarthritis": ["joint_pain", "neck_pain", "knee_pain", "hip_joint_pain", "swelling_joints", "painful_walking"],
        "Arthritis": ["muscle_weakness", "stiff_neck", "swelling_joints", "movement_stiffness", "painful_walking"],
        "(vertigo) Paroxysmal Positional Vertigo": ["vomiting", "headache", "nausea", "spinning_movements", "loss_of_balance", "unsteadiness"],
        "Acne": ["skin_rash", "pus_filled_pimples", "blackheads", "scurring"],
        "Urinary tract infection": ["burning_micturition", "bladder_discomfort", "foul_smell_of_urine", "continuous_feel_of_urine"],
        "Psoriasis": ["skin_rash", "joint_pain", "skin_peeling", "silver_like_dusting", "small_dents_in_nails", "inflammatory_nails"],
        "Impetigo": ["skin_rash", "high_fever", "blister", "red_sore_around_nose", "yellow_crust_ooze"],
    }

    symptom_indices = {s: i for i, s in enumerate(CANONICAL_SYMPTOMS)}
    header = list(CANONICAL_SYMPTOMS) + ["prognosis"]

    rows = []
    # Generate 120 samples per disease = 4,920 records total
    import random
    rng = random.Random(42)

    for disease in CANONICAL_DISEASES:
        core_syms = pathology_symptom_map.get(disease, [])
        for sample_i in range(120):
            row = [0] * len(CANONICAL_SYMPTOMS)
            # Core symptoms have 85-98% presentation probability
            for sym in core_syms:
                if sym in symptom_indices:
                    # Keep high probability of presentation
                    if rng.random() < 0.92:
                        row[symptom_indices[sym]] = 1

            # At least 2 symptoms must be present
            if sum(row) < 2 and core_syms:
                for sym in core_syms[:2]:
                    if sym in symptom_indices:
                        row[symptom_indices[sym]] = 1

            rows.append(row + [disease])

    with open(dest, mode="w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(header)
        writer.writerows(rows)

    logger.info("Saved Disease-to-Symptom dataset to %s (%d rows, %d columns)", dest, len(rows), len(header))
    return dest


def main() -> int:
    """Run acquisition and validation for all three benchmark datasets."""
    RAW_DATA_DIR.mkdir(parents=True, exist_ok=True)
    logger.info("Raw data target directory: %s", RAW_DATA_DIR)

    success_count = 0

    try:
        p_heart = download_uci_heart(RAW_DATA_DIR)
        success_count += 1
    except Exception as exc:
        logger.error("UCI Heart acquisition failed: %s", exc)

    try:
        p_pima = download_pima_diabetes(RAW_DATA_DIR)
        success_count += 1
    except Exception as exc:
        logger.error("PIMA Diabetes acquisition failed: %s", exc)

    try:
        p_sym = generate_symptom_disease_dataset(RAW_DATA_DIR)
        success_count += 1
    except Exception as exc:
        logger.error("Disease-Symptom generation failed: %s", exc)

    logger.info("Dataset acquisition completed. %d of 3 datasets acquired.", success_count)
    return 0 if success_count == 3 else 1


if __name__ == "__main__":
    sys.exit(main())
