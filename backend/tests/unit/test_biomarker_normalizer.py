"""Unit test suite for Clinical OCR Biomarker Normalization & Entity Disambiguation (Step 8.4.3).

Validates:
1. Canonical Entity Mapping & Synonym Resolution.
2. Strict Assay Disambiguation (BNP vs NT-proBNP; Troponin I vs T; hs vs standard).
3. Ambiguous and Unmapped Label Handling.
4. Deterministic Unit Conversions & Guideline Formulae.
5. Incompatible and Missing Unit Detection.
6. OCR Typo Tolerance & Numeric Cleansing (Commas, letter substitutions, inequalities).
7. Qualitative Value Preservation (Negative, Reactive, Trace without invented floats).
8. Reference Range Extraction, Unit Normalization, and Abnormality Classification.
9. Abnormality Flag Conflict Detection & Needs Review State.
10. Low OCR Confidence Guarding.
11. Provenance Integrity & Downstream Consumer Dictionary Generation.
"""

import pytest

from app.clinical.biomarker_types import (
    CanonicalBiomarker,
    NormalizationStatus,
    AbnormalityFlag,
)
from app.services.biomarker_normalizer import BiomarkerEntityNormalizer


# =========================================================================
# 1. Entity Mapping & Assay Disambiguation Tests
# =========================================================================

def test_glycemic_entity_synonyms():
    """Verify various aliases for fasting glucose map to canonical fasting_blood_glucose_mg_dl."""
    synonyms = [
        "Fasting Blood Glucose",
        "fasting glucose",
        "FBG",
        "FPG",
        "FBS",
        "Glucose (Fasting)",
        "Blood Sugar Fasting",
        "GLU-F",
        "Serum Glucose, Fasting",
    ]
    for syn in synonyms:
        canon_id, conf, status, amb = BiomarkerEntityNormalizer.map_biomarker_entity(syn)
        assert canon_id == CanonicalBiomarker.FASTING_BLOOD_GLUCOSE, f"Failed for synonym: {syn}"
        assert status == NormalizationStatus.NORMALIZED
        assert conf >= 0.90


def test_strict_bnp_vs_nt_probnp_separation():
    """Verify active BNP and inactive NT-proBNP are strictly delineated as distinct biomarkers."""
    # BNP
    bnp_labels = ["BNP", "B-type Natriuretic Peptide", "Brain Natriuretic Peptide", "Serum BNP"]
    for lbl in bnp_labels:
        canon_id, conf, status, _ = BiomarkerEntityNormalizer.map_biomarker_entity(lbl)
        assert canon_id == CanonicalBiomarker.BNP, f"Failed for BNP label: {lbl}"
        assert canon_id != CanonicalBiomarker.NT_PROBNP

    # NT-proBNP
    nt_labels = ["NT-proBNP", "NT-Pro BNP", "N-Terminal proBNP", "Pro-BNP", "N-terminal pro-B-type natriuretic peptide"]
    for lbl in nt_labels:
        canon_id, conf, status, _ = BiomarkerEntityNormalizer.map_biomarker_entity(lbl)
        assert canon_id == CanonicalBiomarker.NT_PROBNP, f"Failed for NT-proBNP label: {lbl}"
        assert canon_id != CanonicalBiomarker.BNP


def test_strict_troponin_assay_separation():
    """Verify standard cTnI, standard cTnT, hs-cTnI, and hs-cTnT retain unique non-fungible identities."""
    tests = [
        ("Troponin I", CanonicalBiomarker.TROPONIN_I),
        ("cTnI", CanonicalBiomarker.TROPONIN_I),
        ("Troponin T", CanonicalBiomarker.TROPONIN_T),
        ("cTnT", CanonicalBiomarker.TROPONIN_T),
        ("hs-cTnI", CanonicalBiomarker.HS_TROPONIN_I),
        ("High-Sensitivity Troponin I", CanonicalBiomarker.HS_TROPONIN_I),
        ("hs-cTnT", CanonicalBiomarker.HS_TROPONIN_T),
        ("High-Sensitivity Cardiac Troponin T", CanonicalBiomarker.HS_TROPONIN_T),
    ]
    for lbl, expected in tests:
        canon_id, conf, status, _ = BiomarkerEntityNormalizer.map_biomarker_entity(lbl)
        assert canon_id == expected, f"Label '{lbl}' mapped to {canon_id}, expected {expected}"
        assert status == NormalizationStatus.NORMALIZED


