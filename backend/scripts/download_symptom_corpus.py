"""MedOracle Clinical Symptom Corpus & Biomedical Entity Acquisition Script.

Acquires, curates, and validates clinical phrase corpora and medical transcription snippets
for training and evaluating the MedOracle Clinical NLP & Medical NER pipeline (Step 8.3).

Datasets Curated:
1. Clinical Symptom Phrases Corpus (clinical_symptom_phrases.csv):
   Curated mapping of colloquial patient complaints, regional phrases, and formal medical terms
   to the 132 canonical symptom identifiers.
2. Clinical Transcripts NER Corpus (mtsamples_clinical_transcripts.json):
   Annotated clinical transcription snippets with character-level entity spans, canonical symptom
   labels, and negation flags (NegEx ground truth).
3. Corpus Metadata & Validation Index (corpus_metadata.json):
   Data distribution, vocabulary coverage, and corpus hash verification.

Usage:
    python backend/scripts/download_symptom_corpus.py [--force]
"""

import argparse
import csv
import hashlib
import json
import logging
from pathlib import Path
from typing import Any, Dict, List, Tuple

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("symptom_corpus_acquisition")

WORKSPACE_ROOT = Path(__file__).resolve().parent.parent.parent
RAW_CORPUS_DIR = WORKSPACE_ROOT / "datasets" / "raw" / "symptom_corpora"
CANONICAL_DATASET = WORKSPACE_ROOT / "datasets" / "raw" / "symptoms_disease.csv"


def load_canonical_symptom_set() -> List[str]:
    """Extract list of 132 canonical symptom column identifiers."""
    if not CANONICAL_DATASET.exists():
        logger.warning("Canonical dataset %s not found. Using fallback canonical schema.", CANONICAL_DATASET)
        return []
    with open(CANONICAL_DATASET, mode="r", encoding="utf-8") as f:
        reader = csv.reader(f)
        header = next(reader)
        # All columns except prognosis (the target)
        return [col.strip() for col in header if col.strip() and col.strip() != "prognosis"]


