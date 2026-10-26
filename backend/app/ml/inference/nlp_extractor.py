"""Clinical Natural Language Processing (NLP) Symptom Entity Extractor.

Extracts canonical symptom entities from unstructured clinical text using:
1. Exact and synonym phrase mapping against the 132-symptom clinical ontology.
2. Robust fuzzy string matching for typos (e.g., 'sore throught' -> 'throat_irritation').
3. Clinical negation detection (NegEx-style) to prevent negated symptoms ('no fever')
   from triggering positive diagnostic classification.
"""

from dataclasses import dataclass
import difflib
import logging
import re
from typing import Any, Dict, List, Optional, Set, Tuple

from app.ml.inference.ontology_manager import (
    CLINICAL_STOPWORDS,
    DynamicOntologyManager,
    UnmappedPhraseBuffer,
)

logger = logging.getLogger("nlp_extractor")


@dataclass
class ExtractedEntity:
    raw_mention: str
    canonical_symptom: str
    confidence: float
    match_type: str  # "exact", "synonym", "dynamic_synonym", "fuzzy_typo"
    is_negated: bool = False


# Negation trigger keywords (clinical NegEx patterns)
NEGATION_TRIGGERS: Set[str] = {
    "no",
    "not",
    "none",
    "denies",
    "denied",
    "without",
    "never",
    "free of",
    "negative for",
    "no evidence of",
    "absent",
    "rule out",
    "no signs of",
    "zero",
}

# Negation scope termination punctuation and adversative conjunctions
NEGATION_TERMINATORS: Set[str] = {
    ".",
    ";",
    "!",
    "?",
    "but",
    "however",
    "although",
    "except",
    "yet",
    "aside from",
    "apart from",
}