def test_ambiguous_biomarker_labels_rejected():
    """Verify unspecific labels return AMBIGUOUS_BIOMARKER with clinical explanation."""
    ambiguous = [
        "Troponin",
        "Natriuretic peptide",
        "Transaminase",
    ]
    for lbl in ambiguous:
        canon_id, _, status, reason = BiomarkerEntityNormalizer.map_biomarker_entity(lbl)
        assert canon_id is None
        assert status == NormalizationStatus.AMBIGUOUS_BIOMARKER
        assert reason is not None
        assert len(reason) > 10


def test_unknown_biomarker_returns_unmapped():
    """Verify completely uncataloged tests return UNMAPPED status."""
    unknowns = ["Random Unrelated Serum Substance", "Factor XYZ-123", "Alkaline Alpha-9"]
    for lbl in unknowns:
        canon_id, conf, status, reason = BiomarkerEntityNormalizer.map_biomarker_entity(lbl)
        assert canon_id is None
        assert status == NormalizationStatus.UNMAPPED
        assert conf == 0.0


def test_ocr_typo_tolerance_in_entity_mapping():
    """Verify common OCR character transpositions and misspellings map with appropriate confidence."""
    typos = [
        ("c0lestrol", CanonicalBiomarker.TOTAL_CHOLESTEROL),
        ("creatanine", CanonicalBiomarker.SERUM_CREATININE),
        ("triqliserides", CanonicalBiomarker.TRIGLYCERIDES),
        ("haemogl0bin", CanonicalBiomarker.HEMOGLOBIN),
        ("hba1-c", CanonicalBiomarker.HBA1C),
    ]
    for typo, expected in typos:
        canon_id, conf, status, _ = BiomarkerEntityNormalizer.map_biomarker_entity(typo)
        assert canon_id == expected, f"Failed for typo: {typo}"
        assert status == NormalizationStatus.NORMALIZED
        assert 0.80 <= conf <= 0.90


# =========================================================================
# 2. Unit Conversion & Formula Validation Tests
# =========================================================================

def test_glucose_unit_conversion():
    """Verify glucose conversion from mmol/L to mg/dL using MW 180.156 g/mol (factor 18.0156)."""
    # 5.55 mmol/L * 18.0156 = 99.99 mg/dL
    norm_val, unit, factor, method, status = BiomarkerEntityNormalizer.convert_unit(
        CanonicalBiomarker.FASTING_BLOOD_GLUCOSE, 5.55, "mmol/L"
    )
    assert status == NormalizationStatus.NORMALIZED
    assert unit == "mg/dL"
    assert factor == 18.0156
    assert norm_val == pytest.approx(99.99, abs=0.1)

    # mg/dL identity pass-through
    norm_val2, unit2, factor2, _, status2 = BiomarkerEntityNormalizer.convert_unit(
        CanonicalBiomarker.FASTING_BLOOD_GLUCOSE, 126.0, "mg/dL"
    )
    assert status2 == NormalizationStatus.NORMALIZED
    assert unit2 == "mg/dL"
    assert factor2 == 1.0
    assert norm_val2 == 126.0


def test_cholesterol_vs_triglycerides_distinct_molecular_factors():
    """Verify cholesterol (38.67) and triglycerides (88.54) use distinct molecular conversion factors."""
    # Total Cholesterol: 5.0 mmol/L * 38.67 = 193.35 mg/dL
    tc_norm, tc_unit, tc_factor, _, tc_status = BiomarkerEntityNormalizer.convert_unit(
        CanonicalBiomarker.TOTAL_CHOLESTEROL, 5.0, "mmol/L"
    )
    assert tc_status == NormalizationStatus.NORMALIZED
    assert tc_factor == 38.67
    assert tc_norm == pytest.approx(193.35, abs=0.1)

    # Triglycerides: 2.0 mmol/L * 88.54 = 177.08 mg/dL (triolein MW 885.4)
    tg_norm, tg_unit, tg_factor, _, tg_status = BiomarkerEntityNormalizer.convert_unit(
        CanonicalBiomarker.TRIGLYCERIDES, 2.0, "mmol/L"
    )
    assert tg_status == NormalizationStatus.NORMALIZED
    assert tg_factor == 88.54
    assert tg_norm == pytest.approx(177.08, abs=0.1)

    # Ensure cholesterol and triglyceride factors are NEVER equal
    assert tc_factor != tg_factor