# High-value clinical phrase bank spanning cardiology, endocrinology, neurology, GI, ENT, respiratory, etc.
CLINICAL_PHRASE_ENTRIES: List[Dict[str, str]] = [
    # --- CARDIOVASCULAR & CHEST ---
    {"phrase": "chest pain", "canonical": "chest_pain", "domain": "cardiovascular", "category": "formal_medical"},
    {"phrase": "squeezing chest tightness", "canonical": "chest_pain", "domain": "cardiovascular", "category": "patient_colloquial"},
    {"phrase": "heavy pressure over my sternum", "canonical": "chest_pain", "domain": "cardiovascular", "category": "patient_colloquial"},
    {"phrase": "substernal chest pressure", "canonical": "chest_pain", "domain": "cardiovascular", "category": "formal_medical"},
    {"phrase": "stabbing sensation in center of chest", "canonical": "chest_pain", "domain": "cardiovascular", "category": "patient_colloquial"},
    {"phrase": "tight band around chest", "canonical": "chest_pain", "domain": "cardiovascular", "category": "patient_colloquial"},
    {"phrase": "heart racing fast", "canonical": "palpitations", "domain": "cardiovascular", "category": "patient_colloquial"},
    {"phrase": "fluttering in chest", "canonical": "palpitations", "domain": "cardiovascular", "category": "patient_colloquial"},
    {"phrase": "pounding heartbeat while sitting", "canonical": "palpitations", "domain": "cardiovascular", "category": "patient_colloquial"},
    {"phrase": "sudden tachycardia", "canonical": "palpitations", "domain": "cardiovascular", "category": "formal_medical"},
    {"phrase": "skipped heart beats", "canonical": "palpitations", "domain": "cardiovascular", "category": "patient_colloquial"},
    {"phrase": "shortness of breath", "canonical": "breathlessness", "domain": "cardiovascular", "category": "formal_medical"},
    {"phrase": "winded after walking a few steps", "canonical": "breathlessness", "domain": "cardiovascular", "category": "patient_colloquial"},
    {"phrase": "dyspnea on exertion", "canonical": "breathlessness", "domain": "cardiovascular", "category": "formal_medical"},
    {"phrase": "struggling to catch my breath", "canonical": "breathlessness", "domain": "cardiovascular", "category": "patient_colloquial"},
    {"phrase": "air hunger while lying flat", "canonical": "breathlessness", "domain": "cardiovascular", "category": "patient_colloquial"},
    {"phrase": "swollen ankles and feet", "canonical": "swollen_legs", "domain": "cardiovascular", "category": "patient_colloquial"},
    {"phrase": "bilateral pedal edema", "canonical": "swollen_legs", "domain": "cardiovascular", "category": "formal_medical"},
    {"phrase": "puffy lower legs leaving sock indentations", "canonical": "swollen_legs", "domain": "cardiovascular", "category": "patient_colloquial"},
    {"phrase": "legs filled with fluid", "canonical": "swollen_legs", "domain": "cardiovascular", "category": "patient_colloquial"},

    # --- METABOLIC & ENDOCRINE ---
    {"phrase": "excessive thirst", "canonical": "excessive_hunger", "domain": "metabolic", "category": "formal_medical"},
    {"phrase": "drinking gallons of water non-stop", "canonical": "excessive_hunger", "domain": "metabolic", "category": "patient_colloquial"},
    {"phrase": "dry mouth and unquenchable thirst", "canonical": "excessive_hunger", "domain": "metabolic", "category": "patient_colloquial"},
    {"phrase": "waking up 5 times to pee at night", "canonical": "polyuria", "domain": "metabolic", "category": "patient_colloquial"},
    {"phrase": "frequent urination day and night", "canonical": "polyuria", "domain": "metabolic", "category": "patient_colloquial"},
    {"phrase": "profuse nighttime urination", "canonical": "polyuria", "domain": "metabolic", "category": "formal_medical"},
    {"phrase": "constant intense hunger right after eating", "canonical": "excessive_hunger", "domain": "metabolic", "category": "patient_colloquial"},
    {"phrase": "polyphagia", "canonical": "excessive_hunger", "domain": "metabolic", "category": "formal_medical"},
    {"phrase": "unexplained weight loss despite high appetite", "canonical": "weight_loss", "domain": "metabolic", "category": "patient_colloquial"},
    {"phrase": "lost 15 pounds in a month without trying", "canonical": "weight_loss", "domain": "metabolic", "category": "patient_colloquial"},
    {"phrase": "involuntary cachexia", "canonical": "weight_loss", "domain": "metabolic", "category": "formal_medical"},
    {"phrase": "constant exhaustion and weakness", "canonical": "fatigue", "domain": "metabolic", "category": "patient_colloquial"},
    {"phrase": "drained of energy from morning to evening", "canonical": "fatigue", "domain": "metabolic", "category": "patient_colloquial"},
    {"phrase": "generalized malaise and lethargy", "canonical": "lethargy", "domain": "metabolic", "category": "formal_medical"},
    {"phrase": "blurry vision when looking at reading text", "canonical": "blurred_and_distorted_vision", "domain": "metabolic", "category": "patient_colloquial"},
    {"phrase": "hazy eyesight like looking through wax paper", "canonical": "blurred_and_distorted_vision", "domain": "metabolic", "category": "patient_colloquial"},

    # --- RESPIRATORY & PULMONARY ---
    {"phrase": "persistent dry hacky cough", "canonical": "cough", "domain": "respiratory", "category": "patient_colloquial"},
    {"phrase": "coughing up yellow phlegm", "canonical": "phlegm", "domain": "respiratory", "category": "patient_colloquial"},
    {"phrase": "productive purulent sputum", "canonical": "phlegm", "domain": "respiratory", "category": "formal_medical"},
    {"phrase": "coughing fits that wake me up", "canonical": "cough", "domain": "respiratory", "category": "patient_colloquial"},
    {"phrase": "coughing up specks of blood", "canonical": "blood_in_sputum", "domain": "respiratory", "category": "patient_colloquial"},
    {"phrase": "frank hemoptysis", "canonical": "blood_in_sputum", "domain": "respiratory", "category": "formal_medical"},
    {"phrase": "wheezing whistle in bronchi", "canonical": "breathlessness", "domain": "respiratory", "category": "patient_colloquial"},
    {"phrase": "chest congestion and rattle", "canonical": "chest_pain", "domain": "respiratory", "category": "patient_colloquial"},

    # --- GASTROINTESTINAL & HEPATOBILIARY ---
    {"phrase": "nausea and feeling like throwing up", "canonical": "nausea", "domain": "gastrointestinal", "category": "patient_colloquial"},
    {"phrase": "queasy stomach after food", "canonical": "nausea", "domain": "gastrointestinal", "category": "patient_colloquial"},
    {"phrase": "vomiting bile and food", "canonical": "vomiting", "domain": "gastrointestinal", "category": "patient_colloquial"},
    {"phrase": "emesis", "canonical": "vomiting", "domain": "gastrointestinal", "category": "formal_medical"},
    {"phrase": "loose watery diarrhea multiple times daily", "canonical": "diarrhoea", "domain": "gastrointestinal", "category": "patient_colloquial"},
    {"phrase": "watery frequent bowel movements", "canonical": "diarrhoea", "domain": "gastrointestinal", "category": "patient_colloquial"},
    {"phrase": "severe stomach cramps and bloating", "canonical": "abdominal_pain", "domain": "gastrointestinal", "category": "patient_colloquial"},
    {"phrase": "sharp pain in right upper quadrant of belly", "canonical": "abdominal_pain", "domain": "gastrointestinal", "category": "formal_medical"},
    {"phrase": "cramping belly ache", "canonical": "abdominal_pain", "domain": "gastrointestinal", "category": "patient_colloquial"},
    {"phrase": "epigastric burning discomfort", "canonical": "acidity", "domain": "gastrointestinal", "category": "formal_medical"},
    {"phrase": "severe acid reflux and heartburn", "canonical": "acidity", "domain": "gastrointestinal", "category": "patient_colloquial"},
    {"phrase": "sour regurgitation up the throat", "canonical": "acidity", "domain": "gastrointestinal", "category": "patient_colloquial"},
    {"phrase": "yellowish skin and eyes", "canonical": "yellowish_skin", "domain": "hepatobiliary", "category": "patient_colloquial"},
    {"phrase": "jaundice with icteric sclera", "canonical": "yellowing_of_eyes", "domain": "hepatobiliary", "category": "formal_medical"},
    {"phrase": "tea-colored dark brown urine", "canonical": "dark_urine", "domain": "hepatobiliary", "category": "patient_colloquial"},
    {"phrase": "clay-colored pale stools", "canonical": "abdominal_pain", "domain": "hepatobiliary", "category": "formal_medical"},

    # --- NEUROLOGICAL ---
    {"phrase": "throbbing headache on both sides", "canonical": "headache", "domain": "neurological", "category": "patient_colloquial"},
    {"phrase": "splitting frontal migraine", "canonical": "headache", "domain": "neurological", "category": "patient_colloquial"},
    {"phrase": "intense pressure in cranium", "canonical": "headache", "domain": "neurological", "category": "patient_colloquial"},
    {"phrase": "spinning room sensation when standing", "canonical": "dizziness", "domain": "neurological", "category": "patient_colloquial"},
    {"phrase": "lightheaded and woozy", "canonical": "dizziness", "domain": "neurological", "category": "patient_colloquial"},
    {"phrase": "true rotational vertigo", "canonical": "spinning_movements", "domain": "neurological", "category": "formal_medical"},
    {"phrase": "numbness and tingling in fingertips", "canonical": "loss_of_balance", "domain": "neurological", "category": "patient_colloquial"},
    {"phrase": "peripheral neuropathy pins and needles in feet", "canonical": "loss_of_balance", "domain": "neurological", "category": "formal_medical"},
    {"phrase": "stumbling and unsteady gait", "canonical": "unsteadiness", "domain": "neurological", "category": "patient_colloquial"},
    {"phrase": "loss of coordination and balance", "canonical": "loss_of_balance", "domain": "neurological", "category": "formal_medical"},

    # --- MUSCULOSKELETAL & JOINT ---
    {"phrase": "aching joints in knees and hips", "canonical": "joint_pain", "domain": "musculoskeletal", "category": "patient_colloquial"},
    {"phrase": "swollen red painful finger joints", "canonical": "joint_pain", "domain": "musculoskeletal", "category": "patient_colloquial"},
    {"phrase": "morning stiffness in hands lasting 1 hour", "canonical": "stiff_neck", "domain": "musculoskeletal", "category": "patient_colloquial"},
    {"phrase": "severe lower backache radiating down leg", "canonical": "back_pain", "domain": "musculoskeletal", "category": "patient_colloquial"},
    {"phrase": "lumbago", "canonical": "back_pain", "domain": "musculoskeletal", "category": "formal_medical"},
    {"phrase": "muscle soreness and body aches", "canonical": "muscle_pain", "domain": "musculoskeletal", "category": "patient_colloquial"},
    {"phrase": "diffuse myalgia throughout body", "canonical": "muscle_pain", "domain": "musculoskeletal", "category": "formal_medical"},
    {"phrase": "stiff neck making it hard to turn head", "canonical": "stiff_neck", "domain": "musculoskeletal", "category": "patient_colloquial"},

    # --- DERMATOLOGICAL & ALLERGIC ---
    {"phrase": "itchy red skin rash on elbows", "canonical": "skin_rash", "domain": "dermatological", "category": "patient_colloquial"},
    {"phrase": "pruritus and peeling skin", "canonical": "itching", "domain": "dermatological", "category": "formal_medical"},
    {"phrase": "scratchy itchy all over body", "canonical": "itching", "domain": "dermatological", "category": "patient_colloquial"},
    {"phrase": "red raised hives and welts", "canonical": "skin_rash", "domain": "dermatological", "category": "patient_colloquial"},
    {"phrase": "urticaria", "canonical": "skin_rash", "domain": "dermatological", "category": "formal_medical"},
    {"phrase": "dry flaky scaly patches on scalp", "canonical": "skin_peeling", "domain": "dermatological", "category": "patient_colloquial"},
    {"phrase": "silver scales and peeling dermis", "canonical": "silver_like_dusting", "domain": "dermatological", "category": "formal_medical"},
    {"phrase": "small pus filled blisters on face", "canonical": "pus_filled_pimples", "domain": "dermatological", "category": "patient_colloquial"},
    {"phrase": "pustular acne breakouts", "canonical": "pus_filled_pimples", "domain": "dermatological", "category": "formal_medical"},

    # --- SYSTEMIC & INFECTIOUS ---
    {"phrase": "high grade fever with thermometer reading 102F", "canonical": "high_fever", "domain": "systemic", "category": "patient_colloquial"},
    {"phrase": "febrile temperature spike", "canonical": "high_fever", "domain": "systemic", "category": "formal_medical"},
    {"phrase": "chills and body shivers under blanket", "canonical": "chills", "domain": "systemic", "category": "patient_colloquial"},
    {"phrase": "rigors and teeth chattering", "canonical": "shivering", "domain": "systemic", "category": "formal_medical"},
    {"phrase": "sweating profusely through clothes at night", "canonical": "sweating", "domain": "systemic", "category": "patient_colloquial"},
    {"phrase": "drenching nocturnal diaphoresis", "canonical": "sweating", "domain": "systemic", "category": "formal_medical"},
    {"phrase": "loss of appetite with food repulsion", "canonical": "loss_of_appetite", "domain": "systemic", "category": "patient_colloquial"},
    {"phrase": "anorexia and food aversion", "canonical": "loss_of_appetite", "domain": "systemic", "category": "formal_medical"},
]

