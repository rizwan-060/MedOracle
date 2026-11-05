"""Laboratory test results and biomarker Pydantic v2 schemas."""

from datetime import date, datetime
from typing import Any, Dict, Optional
from pydantic import BaseModel, ConfigDict, Field


class BiomarkerValues(BaseModel):
    """Commonly referenced metabolic and clinical biomarkers."""

    systolic_bp: Optional[float] = Field(None, ge=50, le=280, description="mmHg")
    diastolic_bp: Optional[float] = Field(None, ge=30, le=180, description="mmHg")
    total_cholesterol_mg_dl: Optional[float] = Field(None, ge=50, le=600, description="mg/dL")
    hdl_cholesterol_mg_dl: Optional[float] = Field(None, ge=10, le=150, description="mg/dL")
    ldl_cholesterol_mg_dl: Optional[float] = Field(None, ge=20, le=400, description="mg/dL")
    triglycerides_mg_dl: Optional[float] = Field(None, ge=20, le=1500, description="mg/dL")
    fasting_blood_glucose_mg_dl: Optional[float] = Field(None, ge=30, le=600, description="mg/dL")
    hba1c_percent: Optional[float] = Field(None, ge=3.0, le=20.0, description="%")
    serum_creatinine_mg_dl: Optional[float] = Field(None, ge=0.1, le=25.0, description="mg/dL")
    estimated_gfr: Optional[float] = Field(None, ge=1.0, le=200.0, description="mL/min/1.73m2")


class LabResultBase(BaseModel):
    """Base laboratory record schema."""

    test_date: date
    lab_name: Optional[str] = Field(None, max_length=255)
    biomarkers: Dict[str, Any] = Field(
        ..., description="Biomarker key-value mapping (e.g. cholesterol, creatinine)"
    )
    notes: Optional[str] = None


class LabResultCreate(LabResultBase):
    """Create lab result schema."""

    pass


class LabResultResponse(LabResultBase):
    """Response lab result schema."""

    id: str
    user_id: str
    document_url: Optional[str] = None
    document_type: str = "manual_entry"
    ocr_raw_text: Optional[str] = None
    ocr_confidence: Optional[float] = None
    is_verified: bool = False
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class RawExtractedBiomarkerItem(BaseModel):
    """Raw unnormalized biomarker observation extracted from OCR table or document text."""

    label: str = Field(..., description="Raw label extracted from the laboratory report (e.g. 'Fasting B.S.')")
    value: Any = Field(..., description="Raw value token (e.g. '125', '1,25', '< 0.01', 'Negative')")
    unit: Optional[str] = Field(None, description="Extracted unit of measure (e.g. 'mg/dL', 'mmol/L', 'µmol/L')")
    reference_range: Optional[str] = Field(None, description="Raw reference range string (e.g. '70 - 99 mg/dL')")
    flag: Optional[str] = Field(None, description="Extracted abnormality flag (e.g. 'H', 'High', 'L', 'Normal')")
    ocr_confidence: float = Field(100.0, ge=0.0, le=100.0, description="OCR extraction confidence score percentage")
    page_number: Optional[int] = Field(None, ge=1, description="Page number of report scan")