def test_creatinine_umol_to_mg_dl():
    """Verify creatinine conversion from µmol/L to mg/dL (divisor 88.42)."""
    # 88.42 µmol/L = 1.00 mg/dL
    norm_val, unit, factor, method, status = BiomarkerEntityNormalizer.convert_unit(
        CanonicalBiomarker.SERUM_CREATININE, 88.42, "µmol/L"
    )
    assert status == NormalizationStatus.NORMALIZED
    assert unit == "mg/dL"
    assert norm_val == pytest.approx(1.0, abs=0.01)
    assert "creatinine" in method

    # Also test ascii umol/L spelling
    norm_val2, _, _, _, status2 = BiomarkerEntityNormalizer.convert_unit(
        CanonicalBiomarker.SERUM_CREATININE, 176.84, "umol/L"
    )
    assert status2 == NormalizationStatus.NORMALIZED
    assert norm_val2 == pytest.approx(2.0, abs=0.02)


def test_hba1c_ifcc_to_ngsp_conversion():
    """Verify IFCC (mmol/mol) converts to NGSP (%) via master equation % = (0.09148 * mmol/mol) + 2.152."""
    # 48 mmol/mol (diagnostic threshold) -> 0.09148*48 + 2.152 = 6.54% ~ 6.5%
    norm_val, unit, _, method, status = BiomarkerEntityNormalizer.convert_unit(
        CanonicalBiomarker.HBA1C, 48.0, "mmol/mol"
    )
    assert status == NormalizationStatus.NORMALIZED
    assert unit == "%"
    assert norm_val == pytest.approx(6.54, abs=0.05)
    assert "master_equation" in method


def test_hemoglobin_and_electrolytes_conversions():
    """Verify hemoglobin g/L -> g/dL (factor 0.1) and electrolytes mEq/L -> mmol/L (1:1)."""
    # Hemoglobin: 140 g/L -> 14.0 g/dL
    hb_norm, hb_unit, hb_factor, _, hb_status = BiomarkerEntityNormalizer.convert_unit(
        CanonicalBiomarker.HEMOGLOBIN, 140.0, "g/L"
    )
    assert hb_status == NormalizationStatus.NORMALIZED
    assert hb_unit == "g/dL"
    assert hb_norm == 14.0
    assert hb_factor == 0.1

    # Sodium: 140 mEq/L -> 140 mmol/L (1:1)
    na_norm, na_unit, na_factor, _, na_status = BiomarkerEntityNormalizer.convert_unit(
        CanonicalBiomarker.SODIUM, 140.0, "mEq/L"
    )
    assert na_status == NormalizationStatus.NORMALIZED
    assert na_unit == "mmol/L"
    assert na_norm == 140.0
    assert na_factor == 1.0


def test_troponin_ng_l_to_ng_ml():
    """Verify troponin conversion from ng/L (pg/mL) to canonical ng/mL (factor 0.001)."""
    # 14 ng/L -> 0.014 ng/mL
    norm_val, unit, factor, _, status = BiomarkerEntityNormalizer.convert_unit(
        CanonicalBiomarker.HS_TROPONIN_T, 14.0, "ng/L"
    )
    assert status == NormalizationStatus.NORMALIZED
    assert unit == "ng/mL"
    assert norm_val == 0.014
    assert factor == 0.001


def test_missing_unit_flags_explicit_status():
    """Verify absent unit returns MISSING_UNIT and does NOT silently assume a default."""
    norm_val, unit, factor, method, status = BiomarkerEntityNormalizer.convert_unit(
        CanonicalBiomarker.FASTING_BLOOD_GLUCOSE, 125.0, None
    )
    assert status == NormalizationStatus.MISSING_UNIT
    assert norm_val is None
    assert method == "unit_missing"


