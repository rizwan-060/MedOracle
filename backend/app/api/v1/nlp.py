"""Clinical NLP & Dynamic Ontology Expansion Endpoints (Step 8.3.2).

Provides clinician and diagnostic endpoints for:
1. Extracting clinical entities and symptoms from free-text patient narratives.
2. Browsing active clinical ontology and dynamic clinician-approved synonyms.
3. Reviewing candidate unmapped phrases captured by the active learning buffer.
4. Expanding the ontology dynamically with zero-downtime hot reloading.
"""

import logging
from typing import List
from fastapi import APIRouter, Depends, HTTPException, Query, status

from app.core.security import get_current_user
from app.database.models import User
from app.ml.inference.predictor import RealtimePredictor
from app.schemas.nlp import (
    EntityMention,
    ExpandOntologyRequest,
    ExpandOntologyResponse,
    OntologyOverviewResponse,
    SuggestedMatch,
    TextExtractionRequest,
    TextExtractionResponse,
    UnmappedPhraseItem,
    UnmappedPhrasesListResponse,
)

logger = logging.getLogger("nlp_router")

router = APIRouter(prefix="/nlp", tags=["Clinical NLP & Dynamic Ontology"])


@router.get(
    "/ontology",
    response_model=OntologyOverviewResponse,
    status_code=status.HTTP_200_OK,
    summary="Active Clinical Ontology Catalog",
)
def get_ontology_catalog(
    current_user: User = Depends(get_current_user),
) -> OntologyOverviewResponse:
    """Retrieve catalog of 132 canonical symptoms, static clinical synonyms, and dynamic mappings."""
    try:
        predictor = RealtimePredictor.get_instance()
        overview = predictor.nlp_extractor.get_ontology_overview()
        return OntologyOverviewResponse(
            total_canonical_symptoms=overview["total_canonical_symptoms"],
            canonical_symptoms=overview["canonical_symptoms"],
            total_synonyms=overview["total_synonyms"],
            total_dynamic_synonyms=overview["total_dynamic_synonyms"],
            dynamic_synonyms=overview["dynamic_synonyms"],
        )
    except Exception as e:
        logger.exception("Failed to retrieve ontology catalog: %s", e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to load clinical ontology: {str(e)}",
        )


@router.get(
    "/unmapped-phrases",
    response_model=UnmappedPhrasesListResponse,
    status_code=status.HTTP_200_OK,
    summary="Unmapped Symptom Phrases Active Learning Buffer",
)
def list_unmapped_phrases(
    limit: int = Query(50, ge=1, le=200, description="Maximum number of candidate phrases to return"),
    current_user: User = Depends(get_current_user),
) -> UnmappedPhrasesListResponse:
    """List unmapped phrases recorded from real queries, ranked by frequency with candidate target suggestions."""
    try:
        predictor = RealtimePredictor.get_instance()
        raw_items = predictor.nlp_extractor.get_unmapped_phrases(limit=limit)

        formatted_items: List[UnmappedPhraseItem] = []
        for item in raw_items:
            suggestions = [
                SuggestedMatch(
                    canonical_symptom=s["canonical_symptom"],
                    similarity_score=s["similarity_score"],
                    reference_phrase=s["reference_phrase"],
                )
                for s in item.get("suggested_matches", [])
            ]
            formatted_items.append(
                UnmappedPhraseItem(
                    phrase=item["phrase"],
                    occurrence_count=item["occurrence_count"],
                    first_seen=item["first_seen"],
                    last_seen=item["last_seen"],
                    suggested_matches=suggestions,
                )
            )

        return UnmappedPhrasesListResponse(
            total_unmapped=len(formatted_items),
            unmapped_phrases=formatted_items,
        )
    except Exception as e:
        logger.exception("Failed to retrieve unmapped phrases: %s", e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to load unmapped phrase buffer: {str(e)}",
        )


@router.post(
    "/expand-ontology",
    response_model=ExpandOntologyResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Dynamic Symptom Ontology Expansion",
)
def expand_symptom_ontology(
    payload: ExpandOntologyRequest,
    current_user: User = Depends(get_current_user),
) -> ExpandOntologyResponse:
    """Register a new colloquial or regional phrase mapping to a canonical symptom.

    Persists to disk, resolves unmapped phrase buffer entry, and hot-reloads the active extractor.
    """
    try:
        predictor = RealtimePredictor.get_instance()
        success = predictor.nlp_extractor.register_dynamic_synonym(
            phrase=payload.phrase,
            canonical_symptom=payload.canonical_symptom,
            clinical_notes=payload.clinical_notes,
            source=f"clinician:{current_user.email}",
        )
        if not success:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Unable to register dynamic synonym. Invalid phrase or canonical symptom provided.",
            )

        overview = predictor.nlp_extractor.get_ontology_overview()
        return ExpandOntologyResponse(
            status="success",
            phrase=payload.phrase.strip().lower(),
            canonical_symptom=payload.canonical_symptom.strip().lower(),
            total_dynamic_synonyms=overview["total_dynamic_synonyms"],
            message=f"Phrase '{payload.phrase}' successfully mapped to canonical symptom '{payload.canonical_symptom}' and hot-reloaded.",
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(e),
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.exception("Failed to expand ontology: %s", e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to expand clinical ontology: {str(e)}",
        )


@router.post(
    "/extract-entities",
    response_model=TextExtractionResponse,
    status_code=status.HTTP_200_OK,
    summary="Extract Clinical Symptoms and Entities from Free Text",
)
def extract_clinical_entities(
    payload: TextExtractionRequest,
    current_user: User = Depends(get_current_user),
) -> TextExtractionResponse:
    """Analyze unstructured patient complaints or clinical narratives.

    Extracts positive symptoms, filters negated findings (NegEx), identifies unmapped phrases,
    and returns structured entity spans with confidence metrics.
    """
    try:
        predictor = RealtimePredictor.get_instance()
        extraction = predictor.nlp_extractor.extract(
            text=payload.narrative,
            record_unmapped=payload.record_unmapped,
        )

        entity_models = [
            EntityMention(
                raw_mention=e["raw_mention"],
                canonical_symptom=e["canonical_symptom"],
                confidence=e["confidence"],
                match_type=e["match_type"],
                is_negated=e["is_negated"],
            )
            for e in extraction.get("extracted_entities", [])
        ]

        detected = extraction.get("detected_symptoms", [])

        return TextExtractionResponse(
            detected_symptoms=detected,
            negated_symptoms=extraction.get("negated_symptoms", []),
            extracted_entities=entity_models,
            unrecognized_spans=extraction.get("unrecognized_spans", []),
            total_detected=len(detected),
        )
    except Exception as e:
        logger.exception("Failed to extract clinical entities: %s", e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Clinical NLP entity extraction failed: {str(e)}",
        )