# Extensive clinical synonym dictionary mapping colloquial phrases to the 132 benchmark symptoms
CLINICAL_SYNONYMS: Dict[str, str] = {
    # Upper Respiratory / ENT
    "sore throat": "throat_irritation",
    "sore throught": "throat_irritation",
    "sore throt": "throat_irritation",
    "sore throate": "throat_irritation",
    "throat irritation": "throat_irritation",
    "scratchy throat": "throat_irritation",
    "throat pain": "throat_irritation",
    "painful throat": "throat_irritation",
    "hurts to swallow": "throat_irritation",
    "pharyngitis": "throat_irritation",
    "patches in throat": "patches_in_throat",
    "white spots on tonsils": "patches_in_throat",
    "white patches in throat": "patches_in_throat",
    "runny nose": "runny_nose",
    "running nose": "runny_nose",
    "rhinorrhea": "runny_nose",
    "stuffy nose": "congestion",
    "nasal congestion": "congestion",
    "blocked nose": "congestion",
    "congestion": "congestion",
    "sinus pressure": "sinus_pressure",
    "sinus pain": "sinus_pressure",
    "sneezing": "continuous_sneezing",
    "continuous sneezing": "continuous_sneezing",
    "frequent sneezing": "continuous_sneezing",
    "sneezing constantly": "continuous_sneezing",
    "loss of smell": "loss_of_smell",
    "anosmia": "loss_of_smell",
    "cannot smell": "loss_of_smell",
    "cough": "cough",
    "coughing": "cough",
    "dry cough": "cough",
    "hacking cough": "cough",
    "phlegm": "phlegm",
    "mucus": "phlegm",
    "mucoid sputum": "mucoid_sputum",
    "rusty sputum": "rusty_sputum",
    "blood in sputum": "blood_in_sputum",
    "hemoptysis": "blood_in_sputum",
    "coughing up blood": "blood_in_sputum",

    # Neurological / Sensory
    "headache": "headache",
    "severe headache": "headache",
    "head pain": "headache",
    "throbbing headache": "headache",
    "head pounding": "headache",
    "migraine": "headache",
    "cephalalgia": "headache",
    "dizziness": "dizziness",
    "dizzy": "dizziness",
    "lightheaded": "dizziness",
    "lightheadedness": "dizziness",
    "vertigo": "spinning_movements",
    "spinning": "spinning_movements",
    "spinning sensations": "spinning_movements",
    "loss of balance": "loss_of_balance",
    "unsteady": "unsteadiness",
    "unsteadiness": "unsteadiness",
    "stiff neck": "stiff_neck",
    "neck stiffness": "stiff_neck",
    "neck pain": "neck_pain",
    "altered sensorium": "altered_sensorium",
    "confusion": "altered_sensorium",
    "disorientation": "altered_sensorium",
    "lack of concentration": "lack_of_concentration",
    "brain fog": "lack_of_concentration",
    "visual disturbances": "visual_disturbances",
    "blurred vision": "blurred_and_distorted_vision",
    "distorted vision": "blurred_and_distorted_vision",
    "slurred speech": "slurred_speech",
    "weakness on one side": "weakness_of_one_body_side",
    "hemiparesis": "weakness_of_one_body_side",

    # Constitutional / Systemic
    "fever": "high_fever",
    "high fever": "high_fever",
    "burning up": "high_fever",
    "pyrexia": "high_fever",
    "elevated temperature": "high_fever",
    "mild fever": "mild_fever",
    "low grade fever": "mild_fever",
    "slight fever": "mild_fever",
    "chills": "chills",
    "feeling chilly": "chills",
    "shivering": "shivering",
    "sweating": "sweating",
    "night sweats": "sweating",
    "excessive sweating": "sweating",
    "cold sweats": "sweating",
    "fatigue": "fatigue",
    "feeling tired": "fatigue",
    "extreme tiredness": "fatigue",
    "exhaustion": "fatigue",
    "lethargy": "lethargy",
    "sluggishness": "lethargy",
    "malaise": "malaise",
    "feeling unwell": "malaise",
    "dehydration": "dehydration",
    "parched": "dehydration",
    "weight loss": "weight_loss",
    "losing weight": "weight_loss",
    "weight gain": "weight_gain",
    "gaining weight": "weight_gain",
    "anxiety": "anxiety",
    "nervousness": "anxiety",
    "restlessness": "restlessness",
    "depression": "depression",
    "irritability": "irritability",
    "mood swings": "mood_swings",

    # Gastrointestinal
    "nausea": "nausea",
    "nauseous": "nausea",
    "queasy": "nausea",
    "feeling sick to stomach": "nausea",
    "vomiting": "vomiting",
    "throwing up": "vomiting",
    "puking": "vomiting",
    "emesis": "vomiting",
    "stomach pain": "stomach_pain",
    "tummy ache": "stomach_pain",
    "stomach ache": "stomach_pain",
    "abdominal pain": "abdominal_pain",
    "belly pain": "belly_pain",
    "stomach cramps": "cramps",
    "cramps": "cramps",
    "acidity": "acidity",
    "heartburn": "acidity",
    "acid reflux": "acidity",
    "indigestion": "indigestion",
    "upset stomach": "indigestion",
    "dyspepsia": "indigestion",
    "diarrhea": "diarrhoea",
    "diarrhoea": "diarrhoea",
    "loose stools": "diarrhoea",
    "watery stools": "diarrhoea",
    "constipation": "constipation",
    "hard stools": "constipation",
    "loss of appetite": "loss_of_appetite",
    "poor appetite": "loss_of_appetite",
    "decreased appetite": "loss_of_appetite",
    "not hungry": "loss_of_appetite",
    "excessive hunger": "excessive_hunger",
    "polyphagia": "excessive_hunger",
    "passage of gases": "passage_of_gases",
    "flatulence": "passage_of_gases",
    "bloating": "distention_of_abdomen",
    "distention of abdomen": "distention_of_abdomen",
    "swelling of stomach": "swelling_of_stomach",
    "ulcers on tongue": "ulcers_on_tongue",
    "mouth ulcers": "ulcers_on_tongue",
    "canker sores": "ulcers_on_tongue",
    "stomach bleeding": "stomach_bleeding",
    "bloody stool": "bloody_stool",
    "blood in stool": "bloody_stool",

    # Cardiovascular / Respiratory
    "chest pain": "chest_pain",
    "angina": "chest_pain",
    "chest pressure": "chest_pain",
    "tightness in chest": "chest_pain",
    "chest tightness": "chest_pain",
    "breathlessness": "breathlessness",
    "shortness of breath": "breathlessness",
    "difficulty breathing": "breathlessness",
    "dyspnea": "breathlessness",
    "fast heart rate": "fast_heart_rate",
    "rapid heart rate": "fast_heart_rate",
    "tachycardia": "fast_heart_rate",
    "palpitations": "palpitations",
    "racing heart": "palpitations",

    # Dermatological
    "itching": "itching",
    "itchy": "itching",
    "pruritus": "itching",
    "skin rash": "skin_rash",
    "rash": "skin_rash",
    "red spots over body": "red_spots_over_body",
    "red spots": "red_spots_over_body",
    "skin peeling": "skin_peeling",
    "blister": "blister",
    "blisters": "blister",
    "pus filled pimples": "pus_filled_pimples",
    "pimples": "pus_filled_pimples",
    "blackheads": "blackheads",
    "scurring": "scurring",
    "bruising": "bruising",
    "bruises": "bruising",
    "yellowish skin": "yellowish_skin",
    "jaundice": "yellowish_skin",
    "yellowing of eyes": "yellowing_of_eyes",
    "yellow eyes": "yellowing_of_eyes",
    "sunken eyes": "sunken_eyes",
    "redness of eyes": "redness_of_eyes",
    "red eyes": "redness_of_eyes",
    "watering from eyes": "watering_from_eyes",
    "watery eyes": "watering_from_eyes",
    "pain behind the eyes": "pain_behind_the_eyes",
    "retro-orbital pain": "pain_behind_the_eyes",

    # Musculoskeletal
    "joint pain": "joint_pain",
    "hurting joints": "joint_pain",
    "arthralgia": "joint_pain",
    "knee pain": "knee_pain",
    "hip joint pain": "hip_joint_pain",
    "muscle pain": "muscle_pain",
    "muscle ache": "muscle_pain",
    "body ache": "muscle_pain",
    "myalgia": "muscle_pain",
    "back pain": "back_pain",
    "lower back pain": "back_pain",
    "swelling joints": "swelling_joints",
    "swollen joints": "swelling_joints",
    "movement stiffness": "movement_stiffness",
    "muscle weakness": "muscle_weakness",
    "weakness in limbs": "weakness_in_limbs",
    "painful walking": "painful_walking",
    "muscle wasting": "muscle_wasting",

    # Renal / Urological
    "burning urination": "burning_micturition",
    "burning micturition": "burning_micturition",
    "painful urination": "burning_micturition",
    "dysuria": "burning_micturition",
    "spotting urination": "spotting_urination",
    "dark urine": "dark_urine",
    "yellow urine": "yellow_urine",
    "foul smell of urine": "foul_smell_of_urine",
    "smelly urine": "foul_smell_of_urine",
    "continuous feel of urine": "continuous_feel_of_urine",
    "urinary urgency": "continuous_feel_of_urine",
    "frequent urination": "polyuria",
    "polyuria": "polyuria",
    "bladder discomfort": "bladder_discomfort",

    # Endocrine & Swelling
    "cold hands and feet": "cold_hands_and_feets",
    "cold hands and feets": "cold_hands_and_feets",
    "swollen legs": "swollen_legs",
    "swollen extremities": "swollen_extremeties",
    "swollen feet": "swollen_extremeties",
    "puffy face": "puffy_face_and_eyes",
    "puffy face and eyes": "puffy_face_and_eyes",
    "enlarged thyroid": "enlarged_thyroid",
    "goiter": "enlarged_thyroid",
    "swelled lymph nodes": "swelled_lymph_nodes",
    "swollen glands": "swelled_lymph_nodes",
    "brittle nails": "brittle_nails",
    "irregular sugar level": "irregular_sugar_level",
    "fluid overload": "fluid_overload",
}