def test_incompatible_unit_flags_unsupported_status():
    """Verify clinically nonsensical units return UNSUPPORTED_UNIT."""
    # Glucose in mmHg
    norm_val, unit, _, _, status = BiomarkerEntityNormalizer.convert_unit(
        CanonicalBiomarker.FASTING_BLOOD_GLUCOSE, 125.0, "mmHg"
    )
    assert status == NormalizationStatus.UNSUPPORTED_UNIT
    assert norm_val is None

    # Creatinine in g/dL
    norm_val2, _, _, _, status2 = BiomarkerEntityNormalizer.convert_unit(
        CanonicalBiomarker.SERUM_CREATININE, 1.2, "g/dL"
    )
    assert status2 == NormalizationStatus.UNSUPPORTED_UNIT


# =========================================================================
# 3. Numeric Parsing, Sanitation & Qualitative Results Tests
# =========================================================================

def test_numeric_parsing_decimal_commas_and_thousands():
    """Verify European decimal commas and thousands commas are correctly sanitized."""
    # European decimal: 1,25 -> 1.25
    val, comp, qual = BiomarkerEntityNormalizer.parse_numeric_value("1,25")
    assert val == 1.25
    assert comp is None
    assert qual is None

    # Thousands comma: 1,250.5 -> 1250.5
    val2, comp2, _ = BiomarkerEntityNormalizer.parse_numeric_value("1,250.5")
    assert val2 == 1250.5

    # Inequality: < 0.01
    val3, comp3, _ = BiomarkerEntityNormalizer.parse_numeric_value("< 0.01")
    assert val3 == 0.01
    assert comp3 == "<"


def test_ocr_glyph_substitutions_in_numbers():
    """Verify common OCR letter-in-number substitutions (e.g. 1O5 -> 105, l42 -> 142)."""
    val, _, _ = BiomarkerEntityNormalizer.parse_numeric_value("1O5")
    assert val == 105.0

    val2, _, _ = BiomarkerEntityNormalizer.parse_numeric_value("l42")
    assert val2 == 142.0


def test_qualitative_laboratory_results_preserved():
    """Verify qualitative results (Negative, Reactive, Trace) are preserved without inventing numbers."""
    qual_samples = ["Negative", "Non-reactive", "Normal", "Trace", "Positive"]
    for q in qual_samples:
        val, comp, qual = BiomarkerEntityNormalizer.parse_numeric_value(q)
        assert val is None, f"Qualitative string '{q}' was incorrectly converted to float {val}"
        assert qual == q

        # Run full normalization entry
        res = BiomarkerEntityNormalizer.normalize_biomarker_entry(
            raw_label="HBsAg",
            raw_value=q,
            raw_unit=None,
        )
        assert res["validation_status"] == NormalizationStatus.QUALITATIVE_VALUE.value
        assert res["qualitative_value"] == q
        assert res["normalized_value"] is None


# =========================================================================
# 4. Reference Ranges & Abnormality Classification Tests
# =========================================================================

def test_reference_range_extraction_and_unit_conversion():
    """Verify reference ranges are parsed and converted to canonical unit."""
    # Glucose reported in mmol/L with range 3.9 - 5.5 mmol/L
    low, high, raw = BiomarkerEntityNormalizer.parse_reference_range(
        CanonicalBiomarker.FASTING_BLOOD_GLUCOSE,
        "3.9 - 5.5 mmol/L",
        "mmol/L",
    )
    assert raw == "3.9 - 5.5 mmol/L"
    # 3.9 * 18.0156 = 70.26, 5.5 * 18.0156 = 99.09
    assert low == pytest.approx(70.26, abs=0.5)
    assert high == pytest.approx(99.09, abs=0.5)


def test_abnormality_flag_conflict_triggers_needs_review():
    """Verify report abnormality flag contradicting numerical range triggers NEEDS_REVIEW."""
    # Fasting glucose = 85.0 mg/dL (normal is 70-99), but laboratory flag says "H" (High)
    res = BiomarkerEntityNormalizer.normalize_biomarker_entry(
        raw_label="Fasting Blood Sugar",
        raw_value="85.0",
        raw_unit="mg/dL",
        raw_ref_range="70 - 99",
        raw_flag="H",  # Contradicts normal value!
    )
    assert res["validation_status"] == NormalizationStatus.NEEDS_REVIEW.value
    assert any("Flag conflict" in c for c in res["clinical_caveats"])
    assert res["abnormality_classification"] == AbnormalityFlag.NORMAL.value