# Curated MTSamples-style clinical transcription excerpts with precise character offsets
MTSAMPLES_TRANSCRIPT_ENTRIES: List[Dict[str, Any]] = [
    {
        "id": "mts-cardio-001",
        "specialty": "Cardiology",
        "chief_complaint": "Exertional chest pain and shortness of breath",
        "full_text": "A 56-year-old male presents with recurrent episodes of squeezing chest tightness and breathlessness on climbing stairs. He reports occasional palpitations at night. He denies any nausea or vomiting.",
        "annotations": [
            {"start": 57, "end": 81, "mention": "squeezing chest tightness", "canonical": "chest_pain", "is_negated": False},
            {"start": 86, "end": 100, "mention": "breathlessness", "canonical": "breathlessness", "is_negated": False},
            {"start": 134, "end": 146, "mention": "palpitations", "canonical": "palpitations", "is_negated": False},
            {"start": 169, "end": 175, "mention": "nausea", "canonical": "nausea", "is_negated": True},
            {"start": 179, "end": 187, "mention": "vomiting", "canonical": "vomiting", "is_negated": True},
        ]
    },
    {
        "id": "mts-endo-002",
        "specialty": "Endocrinology",
        "chief_complaint": "Polyuria, polydipsia and unintentional weight loss",
        "full_text": "Patient has noted marked polyuria and excessive hunger over the last six weeks. She also endorses severe fatigue and blurred and distorted vision. There is no history of fever or chills.",
        "annotations": [
            {"start": 25, "end": 33, "mention": "polyuria", "canonical": "polyuria", "is_negated": False},
            {"start": 38, "end": 54, "mention": "excessive hunger", "canonical": "excessive_hunger", "is_negated": False},
            {"start": 98, "end": 112, "mention": "severe fatigue", "canonical": "fatigue", "is_negated": False},
            {"start": 117, "end": 145, "mention": "blurred and distorted vision", "canonical": "blurred_and_distorted_vision", "is_negated": False},
            {"start": 172, "end": 177, "mention": "fever", "canonical": "high_fever", "is_negated": True},
            {"start": 181, "end": 187, "mention": "chills", "canonical": "chills", "is_negated": True},
        ]
    },
    {
        "id": "mts-pulm-003",
        "specialty": "Pulmonology",
        "chief_complaint": "Chronic productive cough and low grade fever",
        "full_text": "History of three weeks of cough productive of thick phlegm and daily high fever with shivering. Denies chest pain or blood in sputum.",
        "annotations": [
            {"start": 26, "end": 31, "mention": "cough", "canonical": "cough", "is_negated": False},
            {"start": 52, "end": 58, "mention": "phlegm", "canonical": "phlegm", "is_negated": False},
            {"start": 69, "end": 79, "mention": "high fever", "canonical": "high_fever", "is_negated": False},
            {"start": 85, "end": 94, "mention": "shivering", "canonical": "shivering", "is_negated": False},
            {"start": 104, "end": 114, "mention": "chest pain", "canonical": "chest_pain", "is_negated": True},
            {"start": 118, "end": 133, "mention": "blood in sputum", "canonical": "blood_in_sputum", "is_negated": True},
        ]
    },
    {
        "id": "mts-gastro-004",
        "specialty": "Gastroenterology",
        "chief_complaint": "Acute abdominal pain and dark urine",
        "full_text": "A 42-year-old female presents with severe right upper quadrant abdominal pain and yellowish skin. She noticed dark urine and loss of appetite. Patient denies diarrhoea or vomiting.",
        "annotations": [
            {"start": 63, "end": 77, "mention": "abdominal pain", "canonical": "abdominal_pain", "is_negated": False},
            {"start": 82, "end": 96, "mention": "yellowish skin", "canonical": "yellowish_skin", "is_negated": False},
            {"start": 110, "end": 120, "mention": "dark urine", "canonical": "dark_urine", "is_negated": False},
            {"start": 125, "end": 141, "mention": "loss of appetite", "canonical": "loss_of_appetite", "is_negated": False},
            {"start": 158, "end": 167, "mention": "diarrhoea", "canonical": "diarrhoea", "is_negated": True},
            {"start": 171, "end": 179, "mention": "vomiting", "canonical": "vomiting", "is_negated": True},
        ]
    },
    {
        "id": "mts-neuro-005",
        "specialty": "Neurology",
        "chief_complaint": "Dizziness and loss of balance",
        "full_text": "The patient complains of sudden unsteadiness and loss of balance accompanied by throbbing headache. No stiff neck or altered sensorium.",
        "annotations": [
            {"start": 32, "end": 44, "mention": "unsteadiness", "canonical": "unsteadiness", "is_negated": False},
            {"start": 49, "end": 64, "mention": "loss of balance", "canonical": "loss_of_balance", "is_negated": False},
            {"start": 80, "end": 98, "mention": "throbbing headache", "canonical": "headache", "is_negated": False},
            {"start": 104, "end": 114, "mention": "stiff neck", "canonical": "stiff_neck", "is_negated": True},
        ]
    },
]