class ClinicalSymptomExtractor:
    """Intelligent clinical entity extractor for free-text symptom narratives."""

    def __init__(
        self,
        known_symptoms: Optional[List[str]] = None,
        dynamic_ontology_manager: Optional[DynamicOntologyManager] = None,
        unmapped_buffer: Optional[UnmappedPhraseBuffer] = None,
    ):
        self.known_symptoms: Set[str] = set(known_symptoms) if known_symptoms else set()
        self.dynamic_ontology_manager = (
            dynamic_ontology_manager or DynamicOntologyManager.get_instance()
        )
        self.unmapped_buffer = (
            unmapped_buffer
            or UnmappedPhraseBuffer.get_instance(ontology_manager=self.dynamic_ontology_manager)
        )
        self._synonym_lookup: Dict[str, str] = {}
        self._dynamic_phrases: Set[str] = set()
        self._target_phrases: List[Tuple[str, str, int]] = []
        self.reload_dynamic_synonyms()

    def reload_dynamic_synonyms(self) -> None:
        """Rebuilds synonym lookup table incorporating static and dynamic ontology synonyms."""
        lookup: Dict[str, str] = {}
        dynamic_phrases: Set[str] = set()

        # 1. Direct canonical features
        for sym in self.known_symptoms:
            clean_sym = sym.replace("_", " ").lower()
            lookup[clean_sym] = sym
            lookup[sym] = sym

        # 2. Add curated static clinical synonyms
        for phrase, canonical in CLINICAL_SYNONYMS.items():
            if not self.known_symptoms or canonical in self.known_symptoms:
                lookup[phrase.lower()] = canonical

        # 3. Add dynamic ontology synonyms
        if self.dynamic_ontology_manager:
            for phrase, canonical in self.dynamic_ontology_manager.get_synonyms().items():
                if not self.known_symptoms or canonical in self.known_symptoms:
                    clean_phrase = phrase.lower()
                    lookup[clean_phrase] = canonical
                    dynamic_phrases.add(clean_phrase)

        self._synonym_lookup = lookup
        self._dynamic_phrases = dynamic_phrases

        # Pre-compile candidate search phrases sorted by token length descending (greedy multi-word matching)
        self._target_phrases = sorted(
            [(phrase, canonical, len(phrase.split())) for phrase, canonical in self._synonym_lookup.items()],
            key=lambda x: (x[2], len(x[0])),
            reverse=True,
        )
        logger.info(
            "Reloaded clinical ontology: %d total phrases (%d dynamic)",
            len(self._synonym_lookup),
            len(self._dynamic_phrases),
        )

    def extract(self, text: str, record_unmapped: bool = True) -> Dict[str, Any]:
        """Extracts canonical symptoms, applies typo correction, and respects clinical negation.

        Args:
            text: Unstructured narrative string provided by patient or clinician.
            record_unmapped: Whether unrecognized tokens should be logged to active learning buffer.

        Returns:
            Dict containing:
                - detected_symptoms: List of active, positive canonical symptom identifiers.
                - extracted_entities: List of detailed ExtractedEntity instances.
                - negated_symptoms: List of symptoms explicitly ruled out in text.
                - unrecognized_spans: List of unrecognized clinical-like terms.
        """
        if not text or not text.strip():
            return {
                "detected_symptoms": [],
                "extracted_entities": [],
                "negated_symptoms": [],
                "unrecognized_spans": [],
            }

        # Tokenize sentence into lowercased words while preserving punctuation boundaries
        tokens, token_spans = self._tokenize(text)
        total_tokens = len(tokens)

        detected_symptoms: Set[str] = set()
        negated_symptoms: Set[str] = set()
        extracted_entities: List[ExtractedEntity] = []
        matched_token_indices: Set[int] = set()

        # Phase 1: Multi-word & Single-word Exact and Synonym Matching
        for phrase, canonical, phrase_len in self._target_phrases:
            phrase_tokens = phrase.split()
            k = len(phrase_tokens)

            for i in range(total_tokens - k + 1):
                # Skip if any token in window is already matched
                if any(idx in matched_token_indices for idx in range(i, i + k)):
                    continue

                window_tokens = tokens[i : i + k]
                window_phrase = " ".join(window_tokens)

                if window_phrase == phrase:
                    # Check if governed by negation trigger
                    is_neg = self._is_negated(tokens, i)
                    for idx in range(i, i + k):
                        matched_token_indices.add(idx)

                    # Determine match category
                    if window_phrase in self._dynamic_phrases:
                        m_type = "dynamic_synonym"
                        confidence = 0.99
                    elif window_phrase == canonical.replace("_", " "):
                        m_type = "exact"
                        confidence = 1.0
                    else:
                        m_type = "synonym"
                        confidence = 0.98

                    entity = ExtractedEntity(
                        raw_mention=window_phrase,
                        canonical_symptom=canonical,
                        confidence=confidence,
                        match_type=m_type,
                        is_negated=is_neg,
                    )
                    extracted_entities.append(entity)

                    if is_neg:
                        negated_symptoms.add(canonical)
                    else:
                        detected_symptoms.add(canonical)

        # Phase 2: Fuzzy Typo-Tolerant Matching for remaining unassigned spans
        # Checks 1-word, 2-word, and 3-word combinations against clinical phrases
        for k in [3, 2, 1]:
            for i in range(total_tokens - k + 1):
                if any(idx in matched_token_indices for idx in range(i, i + k)):
                    continue

                window_tokens = tokens[i : i + k]
                window_phrase = " ".join(window_tokens)

                # Skip trivial stopword windows
                if window_phrase in {"i am", "from the", "i also", "and a", "have a", "the past"}:
                    continue

                best_match, best_score, best_canonical = self._find_best_fuzzy_match(window_phrase)
                # Robust threshold (0.80) to capture clinical misspellings while guarding against spurious matches
                if best_match and best_score >= 0.80:
                    is_neg = self._is_negated(tokens, i)
                    for idx in range(i, i + k):
                        matched_token_indices.add(idx)

                    entity = ExtractedEntity(
                        raw_mention=window_phrase,
                        canonical_symptom=best_canonical,
                        confidence=round(best_score, 2),
                        match_type="fuzzy_typo",
                        is_negated=is_neg,
                    )
                    extracted_entities.append(entity)

                    if is_neg:
                        negated_symptoms.add(best_canonical)
                    else:
                        detected_symptoms.add(best_canonical)

        # Phase 3: Identify unrecognized clinical phrases / active learning candidates
        unrecognized_spans: List[str] = []
        i = 0
        while i < total_tokens:
            # Skip matched tokens, punctuation, and stopwords
            if (
                i in matched_token_indices
                or tokens[i] in {".", ",", "!", "?", ";", "-", ":"}
                or tokens[i] in CLINICAL_STOPWORDS
                or len(tokens[i]) < 3
            ):
                i += 1
                continue

            # Gather contiguous slice of unmatched non-stopword tokens
            chunk_tokens = []
            while (
                i < total_tokens
                and i not in matched_token_indices
                and tokens[i] not in {".", ",", "!", "?", ";", "-", ":"}
                and tokens[i] not in CLINICAL_STOPWORDS
                and len(tokens[i]) >= 2
            ):
                chunk_tokens.append(tokens[i])
                i += 1

            chunk_len = len(chunk_tokens)
            if chunk_len > 0:
                full_phrase = " ".join(chunk_tokens)
                if full_phrase not in unrecognized_spans:
                    unrecognized_spans.append(full_phrase)

                # Add 2-grams and 3-grams for multi-word candidate detection
                for n in [2, 3]:
                    if chunk_len >= n:
                        for j in range(chunk_len - n + 1):
                            ngram = " ".join(chunk_tokens[j : j + n])
                            if ngram not in unrecognized_spans:
                                unrecognized_spans.append(ngram)

        # Buffer unmapped phrases for active learning if requested
        if record_unmapped and self.unmapped_buffer:
            for phrase in unrecognized_spans:
                self.unmapped_buffer.record_unmapped_phrase(phrase, reference_lexicon=self._synonym_lookup)

        # Do not include negated symptoms in positive diagnostic vector
        positive_symptoms = [s for s in sorted(detected_symptoms) if s not in negated_symptoms]

        return {
            "detected_symptoms": positive_symptoms,
            "extracted_entities": [
                {
                    "raw_mention": e.raw_mention,
                    "canonical_symptom": e.canonical_symptom,
                    "confidence": e.confidence,
                    "match_type": e.match_type,
                    "is_negated": e.is_negated,
                }
                for e in extracted_entities
            ],
            "negated_symptoms": sorted(negated_symptoms),
            "unrecognized_spans": unrecognized_spans,
        }

    def register_dynamic_synonym(
        self,
        phrase: str,
        canonical_symptom: str,
        clinical_notes: Optional[str] = None,
        source: str = "clinician_approval",
    ) -> bool:
        """Register a new colloquial phrase mapping to a canonical symptom and hot-reload."""
        clean_canonical = canonical_symptom.strip().lower()
        if self.known_symptoms and clean_canonical not in self.known_symptoms:
            raise ValueError(
                f"Unknown canonical symptom '{canonical_symptom}'. Must be one of 132 benchmark symptoms."
            )

        success = self.dynamic_ontology_manager.register_synonym(
            phrase=phrase,
            canonical_symptom=clean_canonical,
            clinical_notes=clinical_notes,
            source=source,
        )
        if success:
            if self.unmapped_buffer:
                self.unmapped_buffer.resolve_unmapped_phrase(phrase)
            self.reload_dynamic_synonyms()
        return success

    def get_ontology_overview(self) -> Dict[str, Any]:
        """Return catalog of active clinical ontology and dynamic synonyms."""
        return {
            "total_canonical_symptoms": len(self.known_symptoms),
            "canonical_symptoms": sorted(list(self.known_symptoms)),
            "total_synonyms": len(self._synonym_lookup),
            "total_dynamic_synonyms": len(self._dynamic_phrases),
            "dynamic_synonyms": self.dynamic_ontology_manager.get_synonyms(),
        }

    def get_unmapped_phrases(self, limit: int = 50) -> List[Dict[str, Any]]:
        """List candidate unmapped phrases pending clinician review."""
        if not self.unmapped_buffer:
            return []
        return self.unmapped_buffer.list_unmapped_phrases(limit=limit)

    def _tokenize(self, text: str) -> Tuple[List[str], List[Tuple[int, int]]]:
        """Tokenize narrative into clean alphanumeric tokens and punctuation markers."""
        tokens = []
        spans = []
        for match in re.finditer(r"[A-Za-z0-9_-]+|[.!?,;]", text):
            tokens.append(match.group().lower())
            spans.append(match.span())
        return tokens, spans

    def _is_negated(self, tokens: List[str], entity_start_idx: int) -> bool:
        """Determines if the entity is preceded by a negation trigger within a 4-token window.

        Halts negation propagation if a sentence boundary or adversative conjunction is encountered.
        """
        # Look back up to 5 tokens prior to entity start
        lookback_limit = max(0, entity_start_idx - 5)
        preceding_tokens = tokens[lookback_limit:entity_start_idx]

        # Scan backwards from entity start
        for tok in reversed(preceding_tokens):
            if tok in NEGATION_TERMINATORS:
                return False
            if tok in NEGATION_TRIGGERS:
                return True
        return False

    def _find_best_fuzzy_match(self, phrase: str) -> Tuple[Optional[str], float, Optional[str]]:
        """Finds closest synonym or canonical phrase via sequence matcher similarity ratio."""
        # Only fuzzy match phrases with reasonable length to avoid spurious 1-letter matches
        if len(phrase) < 4:
            return None, 0.0, None

        best_score = 0.0
        best_target = None
        best_canonical = None

        for target_phrase, canonical in self._synonym_lookup.items():
            # Quick length filter to speed up comparison
            if abs(len(phrase) - len(target_phrase)) > 4:
                continue

            ratio = difflib.SequenceMatcher(None, phrase, target_phrase).ratio()
            if ratio > best_score:
                best_score = ratio
                best_target = target_phrase
                best_canonical = canonical

        return best_target, best_score, best_canonical