def test_low_ocr_confidence_triggers_guard():
    """Verify OCR confidence below 60% flags LOW_OCR_CONFIDENCE."""
    res = BiomarkerEntityNormalizer.normalize_biomarker_entry(
        raw_label="Total Cholesterol",
        raw_value="185.0",
        raw_unit="mg/dL",
        ocr_confidence=52.4,  # Low confidence!
    )
    assert res["validation_status"] == NormalizationStatus.LOW_OCR_CONFIDENCE.value
    assert any("Low OCR confidence" in c for c in res["clinical_caveats"])


# =========================================================================
# 5. Batch Normalization & Downstream Consumer Integration Tests
# =========================================================================

def test_normalize_batch_full_provenance_and_downstream_dictionary():
    """Verify batch processing produces clean records, metrics, and canonical dictionary."""
    batch_items = [
        {
            "label": "Fasting B.S.",
            "value": "5.55",
            "unit": "mmol/L",
            "reference_range": "3.9 - 5.5 mmol/L",
            "ocr_confidence": 98.0,
        },
        {
            "label": "Cholesterol Tot.",
            "value": "210",
            "unit": "mg/dL",
            "reference_range": "< 200",
            "flag": "H",
            "ocr_confidence": 99.0,
        },
        {
            "label": "S. Creatinine",
            "value": "88.42",
            "unit": "µmol/L",
            "reference_range": "60 - 110",
            "ocr_confidence": 95.0,
        },
        {
            "label": "High-Sensitivity Troponin I",
            "value": "12.0",
            "unit": "ng/L",
            "ocr_confidence": 97.0,
        },
        {
            "label": "Unknown Exotic Test",
            "value": "45.0",
            "unit": "U/L",
            "ocr_confidence": 99.0,
        },
    ]

    result = BiomarkerEntityNormalizer.normalize_batch(
        extracted_items=batch_items,
        patient_id="patient-unit-test-01",
        source_document_id="doc-scan-001",
        lab_name="Chughtai Diagnostic Lab",
        specimen_collection_date="2026-11-01",
    )

    assert result["status"] == "success"
    assert result["total_extracted"] == 5
    assert result["normalized_count"] >= 3
    assert result["unmapped_count"] == 1

    canonical_dict = result["canonical_biomarkers_dict"]
    # Fasting glucose converted from 5.55 mmol/L -> ~100 mg/dL
    assert "fasting_blood_glucose_mg_dl" in canonical_dict
    assert canonical_dict["fasting_blood_glucose_mg_dl"] == pytest.approx(99.99, abs=0.1)

    # Total cholesterol
    assert "total_cholesterol_mg_dl" in canonical_dict
    assert canonical_dict["total_cholesterol_mg_dl"] == 210.0

    # Creatinine converted from 88.42 µmol/L -> 1.0 mg/dL
    assert "serum_creatinine_mg_dl" in canonical_dict
    assert canonical_dict["serum_creatinine_mg_dl"] == pytest.approx(1.0, abs=0.02)

    # Troponin converted from 12 ng/L -> 0.012 ng/mL
    assert "hs_troponin_i_ng_ml" in canonical_dict
    assert canonical_dict["hs_troponin_i_ng_ml"] == 0.012

    # Downstream compatibility aliases populated
    assert canonical_dict.get("cardiac_troponin_ng_ml") == 0.012
    assert canonical_dict.get("cardiac_troponin_assay") == "hs_cTnI"

    # Verify provenance fields on first record
    first_rec = result["records"][0]
    assert first_rec["patient_id"] == "patient-unit-test-01"
    assert first_rec["source_document_id"] == "doc-scan-001"
    assert first_rec["lab_name"] == "Chughtai Diagnostic Lab"
    assert first_rec["specimen_collection_date"] == "2026-11-01"
    assert first_rec["conversion_factor"] == 18.0156
    assert first_rec["normalizer_version"] == "1.0.0"
