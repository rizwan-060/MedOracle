"""Pydantic schemas for Clinical NLP Ontology & Dynamic Vocabulary Expansion (Step 8.3.2)."""

from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class EntityMention(BaseModel):
    """Extracted clinical symptom entity span."""
    raw_mention: str = Field(..., description="Original raw text snippet in patient description")
    canonical_symptom: str = Field(..., description="Canonical 132-symptom target identifier")
    confidence: float = Field(..., description="Extraction confidence score (0.0 to 1.0)")
    match_type: str = Field(..., description="'exact', 'synonym', 'dynamic_synonym', 'fuzzy_typo', or 'semantic_ner'")
    is_negated: bool = Field(False, description="True if preceded by clinical negation trigger")


class TextExtractionRequest(BaseModel):
    """Input payload for clinical narrative symptom extraction."""
    narrative: str = Field(
        ...,
        min_length=3,
        max_length=5000,
        description="Free-text clinical description or patient complaint",
        examples=["Severe throbbing chest tightness and shortness of breath when walking fast."],
    )
    record_unmapped: bool = Field(
        True,
        description="Whether unrecognized phrases should be logged to the active learning buffer",
    )


class TextExtractionResponse(BaseModel):
    """Output payload with extracted symptoms and unrecognized tokens."""
    detected_symptoms: List[str] = Field(..., description="Positive non-negated canonical symptom IDs")
    negated_symptoms: List[str] = Field(..., description="Identified negated symptom entities")
    extracted_entities: List[EntityMention] = Field(..., description="Structured entity metadata")
    unrecognized_spans: List[str] = Field(..., description="Phrases that did not match any ontology entry")
    total_detected: int = Field(..., description="Count of positive canonical symptoms")


class SuggestedMatch(BaseModel):
    """Candidate canonical symptom match with semantic similarity score."""
    canonical_symptom: str
    similarity_score: float
    reference_phrase: str


class UnmappedPhraseItem(BaseModel):
    """Candidate unmapped symptom phrase in active learning buffer."""
    phrase: str = Field(..., description="Unmapped phrase entered by user")
    occurrence_count: int = Field(..., description="Frequency of observation")
    first_seen: str = Field(..., description="ISO UTC timestamp of initial observation")
    last_seen: str = Field(..., description="ISO UTC timestamp of most recent observation")
    suggested_matches: List[SuggestedMatch] = Field(default_factory=list, description="Top similarity matches")


class UnmappedPhrasesListResponse(BaseModel):
    """Response payload listing candidate phrases pending clinician review."""
    total_unmapped: int
    unmapped_phrases: List[UnmappedPhraseItem]


class ExpandOntologyRequest(BaseModel):
    """Payload for registering a new synonym in the active ontology."""
    phrase: str = Field(..., min_length=2, max_length=150, description="New synonym expression")
    canonical_symptom: str = Field(..., description="Valid canonical symptom target from 132-symptom list")
    clinical_notes: Optional[str] = Field(None, description="Clinician justification for mapping")


class ExpandOntologyResponse(BaseModel):
    """Confirmation payload after dynamic ontology expansion."""
    status: str = Field("success", description="Registration status")
    phrase: str
    canonical_symptom: str
    total_dynamic_synonyms: int
    message: str


class OntologyOverviewResponse(BaseModel):
    """Catalog of active clinical vocabulary and canonical symptoms."""
    total_canonical_symptoms: int
    canonical_symptoms: List[str]
    total_synonyms: int
    total_dynamic_synonyms: int
    dynamic_synonyms: Dict[str, str]