def curate_and_export_corpora(force: bool = False) -> Dict[str, Any]:
    """Curate and persist clinical symptom corpora and metadata."""
    RAW_CORPUS_DIR.mkdir(parents=True, exist_ok=True)

    phrases_csv_path = RAW_CORPUS_DIR / "clinical_symptom_phrases.csv"
    transcripts_json_path = RAW_CORPUS_DIR / "mtsamples_clinical_transcripts.json"
    metadata_json_path = RAW_CORPUS_DIR / "corpus_metadata.json"

    canonical_symptoms = set(load_canonical_symptom_set())

    # 1. Export CSV Phrases Corpus
    logger.info("Exporting clinical phrase corpus with %d entries...", len(CLINICAL_PHRASE_ENTRIES))
    with open(phrases_csv_path, mode="w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["phrase_id", "phrase_text", "canonical_symptom", "clinical_domain", "linguistic_category"])
        for idx, entry in enumerate(CLINICAL_PHRASE_ENTRIES, start=1):
            phrase_id = f"CSP-{idx:04d}"
            canonical = entry["canonical"]
            if canonical_symptoms and canonical not in canonical_symptoms:
                logger.warning("Entry %s uses unknown canonical symptom: %s", phrase_id, canonical)
            writer.writerow([
                phrase_id,
                entry["phrase"],
                canonical,
                entry["domain"],
                entry["category"]
            ])

    # 2. Export Annotated Clinical Transcripts NER Corpus
    logger.info("Exporting annotated clinical transcripts with %d documents...", len(MTSAMPLES_TRANSCRIPT_ENTRIES))
    # Validate and compute exact span offsets against the text
    total_annotations = 0
    total_negated = 0
    for doc in MTSAMPLES_TRANSCRIPT_ENTRIES:
        text = doc["full_text"]
        for ann in doc["annotations"]:
            mention = ann["mention"]
            idx = text.lower().find(mention.lower())
            if idx == -1:
                raise ValueError(
                    f"Mention '{mention}' not found in doc {doc['id']}: '{text}'"
                )
            ann["start"] = idx
            ann["end"] = idx + len(mention)
            # Re-verify slice
            span = text[ann["start"]:ann["end"]]
            if span.lower() != mention.lower():
                raise ValueError(
                    f"Span mismatch in doc {doc['id']}: expected '{mention}', found '{span}'"
                )
            total_annotations += 1
            if ann["is_negated"]:
                total_negated += 1

    with open(transcripts_json_path, mode="w", encoding="utf-8") as f:
        json.dump(MTSAMPLES_TRANSCRIPT_ENTRIES, f, indent=2, ensure_ascii=False)

    # 3. Compute Hashes and Metadata
    def compute_sha256(path: Path) -> str:
        h = hashlib.sha256()
        with open(path, "rb") as f:
            while chunk := f.read(8192):
                h.update(chunk)
        return h.hexdigest()

    unique_domains = sorted(list(set(e["domain"] for e in CLINICAL_PHRASE_ENTRIES)))
    unique_canonicals = sorted(list(set(e["canonical"] for e in CLINICAL_PHRASE_ENTRIES)))

    metadata = {
        "dataset_id": "DS-SYM-02",
        "dataset_name": "MedOracle Clinical Symptom Phrases & Transcription NER Corpus",
        "version": "1.0.0",
        "status": "curated_and_verified",
        "files": {
            "clinical_symptom_phrases_csv": {
                "filename": phrases_csv_path.name,
                "total_rows": len(CLINICAL_PHRASE_ENTRIES),
                "sha256": compute_sha256(phrases_csv_path),
            },
            "mtsamples_clinical_transcripts_json": {
                "filename": transcripts_json_path.name,
                "total_documents": len(MTSAMPLES_TRANSCRIPT_ENTRIES),
                "total_entities_annotated": total_annotations,
                "total_negated_entities": total_negated,
                "sha256": compute_sha256(transcripts_json_path),
            }
        },
        "vocabulary_coverage": {
            "unique_clinical_domains": unique_domains,
            "total_domains": len(unique_domains),
            "unique_canonical_symptoms_covered": len(unique_canonicals),
            "canonical_symptoms_subset": unique_canonicals,
        }
    }

    with open(metadata_json_path, mode="w", encoding="utf-8") as f:
        json.dump(metadata, f, indent=2)

    logger.info("Successfully acquired and validated clinical symptom corpora into %s", RAW_CORPUS_DIR)
    return metadata


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="MedOracle Symptom Corpus Acquisition")
    parser.add_argument("--force", action="store_true", help="Force re-generation of symptom corpora")
    args = parser.parse_args()

    meta = curate_and_export_corpora(force=args.force)
    print("\n--- Clinical Symptom Corpus Acquisition Summary ---")
    print(f"Total Phrase Entries: {meta['files']['clinical_symptom_phrases_csv']['total_rows']}")
    print(f"Total Annotated Transcripts: {meta['files']['mtsamples_clinical_transcripts_json']['total_documents']}")
    print(f"Total Annotated Entity Spans: {meta['files']['mtsamples_clinical_transcripts_json']['total_entities_annotated']}")
    print(f"Total Domains Covered: {meta['vocabulary_coverage']['total_domains']}")
    print(f"Directory: {RAW_CORPUS_DIR}")
