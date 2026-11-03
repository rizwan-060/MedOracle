"""Clinical OCR Biomarker Normalization and Entity Disambiguation Engine (Step 8.4.3).

Responsibilities:
1. Canonical Entity Mapping: Resolves clinical acronyms, brand assays, and OCR typos to canonical identifiers.
2. Strict Assay Disambiguation: Delineates non-fungible biomarkers (BNP vs. NT-proBNP; Troponin I vs. T; hs vs. standard).
3. Unit Normalization: Deterministic molecular-weight and guideline-based unit conversions.
4. Reference Range Parsing: Extracts, standardizes, and converts reference intervals to canonical scales.
5. OCR Quality & Uncertainty: Flags low-confidence, unmapped, missing-unit, or ambiguous extractions.
6. Auditable Provenance: Preserves raw OCR tokens, conversion multipliers, and source metadata.
"""

from datetime import datetime, timezone
import logging
import math
import re
from typing import Any, Dict, List, Optional, Tuple, Union

from app.clinical.biomarker_types import (
    BIOMARKER_REGISTRY,
    AbnormalityFlag,
    BiomarkerMetadata,
    CanonicalBiomarker,
    NormalizationStatus,
)

logger = logging.getLogger("services.biomarker_normalizer")


class BiomarkerEntityNormalizer:
    """Enterprise-grade normalizer for laboratory biomarkers extracted via OCR or document ingestion."""

    VERSION = "1.0.0"

    # Strict multi-alias mapping dictionary
    SYNONYM_MAP: Dict[str, CanonicalBiomarker] = {
        # --- Glycemic ---
        "fasting blood glucose": CanonicalBiomarker.FASTING_BLOOD_GLUCOSE,
        "fasting glucose": CanonicalBiomarker.FASTING_BLOOD_GLUCOSE,
        "fasting plasma glucose": CanonicalBiomarker.FASTING_BLOOD_GLUCOSE,
        "fasting blood sugar": CanonicalBiomarker.FASTING_BLOOD_GLUCOSE,
        "fbg": CanonicalBiomarker.FASTING_BLOOD_GLUCOSE,
        "fpg": CanonicalBiomarker.FASTING_BLOOD_GLUCOSE,
        "fbs": CanonicalBiomarker.FASTING_BLOOD_GLUCOSE,
        "glucose fasting": CanonicalBiomarker.FASTING_BLOOD_GLUCOSE,
        "blood sugar fasting": CanonicalBiomarker.FASTING_BLOOD_GLUCOSE,
        "plasma glucose fasting": CanonicalBiomarker.FASTING_BLOOD_GLUCOSE,
        "glu f": CanonicalBiomarker.FASTING_BLOOD_GLUCOSE,
        "b s fasting": CanonicalBiomarker.FASTING_BLOOD_GLUCOSE,
        "bs fasting": CanonicalBiomarker.FASTING_BLOOD_GLUCOSE,
        "s glucose fasting": CanonicalBiomarker.FASTING_BLOOD_GLUCOSE,
        "serum glucose fasting": CanonicalBiomarker.FASTING_BLOOD_GLUCOSE,

        "random blood glucose": CanonicalBiomarker.RANDOM_BLOOD_GLUCOSE,
        "random glucose": CanonicalBiomarker.RANDOM_BLOOD_GLUCOSE,
        "random blood sugar": CanonicalBiomarker.RANDOM_BLOOD_GLUCOSE,
        "rbs": CanonicalBiomarker.RANDOM_BLOOD_GLUCOSE,
        "bsr": CanonicalBiomarker.RANDOM_BLOOD_GLUCOSE,
        "glucose random": CanonicalBiomarker.RANDOM_BLOOD_GLUCOSE,
        "blood sugar random": CanonicalBiomarker.RANDOM_BLOOD_GLUCOSE,

        "hba1c": CanonicalBiomarker.HBA1C,
        "a1c": CanonicalBiomarker.HBA1C,
        "glycated hemoglobin": CanonicalBiomarker.HBA1C,
        "glycohemoglobin": CanonicalBiomarker.HBA1C,
        "hemoglobin a1c": CanonicalBiomarker.HBA1C,
        "glycosylated hemoglobin": CanonicalBiomarker.HBA1C,
        "hba1c percent": CanonicalBiomarker.HBA1C,
        "fraction a1c": CanonicalBiomarker.HBA1C,

        # --- Lipids ---
        "total cholesterol": CanonicalBiomarker.TOTAL_CHOLESTEROL,
        "cholesterol total": CanonicalBiomarker.TOTAL_CHOLESTEROL,
        "serum cholesterol": CanonicalBiomarker.TOTAL_CHOLESTEROL,
        "total chol": CanonicalBiomarker.TOTAL_CHOLESTEROL,
        "chol tot": CanonicalBiomarker.TOTAL_CHOLESTEROL,
        "cholesterol tot": CanonicalBiomarker.TOTAL_CHOLESTEROL,
        "tc": CanonicalBiomarker.TOTAL_CHOLESTEROL,
        "s cholesterol": CanonicalBiomarker.TOTAL_CHOLESTEROL,
        "cholesterol": CanonicalBiomarker.TOTAL_CHOLESTEROL,  # Defaults to Total if qualified as lipid profile header

        "ldl cholesterol": CanonicalBiomarker.LDL_CHOLESTEROL,
        "ldl c": CanonicalBiomarker.LDL_CHOLESTEROL,
        "ldl": CanonicalBiomarker.LDL_CHOLESTEROL,
        "low density lipoprotein": CanonicalBiomarker.LDL_CHOLESTEROL,
        "low density lipoprotein cholesterol": CanonicalBiomarker.LDL_CHOLESTEROL,
        "cholesterol ldl": CanonicalBiomarker.LDL_CHOLESTEROL,
        "direct ldl": CanonicalBiomarker.LDL_CHOLESTEROL,
        "calculated ldl": CanonicalBiomarker.LDL_CHOLESTEROL,
        "s ldl": CanonicalBiomarker.LDL_CHOLESTEROL,

        "hdl cholesterol": CanonicalBiomarker.HDL_CHOLESTEROL,
        "hdl c": CanonicalBiomarker.HDL_CHOLESTEROL,
        "hdl": CanonicalBiomarker.HDL_CHOLESTEROL,
        "high density lipoprotein": CanonicalBiomarker.HDL_CHOLESTEROL,
        "high density lipoprotein cholesterol": CanonicalBiomarker.HDL_CHOLESTEROL,
        "cholesterol hdl": CanonicalBiomarker.HDL_CHOLESTEROL,
        "direct hdl": CanonicalBiomarker.HDL_CHOLESTEROL,
        "s hdl": CanonicalBiomarker.HDL_CHOLESTEROL,

        "triglycerides": CanonicalBiomarker.TRIGLYCERIDES,
        "serum triglycerides": CanonicalBiomarker.TRIGLYCERIDES,
        "tg": CanonicalBiomarker.TRIGLYCERIDES,
        "trig": CanonicalBiomarker.TRIGLYCERIDES,
        "trigs": CanonicalBiomarker.TRIGLYCERIDES,
        "triacylglycerol": CanonicalBiomarker.TRIGLYCERIDES,
        "s triglycerides": CanonicalBiomarker.TRIGLYCERIDES,

        # --- Renal & Metabolic ---
        "serum creatinine": CanonicalBiomarker.SERUM_CREATININE,
        "creatinine": CanonicalBiomarker.SERUM_CREATININE,
        "scr": CanonicalBiomarker.SERUM_CREATININE,
        "s creatinine": CanonicalBiomarker.SERUM_CREATININE,
        "crea": CanonicalBiomarker.SERUM_CREATININE,
        "serum creat": CanonicalBiomarker.SERUM_CREATININE,
        "blood creatinine": CanonicalBiomarker.SERUM_CREATININE,

        "egfr": CanonicalBiomarker.ESTIMATED_GFR,
        "estimated gfr": CanonicalBiomarker.ESTIMATED_GFR,
        "glomerular filtration rate": CanonicalBiomarker.ESTIMATED_GFR,
        "estimated glomerular filtration rate": CanonicalBiomarker.ESTIMATED_GFR,
        "ckd epi egfr": CanonicalBiomarker.ESTIMATED_GFR,
        "gfr estimated": CanonicalBiomarker.ESTIMATED_GFR,

        "blood urea nitrogen": CanonicalBiomarker.BLOOD_UREA_NITROGEN,
        "bun": CanonicalBiomarker.BLOOD_UREA_NITROGEN,
        "urea nitrogen": CanonicalBiomarker.BLOOD_UREA_NITROGEN,
        "serum urea nitrogen": CanonicalBiomarker.BLOOD_UREA_NITROGEN,
        "urea": CanonicalBiomarker.BLOOD_UREA_NITROGEN,

        # --- Cardiac Biomarkers (Strict Separation) ---
        "bnp": CanonicalBiomarker.BNP,
        "b type natriuretic peptide": CanonicalBiomarker.BNP,
        "brain natriuretic peptide": CanonicalBiomarker.BNP,
        "serum bnp": CanonicalBiomarker.BNP,

        "nt probnp": CanonicalBiomarker.NT_PROBNP,
        "nt pro bnp": CanonicalBiomarker.NT_PROBNP,
        "n terminal probnp": CanonicalBiomarker.NT_PROBNP,
        "n terminal pro b type natriuretic peptide": CanonicalBiomarker.NT_PROBNP,
        "pro bnp": CanonicalBiomarker.NT_PROBNP,
        "pro b type natriuretic peptide": CanonicalBiomarker.NT_PROBNP,

        "troponin i": CanonicalBiomarker.TROPONIN_I,
        "cardiac troponin i": CanonicalBiomarker.TROPONIN_I,
        "ctni": CanonicalBiomarker.TROPONIN_I,
        "trop i": CanonicalBiomarker.TROPONIN_I,
        "s ctni": CanonicalBiomarker.TROPONIN_I,

        "troponin t": CanonicalBiomarker.TROPONIN_T,
        "cardiac troponin t": CanonicalBiomarker.TROPONIN_T,
        "ctnt": CanonicalBiomarker.TROPONIN_T,
        "trop t": CanonicalBiomarker.TROPONIN_T,
        "s ctnt": CanonicalBiomarker.TROPONIN_T,

        "hs ctni": CanonicalBiomarker.HS_TROPONIN_I,
        "hs troponin i": CanonicalBiomarker.HS_TROPONIN_I,
        "high sensitivity troponin i": CanonicalBiomarker.HS_TROPONIN_I,
        "high sensitivity cardiac troponin i": CanonicalBiomarker.HS_TROPONIN_I,
        "hs cardiac troponin i": CanonicalBiomarker.HS_TROPONIN_I,

        "hs ctnt": CanonicalBiomarker.HS_TROPONIN_T,
        "hs troponin t": CanonicalBiomarker.HS_TROPONIN_T,
        "high sensitivity troponin t": CanonicalBiomarker.HS_TROPONIN_T,
        "high sensitivity cardiac troponin t": CanonicalBiomarker.HS_TROPONIN_T,
        "hs cardiac troponin t": CanonicalBiomarker.HS_TROPONIN_T,

        # --- Hematology ---
        "hemoglobin": CanonicalBiomarker.HEMOGLOBIN,
        "haemoglobin": CanonicalBiomarker.HEMOGLOBIN,
        "hb": CanonicalBiomarker.HEMOGLOBIN,
        "hgb": CanonicalBiomarker.HEMOGLOBIN,
        "blood hemoglobin": CanonicalBiomarker.HEMOGLOBIN,

        "wbc": CanonicalBiomarker.WBC_COUNT,
        "white blood cell count": CanonicalBiomarker.WBC_COUNT,
        "white blood cells": CanonicalBiomarker.WBC_COUNT,
        "total leucocyte count": CanonicalBiomarker.WBC_COUNT,
        "total leukocyte count": CanonicalBiomarker.WBC_COUNT,
        "tlc": CanonicalBiomarker.WBC_COUNT,
        "leukocytes": CanonicalBiomarker.WBC_COUNT,
        "wbc count": CanonicalBiomarker.WBC_COUNT,

        "platelets": CanonicalBiomarker.PLATELETS_COUNT,
        "platelet count": CanonicalBiomarker.PLATELETS_COUNT,
        "plt": CanonicalBiomarker.PLATELETS_COUNT,
        "thrombocytes": CanonicalBiomarker.PLATELETS_COUNT,
        "platelet": CanonicalBiomarker.PLATELETS_COUNT,

        # --- Hepatic ---
        "alt": CanonicalBiomarker.ALT,
        "alanine aminotransferase": CanonicalBiomarker.ALT,
        "sgpt": CanonicalBiomarker.ALT,
        "serum glutamic pyruvic transaminase": CanonicalBiomarker.ALT,
        "alanine transaminase": CanonicalBiomarker.ALT,
        "s alt": CanonicalBiomarker.ALT,

        "ast": CanonicalBiomarker.AST,
        "aspartate aminotransferase": CanonicalBiomarker.AST,
        "sgot": CanonicalBiomarker.AST,
        "serum glutamic oxaloacetic transaminase": CanonicalBiomarker.AST,
        "aspartate transaminase": CanonicalBiomarker.AST,
        "s ast": CanonicalBiomarker.AST,

        # --- Electrolytes ---
        "sodium": CanonicalBiomarker.SODIUM,
        "serum sodium": CanonicalBiomarker.SODIUM,
        "na": CanonicalBiomarker.SODIUM,
        "na+": CanonicalBiomarker.SODIUM,
        "s sodium": CanonicalBiomarker.SODIUM,

        "potassium": CanonicalBiomarker.POTASSIUM,
        "serum potassium": CanonicalBiomarker.POTASSIUM,
        "k": CanonicalBiomarker.POTASSIUM,
        "k+": CanonicalBiomarker.POTASSIUM,
        "s potassium": CanonicalBiomarker.POTASSIUM,

        # --- Vitals ---
        "systolic bp": CanonicalBiomarker.SYSTOLIC_BP,
        "sbp": CanonicalBiomarker.SYSTOLIC_BP,
        "systolic blood pressure": CanonicalBiomarker.SYSTOLIC_BP,
        "systolic": CanonicalBiomarker.SYSTOLIC_BP,
        "bp systolic": CanonicalBiomarker.SYSTOLIC_BP,

        "diastolic bp": CanonicalBiomarker.DIASTOLIC_BP,
        "dbp": CanonicalBiomarker.DIASTOLIC_BP,
        "diastolic blood pressure": CanonicalBiomarker.DIASTOLIC_BP,
        "diastolic": CanonicalBiomarker.DIASTOLIC_BP,
        "bp diastolic": CanonicalBiomarker.DIASTOLIC_BP,
    }

    # Ambiguous clinical labels requiring explicit context or disambiguation
    AMBIGUOUS_LABELS: Dict[str, str] = {
        "troponin": "Unspecified Troponin assay (cannot differentiate Troponin I vs. Troponin T or conventional vs. high-sensitivity hs-cTn)",
        "natriuretic peptide": "Unspecified Natriuretic Peptide (cannot differentiate active BNP from inactive NT-proBNP)",
        "transaminase": "Unspecified Transaminase (cannot differentiate ALT/SGPT from AST/SGOT)",
    }

    # Qualitative clinical outcome keywords
    QUALITATIVE_PATTERNS = {
        "negative", "non reactive", "nonreactive", "normal", "nil", "trace",
        "positive", "reactive", "abnormal", "detected", "not detected", "present", "absent"
    }

    @classmethod
    def clean_string(cls, text: str) -> str:
        """Sanitize raw text token for robust dictionary matching."""
        if not text:
            return ""
        s = text.lower().strip()
        # Remove common lab punctuation
        s = re.sub(r"[\(\)\[\]\{\}\:\;\,\.\-_/]", " ", s)
        s = re.sub(r"\s+", " ", s).strip()
        return s

    @classmethod
    def map_biomarker_entity(cls, raw_label: str) -> Tuple[Optional[CanonicalBiomarker], float, NormalizationStatus, Optional[str]]:
        """Map raw test label string to canonical biomarker identifier.

        Returns:
            Tuple of (canonical_biomarker, mapping_confidence, status, ambiguity_reason)
        """
        if not raw_label or not raw_label.strip():
            return None, 0.0, NormalizationStatus.UNMAPPED, "Empty or unreadable biomarker label"

        cleaned = cls.clean_string(raw_label)

        # Check explicit ambiguous terms first
        for amb_key, reason in cls.AMBIGUOUS_LABELS.items():
            if cleaned == amb_key or cleaned == cls.clean_string(amb_key):
                return None, 0.5, NormalizationStatus.AMBIGUOUS_BIOMARKER, reason

        # 1. Exact match in synonym registry
        if cleaned in cls.SYNONYM_MAP:
            return cls.SYNONYM_MAP[cleaned], 1.0, NormalizationStatus.NORMALIZED, None

        # 2. Token boundary search for key multi-word phrases
        # Check high-sensitivity troponins before standard troponins
        if ("hs" in cleaned or "high sensitivity" in cleaned) and ("ctni" in cleaned or "troponin i" in cleaned):
            return CanonicalBiomarker.HS_TROPONIN_I, 0.95, NormalizationStatus.NORMALIZED, None
        if ("hs" in cleaned or "high sensitivity" in cleaned) and ("ctnt" in cleaned or "troponin t" in cleaned):
            return CanonicalBiomarker.HS_TROPONIN_T, 0.95, NormalizationStatus.NORMALIZED, None
        if "nt probnp" in cleaned or "n terminal" in cleaned or "pro bnp" in cleaned:
            return CanonicalBiomarker.NT_PROBNP, 0.95, NormalizationStatus.NORMALIZED, None
        if "bnp" in cleaned and "nt" not in cleaned and "pro" not in cleaned:
            return CanonicalBiomarker.BNP, 0.95, NormalizationStatus.NORMALIZED, None
        if "troponin i" in cleaned or "ctni" in cleaned:
            return CanonicalBiomarker.TROPONIN_I, 0.92, NormalizationStatus.NORMALIZED, None
        if "troponin t" in cleaned or "ctnt" in cleaned:
            return CanonicalBiomarker.TROPONIN_T, 0.92, NormalizationStatus.NORMALIZED, None

        # Glycemic phrases
        if "fasting" in cleaned and ("glucose" in cleaned or "sugar" in cleaned or "b s" in cleaned or re.search(r"\b(bs|fbs|fbg|fpg|glu)\b", cleaned)):
            return CanonicalBiomarker.FASTING_BLOOD_GLUCOSE, 0.95, NormalizationStatus.NORMALIZED, None
        if "random" in cleaned and ("glucose" in cleaned or "sugar" in cleaned or "b s" in cleaned or re.search(r"\b(bs|rbs|glu)\b", cleaned)):
            return CanonicalBiomarker.RANDOM_BLOOD_GLUCOSE, 0.95, NormalizationStatus.NORMALIZED, None
        if "hba1c" in cleaned or "glycated" in cleaned or "a1c" in cleaned:
            return CanonicalBiomarker.HBA1C, 0.95, NormalizationStatus.NORMALIZED, None

        # Lipids phrases
        if "triglyceride" in cleaned or "triacylglycerol" in cleaned:
            return CanonicalBiomarker.TRIGLYCERIDES, 0.95, NormalizationStatus.NORMALIZED, None
        if "ldl" in cleaned and "cholesterol" in cleaned:
            return CanonicalBiomarker.LDL_CHOLESTEROL, 0.95, NormalizationStatus.NORMALIZED, None
        if "hdl" in cleaned and "cholesterol" in cleaned:
            return CanonicalBiomarker.HDL_CHOLESTEROL, 0.95, NormalizationStatus.NORMALIZED, None
        if ("total" in cleaned or "tot" in cleaned) and "cholesterol" in cleaned:
            return CanonicalBiomarker.TOTAL_CHOLESTEROL, 0.95, NormalizationStatus.NORMALIZED, None

        # Renal phrases
        if "creatinine" in cleaned or re.search(r"\bcrea\b", cleaned):
            return CanonicalBiomarker.SERUM_CREATININE, 0.92, NormalizationStatus.NORMALIZED, None
        if "egfr" in cleaned or "glomerular filtration" in cleaned:
            return CanonicalBiomarker.ESTIMATED_GFR, 0.95, NormalizationStatus.NORMALIZED, None
        if "blood urea" in cleaned or re.search(r"\bbun\b", cleaned):
            return CanonicalBiomarker.BLOOD_UREA_NITROGEN, 0.92, NormalizationStatus.NORMALIZED, None

        # Hepatic phrases
        if re.search(r"\balt\b", cleaned) or "sgpt" in cleaned or "alanine" in cleaned:
            return CanonicalBiomarker.ALT, 0.92, NormalizationStatus.NORMALIZED, None
        if re.search(r"\bast\b", cleaned) or "sgot" in cleaned or "aspartate" in cleaned:
            return CanonicalBiomarker.AST, 0.92, NormalizationStatus.NORMALIZED, None

        # Electrolytes
        if "sodium" in cleaned or cleaned == "na" or cleaned.startswith("na "):
            return CanonicalBiomarker.SODIUM, 0.90, NormalizationStatus.NORMALIZED, None
        if "potassium" in cleaned or cleaned == "k" or cleaned.startswith("k "):
            return CanonicalBiomarker.POTASSIUM, 0.90, NormalizationStatus.NORMALIZED, None

        # Hematology
        if "hemoglobin" in cleaned or "haemoglobin" in cleaned or cleaned == "hb" or cleaned == "hgb":
            return CanonicalBiomarker.HEMOGLOBIN, 0.92, NormalizationStatus.NORMALIZED, None
        if "leucocyte" in cleaned or "leukocyte" in cleaned or "wbc" in cleaned or "tlc" in cleaned:
            return CanonicalBiomarker.WBC_COUNT, 0.90, NormalizationStatus.NORMALIZED, None
        if "platelet" in cleaned or "thrombocyte" in cleaned or cleaned == "plt":
            return CanonicalBiomarker.PLATELETS_COUNT, 0.90, NormalizationStatus.NORMALIZED, None

        # OCR Typo tolerance (single character transpositions / digit-letter substitutions)
        # e.g., 'c0lestrol' -> cholesterol; 'creatanine' -> creatinine; 'triqliserides' -> triglycerides
        typo_rules = [
            (r"c[0o]lest(?:[ea])?r[o0]l", CanonicalBiomarker.TOTAL_CHOLESTEROL, 0.82),
            (r"cr[ea]at[ia]n[ie]n[e]?", CanonicalBiomarker.SERUM_CREATININE, 0.85),
            (r"tr[iy][gq]l[yi][cs]?[ei]r[ie]d[es]?", CanonicalBiomarker.TRIGLYCERIDES, 0.82),
            (r"h[ae]em?ogl[o0]b[ie]n", CanonicalBiomarker.HEMOGLOBIN, 0.85),
            (r"hba1[\s\-]?[c0]", CanonicalBiomarker.HBA1C, 0.88),
            (r"gl[uo]c[o0]s[ea]", CanonicalBiomarker.FASTING_BLOOD_GLUCOSE, 0.80),
        ]
        for pattern, canon_id, conf in typo_rules:
            if re.search(pattern, cleaned):
                return canon_id, conf, NormalizationStatus.NORMALIZED, None

        return None, 0.0, NormalizationStatus.UNMAPPED, f"Unrecognized clinical biomarker label: '{raw_label}'"

    @classmethod
    def parse_numeric_value(
        cls, raw_val: Any, return_audit: bool = False
    ) -> Any:
        """Extract sanitized float, comparator, or qualitative description from OCR value token.

        When return_audit is True:
            Returns (cleaned_float, comparator, qualitative_str, audit_notes, is_ambiguous_locale)
        When return_audit is False (default):
            Returns (cleaned_float, comparator, qualitative_str)
        """
        if raw_val is None:
            return (None, None, None, [], False) if return_audit else (None, None, None)

        val_str = str(raw_val).strip()
        if not val_str:
            return (None, None, None, [], False) if return_audit else (None, None, None)

        clean_lower = cls.clean_string(val_str)
        if clean_lower in cls.QUALITATIVE_PATTERNS:
            return (None, None, val_str, [], False) if return_audit else (None, None, val_str)

        # Check for inequality prefix (<, <=, >, >=)
        comparator = None
        match_ineq = re.match(r"^([<>]=?)\s*(.*)$", val_str)
        if match_ineq:
            comparator = match_ineq.group(1)
            val_str = match_ineq.group(2).strip()

        # CLINICAL SAFETY: Do NOT calculate midpoints for range intervals (e.g., '100 - 120' or '3.5 - 5.0')!
        # Fabricating patient measurements from ranges is strictly prohibited.
        if "-" in val_str and not val_str.startswith("-"):
            audit_notes = [
                f"Raw value token '{val_str}' represents an interval range rather than a discrete observed patient measurement. "
                "Midpoint calculation is strictly prohibited to prevent fabricated clinical values."
            ]
            return (None, "interval_range", None, audit_notes, True) if return_audit else (None, "interval_range", None)

        # Clean number representation with auditable tracking
        clean_num, audit_notes, is_ambiguous_locale = cls.clean_number_string(val_str)
        try:
            num = float(clean_num)
            return (num, comparator, None, audit_notes, is_ambiguous_locale) if return_audit else (num, comparator, None)
        except (ValueError, TypeError):
            for qp in cls.QUALITATIVE_PATTERNS:
                if qp in clean_lower:
                    return (None, None, val_str, audit_notes, False) if return_audit else (None, None, val_str)
            return (None, None, None, audit_notes, False) if return_audit else (None, None, None)

    @classmethod
    def clean_number_string(cls, num_str: str) -> Tuple[str, List[str], bool]:
        """Resolve commas, period decimal points, and OCR glyph errors with full auditable tracking.

        Returns:
            Tuple of (cleaned_number_string, audit_notes, is_ambiguous_locale)
        """
        s = num_str.strip()
        audit_notes: List[str] = []
        is_ambiguous_locale = False

        # Replace common letter substitutions in numeric fields (O -> 0, l/I -> 1)
        if re.search(r"(?<=\d)[oO](?=\d)|^[oO](?=\d)|(?<=\d)[oO]$", s):
            s = re.sub(r"(?<=\d)[oO](?=\d)", "0", s)
            s = re.sub(r"^[oO](?=\d)", "0", s)
            s = re.sub(r"(?<=\d)[oO]$", "0", s)
            audit_notes.append("OCR glyph substitution: 'O'/'o' corrected to '0'")

        if re.search(r"(?<=\d)[lI](?=\d)|^[lI](?=\d)", s):
            s = re.sub(r"(?<=\d)[lI](?=\d)", "1", s)
            s = re.sub(r"^[lI](?=\d)", "1", s)
            audit_notes.append("OCR glyph substitution: 'l'/'I' corrected to '1'")

        # Handle European decimal comma vs. thousands comma
        # e.g., '1,25' -> '1.25'
        # e.g., '1,250.5' -> '1250.5'
        # e.g., '1.250,5' -> '1250.5'
        if "," in s and "." in s:
            if s.rfind(",") > s.rfind("."):
                # European format: 1.250,50
                s = s.replace(".", "").replace(",", ".")
                audit_notes.append("European numeric format: converted decimal comma to period")
            else:
                # US format: 1,250.50
                s = s.replace(",", "")
                audit_notes.append("US numeric format: stripped thousands comma separator")
        elif "," in s:
            parts = s.split(",")
            # Single comma followed by 1 or 2 digits is standard decimal comma (e.g. 1,25 -> 1.25)
            if len(parts) == 2 and len(parts[1]) in [1, 2]:
                s = s.replace(",", ".")
                audit_notes.append("Decimal comma converted to period")
            elif len(parts) == 2 and len(parts[1]) == 3:
                # Single comma with 3 digits and no dot: e.g. 1,250
                # Could be European 1.250 or US 1250 (potential 1000x difference)
                is_ambiguous_locale = True
                s = s.replace(",", "")
                audit_notes.append(f"Ambiguous single comma separator in '{num_str}': potential 1000x discrepancy across locales (flagged for review)")
            else:
                s = s.replace(",", "")

        # Strip remaining non-numeric characters except leading minus and decimal
        s = re.sub(r"[^\d\.\-]", "", s)
        return s, audit_notes, is_ambiguous_locale

    @classmethod
    def convert_unit(
        cls,
        biomarker: CanonicalBiomarker,
        val: float,
        unit_str: Optional[str],
    ) -> Tuple[Optional[float], str, float, str, NormalizationStatus]:
        """Convert biomarker value from source unit to canonical unit.

        Returns:
            Tuple of (normalized_val, canonical_unit, conversion_factor, method_desc, status)
        """
        meta = BIOMARKER_REGISTRY.get(biomarker)
        if not meta:
            return val, "", 1.0, "unknown_biomarker", NormalizationStatus.UNMAPPED

        canonical_unit = meta.canonical_unit

        if unit_str is None or not unit_str.strip():
            return None, canonical_unit, 0.0, "unit_missing", NormalizationStatus.MISSING_UNIT

        clean_unit = unit_str.lower().strip()
        clean_unit = clean_unit.replace("µ", "u").replace("μ", "u")
        clean_unit = re.sub(r"[\s\.\-_]", "", clean_unit)
        clean_canon = re.sub(r"[\s\.\-_]", "", canonical_unit.lower().replace("µ", "u").replace("μ", "u"))

        # Already canonical unit
        canon_candidates = [
            u.lower().replace(" ", "").replace(".", "").replace("µ", "u").replace("μ", "u")
            for u in meta.supported_units
            if u.lower().replace(" ", "").replace(".", "").replace("µ", "u").replace("μ", "u") == clean_canon
        ]
        if clean_unit == clean_canon or clean_unit in canon_candidates:
            return round(val, 4), canonical_unit, 1.0, "identity_canonical", NormalizationStatus.NORMALIZED

        # Validate dimensional compatibility
        supported_cleaned = {
            u.lower().replace(" ", "").replace(".", "").replace("_", "").replace("µ", "u").replace("μ", "u")
            for u in meta.supported_units
        }
        if clean_unit not in supported_cleaned:
            logger.warning("Incompatible unit '%s' for biomarker %s", unit_str, biomarker.value)
            return None, canonical_unit, 0.0, f"unsupported_unit_{unit_str}", NormalizationStatus.UNSUPPORTED_UNIT

        # -------------------------------------------------------------
        # Biomarker-Specific Conversion Rules
        # -------------------------------------------------------------

        # 1. Glycemic: mmol/L -> mg/dL (molecular weight D-glucose 180.156 g/mol)
        if biomarker in [CanonicalBiomarker.FASTING_BLOOD_GLUCOSE, CanonicalBiomarker.RANDOM_BLOOD_GLUCOSE]:
            if "mmol" in clean_unit:
                factor = 18.0156
                norm_val = round(val * factor, 2)
                return norm_val, canonical_unit, factor, "molecular_weight_180.156_ada", NormalizationStatus.NORMALIZED

        # 2. Glycated Hemoglobin: mmol/mol (IFCC) -> % (NGSP)
        # NGSP (%) = (0.09148 * IFCC [mmol/mol]) + 2.152
        if biomarker == CanonicalBiomarker.HBA1C:
            if "mmol/mol" in clean_unit or "mmolmol" in clean_unit:
                norm_val = round((0.09148 * val) + 2.152, 2)
                return norm_val, canonical_unit, 0.09148, "ifcc_to_ngsp_master_equation", NormalizationStatus.NORMALIZED
            if "%" in clean_unit or "percent" in clean_unit:
                return round(val, 2), canonical_unit, 1.0, "identity_canonical", NormalizationStatus.NORMALIZED

        # 3. Cholesterol Fractions (Total, LDL, HDL): mmol/L -> mg/dL (molecular weight cholesterol 386.654 g/mol)
        if biomarker in [CanonicalBiomarker.TOTAL_CHOLESTEROL, CanonicalBiomarker.LDL_CHOLESTEROL, CanonicalBiomarker.HDL_CHOLESTEROL]:
            if "mmol" in clean_unit:
                factor = 38.67
                norm_val = round(val * factor, 2)
                return norm_val, canonical_unit, factor, "molecular_weight_386.654_atp3", NormalizationStatus.NORMALIZED

        # 4. Triglycerides: mmol/L -> mg/dL (molecular weight triolein standard 885.4 g/mol)
        # CRITICAL: Distinct from cholesterol (88.54 vs 38.67)!
        if biomarker == CanonicalBiomarker.TRIGLYCERIDES:
            if "mmol" in clean_unit:
                factor = 88.54
                norm_val = round(val * factor, 2)
                return norm_val, canonical_unit, factor, "triolein_molecular_weight_885.4", NormalizationStatus.NORMALIZED

        # 5. Serum Creatinine: µmol/L / umol/L -> mg/dL (molecular weight creatinine 113.12 g/mol)
        # 1 mg/dL = 88.42 µmol/L => µmol/L / 88.42 = mg/dL (multiplier: 0.01131)
        if biomarker == CanonicalBiomarker.SERUM_CREATININE:
            if "umol" in clean_unit or "µmol" in clean_unit or "umoll" in clean_unit or "µmoll" in clean_unit:
                divisor = 88.42
                factor = round(1.0 / divisor, 6)
                norm_val = round(val / divisor, 3)
                return norm_val, canonical_unit, factor, "creatinine_molecular_weight_113.12_kdigo", NormalizationStatus.NORMALIZED

        # 6. Hemoglobin: g/L -> g/dL (factor 0.1) or mmol/L -> g/dL (factor 1.611)
        if biomarker == CanonicalBiomarker.HEMOGLOBIN:
            if clean_unit in ["gl", "g/l"]:
                factor = 0.1
                norm_val = round(val * factor, 2)
                return norm_val, canonical_unit, factor, "metric_g_per_L_to_g_per_dL", NormalizationStatus.NORMALIZED
            if "mmol" in clean_unit:
                factor = 1.611
                norm_val = round(val * factor, 2)
                return norm_val, canonical_unit, factor, "hemoglobin_monomer_mmol_L_to_g_dL", NormalizationStatus.NORMALIZED

        # 7. Electrolytes (Sodium, Potassium): mEq/L -> mmol/L (1:1 equivalence for monovalent ions)
        if biomarker in [CanonicalBiomarker.SODIUM, CanonicalBiomarker.POTASSIUM]:
            if "meq" in clean_unit:
                return round(val, 2), canonical_unit, 1.0, "monovalent_cation_equivalence", NormalizationStatus.NORMALIZED

        # 8. Blood Urea Nitrogen: mmol/L (Urea) -> mg/dL (BUN) (factor 2.80)
        if biomarker == CanonicalBiomarker.BLOOD_UREA_NITROGEN:
            if "mmol" in clean_unit:
                factor = 2.80
                norm_val = round(val * factor, 2)
                return norm_val, canonical_unit, factor, "urea_to_bun_molecular_nitrogen", NormalizationStatus.NORMALIZED

        # 9. Troponin Assays: ng/L or pg/mL -> ng/mL (or µg/L) (factor 0.001)
        if biomarker in [
            CanonicalBiomarker.TROPONIN_I, CanonicalBiomarker.TROPONIN_T,
            CanonicalBiomarker.HS_TROPONIN_I, CanonicalBiomarker.HS_TROPONIN_T
        ]:
            if clean_unit in ["ngl", "ng/l", "pgml", "pg/ml"]:
                factor = 0.001
                norm_val = round(val * factor, 5)
                return norm_val, canonical_unit, factor, "ng_L_to_ng_mL_metric", NormalizationStatus.NORMALIZED
            if clean_unit in ["µgl", "ugl", "µg/l", "ug/l"]:
                return round(val, 5), canonical_unit, 1.0, "identity_ug_per_L_equiv_ng_per_mL", NormalizationStatus.NORMALIZED

        # 10. Natriuretic Peptides (NT-proBNP): pmol/L -> pg/mL (molecular weight ~8457 Da, factor 8.457)
        if biomarker == CanonicalBiomarker.NT_PROBNP:
            if "pmol" in clean_unit:
                factor = 8.457
                norm_val = round(val * factor, 2)
                return norm_val, canonical_unit, factor, "nt_probnp_molecular_weight_8457", NormalizationStatus.NORMALIZED
            if clean_unit in ["ngl", "ng/l"]:
                return round(val, 2), canonical_unit, 1.0, "identity_pg_per_mL_equiv_ng_per_L", NormalizationStatus.NORMALIZED

        # 11. Complete Blood Count (WBC, Platelets): cells/mcL or /uL -> 10^3/µL
        if biomarker in [CanonicalBiomarker.WBC_COUNT, CanonicalBiomarker.PLATELETS_COUNT]:
            if clean_unit in ["cellsmcl", "cells/mcl", "/ul", "ul"]:
                factor = 0.001
                norm_val = round(val * factor, 2)
                return norm_val, canonical_unit, factor, "count_per_uL_to_thousands_per_uL", NormalizationStatus.NORMALIZED
            if clean_unit in ["10^9/l", "10^9l", "109l", "109/l"]:
                # 10^9/L == 10^3/µL (1:1 equivalent)
                return round(val, 2), canonical_unit, 1.0, "identity_10^9_per_L_equiv_10^3_per_uL", NormalizationStatus.NORMALIZED

        # 12. Liver Enzymes (ALT, AST): µkat/L -> U/L (factor 60.0)
        if biomarker in [CanonicalBiomarker.ALT, CanonicalBiomarker.AST]:
            if "kat" in clean_unit:
                factor = 60.0
                norm_val = round(val * factor, 2)
                return norm_val, canonical_unit, factor, "katal_to_international_units", NormalizationStatus.NORMALIZED
            if clean_unit in ["iul", "iu/l"]:
                return round(val, 2), canonical_unit, 1.0, "identity_IU_equiv_U", NormalizationStatus.NORMALIZED

        # 13. Blood Pressure: kPa -> mmHg (factor 7.50062)
        if biomarker in [CanonicalBiomarker.SYSTOLIC_BP, CanonicalBiomarker.DIASTOLIC_BP]:
            if "kpa" in clean_unit:
                factor = 7.50062
                norm_val = round(val * factor, 1)
                return norm_val, canonical_unit, factor, "kpa_to_mmhg_hydrostatic", NormalizationStatus.NORMALIZED
            if "torr" in clean_unit:
                return round(val, 1), canonical_unit, 1.0, "torr_to_mmhg_identity", NormalizationStatus.NORMALIZED

        return round(val, 4), canonical_unit, 1.0, "unmodified_pass_through", NormalizationStatus.NORMALIZED

    @classmethod
    def parse_reference_range(
        cls,
        biomarker: Optional[CanonicalBiomarker],
        range_str: Optional[str],
        source_unit: Optional[str],
    ) -> Tuple[Optional[float], Optional[float], Optional[str]]:
        """Extract low and high reference limits and convert to canonical unit if required.

        Returns:
            Tuple of (norm_low_bound, norm_high_bound, raw_range_cleaned)
        """
        if not range_str or not str(range_str).strip():
            return None, None, None

        raw = str(range_str).strip()
        low: Optional[float] = None
        high: Optional[float] = None

        # Check for range: '70 - 99' or '70.0 to 99.0' or '0.5-1.2'
        match_range = re.search(r"(\d+(?:\.\d+)?)\s*(?:-|to)\s*(\d+(?:\.\d+)?)", raw)
        if match_range:
            try:
                low = float(match_range.group(1))
                high = float(match_range.group(2))
            except ValueError:
                pass
        else:
            # Check for upper cutoff: '< 100' or '<= 100' or 'Up to 150'
            match_upper = re.search(r"(?:<|<=|up\s*to)\s*(\d+(?:\.\d+)?)", raw, re.IGNORECASE)
            if match_upper:
                try:
                    high = float(match_upper.group(1))
                except ValueError:
                    pass
            # Check for lower cutoff: '> 50' or '>= 50'
            match_lower = re.search(r"(?:>|>=)\s*(\d+(?:\.\d+)?)", raw)
            if match_lower:
                try:
                    low = float(match_lower.group(1))
                except ValueError:
                    pass

        # If biomarker and source unit are provided, convert reference bounds to canonical unit
        if biomarker and (low is not None or high is not None) and source_unit:
            if low is not None:
                norm_low, _, _, _, status = cls.convert_unit(biomarker, low, source_unit)
                if status == NormalizationStatus.NORMALIZED:
                    low = norm_low
            if high is not None:
                norm_high, _, _, _, status = cls.convert_unit(biomarker, high, source_unit)
                if status == NormalizationStatus.NORMALIZED:
                    high = norm_high

        return low, high, raw

    @classmethod
    def evaluate_abnormality(
        cls,
        biomarker: CanonicalBiomarker,
        normalized_val: Optional[float],
        ref_low: Optional[float],
        ref_high: Optional[float],
        raw_flag: Optional[str],
    ) -> Tuple[AbnormalityFlag, bool]:
        """Classify biological abnormality and detect conflicts between extracted flag and math range.

        Returns:
            Tuple of (abnormality_flag, has_conflicting_flag)
        """
        if normalized_val is None:
            return AbnormalityFlag.INDETERMINATE, False

        meta = BIOMARKER_REGISTRY.get(biomarker)
        computed_flag = AbnormalityFlag.NORMAL

        # Check critical cutoffs first
        if meta:
            if meta.critical_low_threshold is not None and normalized_val <= meta.critical_low_threshold:
                computed_flag = AbnormalityFlag.CRITICAL_LOW
            elif meta.critical_high_threshold is not None and normalized_val >= meta.critical_high_threshold:
                computed_flag = AbnormalityFlag.CRITICAL_HIGH

        if computed_flag == AbnormalityFlag.NORMAL:
            if ref_low is not None and normalized_val < ref_low:
                computed_flag = AbnormalityFlag.LOW
            elif ref_high is not None and normalized_val > ref_high:
                computed_flag = AbnormalityFlag.HIGH

        # Verify against raw flag if present
        has_conflict = False
        if raw_flag:
            rf = raw_flag.strip().upper()
            if rf in ["H", "HIGH", "ABNORMAL"] and computed_flag in [AbnormalityFlag.NORMAL, AbnormalityFlag.LOW]:
                # Extracted lab flag says high, but numerical value falls within or below reference range
                if ref_high is not None and normalized_val <= ref_high:
                    has_conflict = True
            elif rf in ["L", "LOW"] and computed_flag in [AbnormalityFlag.NORMAL, AbnormalityFlag.HIGH]:
                if ref_low is not None and normalized_val >= ref_low:
                    has_conflict = True

        return computed_flag, has_conflict

    @classmethod
    def normalize_biomarker_entry(
        cls,
        raw_label: str,
        raw_value: Any,
        raw_unit: Optional[str] = None,
        raw_ref_range: Optional[str] = None,
        raw_flag: Optional[str] = None,
        ocr_confidence: float = 100.0,
        patient_id: Optional[str] = None,
        source_document_id: Optional[str] = None,
        source_document_url: Optional[str] = None,
        lab_name: Optional[str] = None,
        specimen_collection_date: Optional[str] = None,
        report_date: Optional[str] = None,
        page_number: Optional[int] = None,
    ) -> Dict[str, Any]:
        """Execute full end-to-end clinical normalization pipeline for a single extracted biomarker entry."""
        # 1. Map Entity
        canonical_id, map_conf, map_status, amb_reason = cls.map_biomarker_entity(raw_label)

        # 2. Parse Value with auditable tracking
        num_val, comparator, qual_str, audit_notes, is_ambiguous_locale = cls.parse_numeric_value(raw_value, return_audit=True)

        # Initialize audit tracking
        clinical_caveats: List[str] = list(audit_notes)
        final_status = map_status

        if qual_str:
            final_status = NormalizationStatus.QUALITATIVE_VALUE
            clinical_caveats.append(f"Qualitative finding extracted: '{qual_str}'")

        if comparator == "interval_range":
            final_status = NormalizationStatus.NEEDS_REVIEW
            clinical_caveats.append(
                f"Extracted patient result token represents a range interval ('{raw_value}') rather than a discrete observed measurement. "
                "Midpoint calculation is strictly prohibited to prevent fabricated clinical values; flagged for clinical review."
            )

        if is_ambiguous_locale:
            final_status = NormalizationStatus.NEEDS_REVIEW
            clinical_caveats.append(
                f"Locale ambiguity detected in '{raw_value}': comma could represent decimal or thousands separator; flagged for clinical review."
            )

        if num_val is None and not qual_str and comparator != "interval_range":
            final_status = NormalizationStatus.INVALID_VALUE
            clinical_caveats.append(f"Unparseable numeric value: '{raw_value}'")

        if amb_reason:
            clinical_caveats.append(amb_reason)

        # 3. Unit Conversion & Plausibility
        norm_val: Optional[float] = None
        canon_unit = ""
        conv_factor = 1.0
        conv_method = "unconverted"

        if canonical_id and num_val is not None:
            norm_val, canon_unit, conv_factor, conv_method, unit_status = cls.convert_unit(
                canonical_id, num_val, raw_unit
            )
            if unit_status != NormalizationStatus.NORMALIZED:
                final_status = unit_status
                clinical_caveats.append(f"Unit issue: {unit_status.value} for raw unit '{raw_unit}'")
            elif final_status == NormalizationStatus.NORMALIZED:
                final_status = NormalizationStatus.NORMALIZED

            # Biological plausibility validation
            meta = BIOMARKER_REGISTRY.get(canonical_id)
            if meta and norm_val is not None:
                if meta.min_biological_value is not None and norm_val < meta.min_biological_value:
                    final_status = NormalizationStatus.NEEDS_REVIEW
                    clinical_caveats.append(f"Value {norm_val} {canon_unit} is below extreme biological limit ({meta.min_biological_value})")
                elif meta.max_biological_value is not None and norm_val > meta.max_biological_value:
                    final_status = NormalizationStatus.NEEDS_REVIEW
                    clinical_caveats.append(f"Value {norm_val} {canon_unit} exceeds extreme biological limit ({meta.max_biological_value})")
        elif canonical_id:
            meta = BIOMARKER_REGISTRY.get(canonical_id)
            if meta:
                canon_unit = meta.canonical_unit

        # 4. Reference Range & Abnormality
        ref_low, ref_high, clean_range_str = cls.parse_reference_range(canonical_id, raw_ref_range, raw_unit)
        abnormality_flag = AbnormalityFlag.INDETERMINATE

        if canonical_id and norm_val is not None:
            abnormality_flag, flag_conflict = cls.evaluate_abnormality(
                canonical_id, norm_val, ref_low, ref_high, raw_flag
            )
            if flag_conflict:
                final_status = NormalizationStatus.NEEDS_REVIEW
                clinical_caveats.append(f"Flag conflict: laboratory flag '{raw_flag}' contradicts calculated range bounds ({ref_low}-{ref_high})")

        # 5. Low OCR Confidence Check
        if ocr_confidence < 60.0:
            if final_status == NormalizationStatus.NORMALIZED:
                final_status = NormalizationStatus.LOW_OCR_CONFIDENCE
            clinical_caveats.append(f"Low OCR confidence extraction: {ocr_confidence:.1f}%")

        # 6. Provenance & Audit Record
        return {
            "patient_id": patient_id,
            "source_document_id": source_document_id,
            "source_document_url": source_document_url,
            "lab_name": lab_name,
            "original_label": raw_label,
            "canonical_id": canonical_id.value if canonical_id else None,
            "display_name": BIOMARKER_REGISTRY[canonical_id].display_name if canonical_id else raw_label,
            "original_value_raw": str(raw_value),
            "original_numeric_value": num_val,
            "original_unit": raw_unit,
            "comparator": comparator,
            "qualitative_value": qual_str,
            "normalized_value": norm_val,
            "canonical_unit": canon_unit,
            "conversion_factor": conv_factor,
            "conversion_method": conv_method,
            "reference_range_raw": clean_range_str,
            "reference_range_low": ref_low,
            "reference_range_high": ref_high,
            "abnormal_flag_raw": raw_flag,
            "abnormality_classification": abnormality_flag.value,
            "ocr_confidence": round(ocr_confidence, 2),
            "mapping_confidence": round(map_conf, 2),
            "validation_status": final_status.value,
            "clinical_caveats": clinical_caveats,
            "specimen_collection_date": specimen_collection_date,
            "report_date": report_date,
            "page_number": page_number,
            "normalized_at": datetime.now(timezone.utc).isoformat(),
            "normalizer_version": cls.VERSION,
        }

    @classmethod
    def normalize_batch(
        cls,
        extracted_items: List[Dict[str, Any]],
        patient_id: Optional[str] = None,
        source_document_id: Optional[str] = None,
        source_document_url: Optional[str] = None,
        lab_name: Optional[str] = None,
        specimen_collection_date: Optional[str] = None,
        report_date: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Process batch of OCR extracted biomarkers and generate standardized canonical payload.

        Returns:
            Dict containing:
            - normalized_records: List of detailed provenance records
            - canonical_biomarkers_dict: Key-value map suitable for downstream ML/risk models
            - metrics: Summary count metrics for quality assurance
        """
        normalized_records: List[Dict[str, Any]] = []
        canonical_dict: Dict[str, float] = {}

        total_extracted = len(extracted_items)
        normalized_count = 0
        needs_review_count = 0
        unmapped_count = 0
        ambiguous_count = 0
        invalid_count = 0

        for item in extracted_items:
            record = cls.normalize_biomarker_entry(
                raw_label=item.get("label") or item.get("test_name") or "",
                raw_value=item.get("value") or item.get("result_value"),
                raw_unit=item.get("unit") or item.get("unit_of_measure"),
                raw_ref_range=item.get("reference_range") or item.get("ref_range"),
                raw_flag=item.get("flag") or item.get("abnormal_flag"),
                ocr_confidence=float(item.get("ocr_confidence") or item.get("confidence") or 100.0),
                patient_id=patient_id,
                source_document_id=source_document_id,
                source_document_url=source_document_url,
                lab_name=lab_name,
                specimen_collection_date=specimen_collection_date or item.get("collection_date"),
                report_date=report_date or item.get("report_date"),
                page_number=item.get("page_number"),
            )
            normalized_records.append(record)

            status = record["validation_status"]
            if status == NormalizationStatus.NORMALIZED.value:
                normalized_count += 1
                canon_id = record["canonical_id"]
                val = record["normalized_value"]
                if canon_id and val is not None:
                    # In case of duplicate biomarkers, preserve with warning
                    if canon_id in canonical_dict:
                        record["clinical_caveats"].append(
                            f"Multiple entries extracted for {canon_id}; latest/subsequent entry overwrote {canonical_dict[canon_id]}"
                        )
                        record["validation_status"] = NormalizationStatus.NEEDS_REVIEW.value
                        needs_review_count += 1
                    canonical_dict[canon_id] = val
            elif status == NormalizationStatus.NEEDS_REVIEW.value:
                needs_review_count += 1
                # If numeric value is present under review, still populate for clinician preview
                canon_id = record["canonical_id"]
                val = record["normalized_value"]
                if canon_id and val is not None and canon_id not in canonical_dict:
                    canonical_dict[canon_id] = val
            elif status == NormalizationStatus.UNMAPPED.value:
                unmapped_count += 1
            elif status == NormalizationStatus.AMBIGUOUS_BIOMARKER.value:
                ambiguous_count += 1
            else:
                invalid_count += 1

        # Provide downstream consumer compatibility keys for troponin ONLY when unambiguous
        troponin_assays_found = []
        if "hs_troponin_i_ng_ml" in canonical_dict:
            troponin_assays_found.append(("hs_cTnI", canonical_dict["hs_troponin_i_ng_ml"]))
        if "troponin_i_ng_ml" in canonical_dict:
            troponin_assays_found.append(("cTnI", canonical_dict["troponin_i_ng_ml"]))
        if "hs_troponin_t_ng_ml" in canonical_dict:
            troponin_assays_found.append(("hs_cTnT", canonical_dict["hs_troponin_t_ng_ml"]))
        if "troponin_t_ng_ml" in canonical_dict:
            troponin_assays_found.append(("cTnT", canonical_dict["troponin_t_ng_ml"]))

        if len(troponin_assays_found) == 1:
            canonical_dict["cardiac_troponin_assay"] = troponin_assays_found[0][0]
            canonical_dict["cardiac_troponin_ng_ml"] = troponin_assays_found[0][1]
        elif len(troponin_assays_found) > 1:
            logger.warning("Multiple distinct troponin assays present in report; generic alias suppressed to avoid conflation.")
            for r in normalized_records:
                if "troponin" in str(r.get("canonical_id")):
                    r["clinical_caveats"].append(
                        "Multiple distinct troponin assays present in batch; generic cardiac_troponin_ng_ml alias suppressed to avoid cross-assay conflation."
                    )

        return {
            "status": "success",
            "total_extracted": total_extracted,
            "normalized_count": normalized_count,
            "needs_review_count": needs_review_count,
            "unmapped_count": unmapped_count,
            "ambiguous_count": ambiguous_count,
            "invalid_count": invalid_count,
            "canonical_biomarkers_dict": canonical_dict,
            "records": normalized_records,
            "processed_at": datetime.now(timezone.utc).isoformat(),
        }