class NormalizedBiomarkerRecord(BaseModel):
    """Clinically standardized and auditable biomarker record with provenance tracking."""

    patient_id: Optional[str] = Field(None, description="Traceable patient identifier")
    source_document_id: Optional[str] = Field(None, description="Identifier of source lab report document")
    source_document_url: Optional[str] = Field(None, description="URL or path to uploaded document")
    lab_name: Optional[str] = Field(None, description="Source diagnostic laboratory name")
    original_label: str = Field(..., description="Original raw unnormalized test label")
    canonical_id: Optional[str] = Field(None, description="Canonical MedOracle biomarker identifier")
    display_name: str = Field(..., description="Human-readable standardized clinical biomarker name")
    original_value_raw: str = Field(..., description="Exact raw string representation before parsing")
    original_numeric_value: Optional[float] = Field(None, description="Parsed numeric value on original scale")
    original_unit: Optional[str] = Field(None, description="Source unit of measure")
    comparator: Optional[str] = Field(None, description="Inequality comparator ('<', '<=', '>', '>=') if present")
    qualitative_value: Optional[str] = Field(None, description="Qualitative result ('Negative', 'Reactive', 'Trace')")
    normalized_value: Optional[float] = Field(None, description="Standardized numeric value in MedOracle canonical unit")
    canonical_unit: str = Field(..., description="Target canonical unit of measure")
    conversion_factor: float = Field(1.0, description="Multiplier applied to convert original unit to canonical unit")
    conversion_method: str = Field("unconverted", description="Conversion justification and molecular formula reference")
    reference_range_raw: Optional[str] = Field(None, description="Preserved raw laboratory reference interval string")
    reference_range_low: Optional[float] = Field(None, description="Lower reference bound converted to canonical unit")
    reference_range_high: Optional[float] = Field(None, description="Upper reference bound converted to canonical unit")
    abnormal_flag_raw: Optional[str] = Field(None, description="Original abnormality flag from report")
    abnormality_classification: str = Field("INDETERMINATE", description="Programmatic abnormality classification")
    ocr_confidence: float = Field(100.0, ge=0.0, le=100.0, description="OCR character recognition confidence percentage")
    mapping_confidence: float = Field(1.0, ge=0.0, le=1.0, description="Entity synonym mapping confidence (0.0 to 1.0)")
    validation_status: str = Field("NORMALIZED", description="Audit status ('NORMALIZED', 'NEEDS_REVIEW', etc.)")
    clinical_caveats: list[str] = Field(default_factory=list, description="Clinical audit warnings or unit limitations")
    specimen_collection_date: Optional[str] = Field(None, description="Explicit specimen draw/collection timestamp")
    report_date: Optional[str] = Field(None, description="Report finalization or release date")
    page_number: Optional[int] = Field(None, description="Page number of document")
    normalized_at: str = Field(..., description="ISO 8601 normalization timestamp")
    normalizer_version: str = Field("1.0.0", description="BiomarkerEntityNormalizer version")

    model_config = ConfigDict(from_attributes=True)


class BiomarkerNormalizationBatchRequest(BaseModel):
    """Request payload for normalizing a batch of OCR-extracted biomarker items."""

    patient_id: Optional[str] = Field(None, description="Optional patient identifier")
    source_document_id: Optional[str] = Field(None, description="Optional document scan identifier")
    source_document_url: Optional[str] = Field(None, description="Optional document file path/URL")
    lab_name: Optional[str] = Field(None, description="Source diagnostic laboratory name")
    specimen_collection_date: Optional[str] = Field(None, description="Specimen collection date (YYYY-MM-DD)")
    report_date: Optional[str] = Field(None, description="Lab report date (YYYY-MM-DD)")
    extracted_items: list[RawExtractedBiomarkerItem] = Field(..., description="List of raw extracted biomarker items")

    model_config = ConfigDict(from_attributes=True)


class BiomarkerNormalizationBatchResponse(BaseModel):
    """Response payload containing standardized clinical biomarkers, audit records, and downstream dict."""

    status: str = Field(default="success", description="Processing status")
    total_extracted: int = Field(..., description="Total raw items submitted")
    normalized_count: int = Field(..., description="Count of successfully normalized biomarkers")
    needs_review_count: int = Field(..., description="Count of items requiring clinician review")
    unmapped_count: int = Field(..., description="Count of unrecognized biomarkers")
    ambiguous_count: int = Field(..., description="Count of ambiguous biomarker labels")
    invalid_count: int = Field(..., description="Count of invalid numeric or unit entries")
    canonical_biomarkers_dict: Dict[str, Any] = Field(
        default_factory=dict,
        description="Clean canonical key-value dictionary ready for downstream ML and clinical risk engines",
    )
    records: list[NormalizedBiomarkerRecord] = Field(
        default_factory=list,
        description="Complete list of traceable audit records with full conversion provenance",
    )
    execution_time_ms: float = Field(..., description="Total normalization processing latency in milliseconds")
    processed_at: str = Field(..., description="ISO 8601 processing completion timestamp")

    model_config = ConfigDict(from_attributes=True)

