"""Database synchronization utility for registered ML models.

Synchronizes local filesystem model artifacts (metadata descriptors in `models/saved/`)
with the relational `trained_models` table via SQLAlchemy Session.
"""

from typing import List, Optional
from sqlalchemy import select, update
from sqlalchemy.orm import Session

from app.database.models import TrainedModel
from app.ml.model_registry import list_registered_models


def sync_all_models_to_db(db: Session) -> List[TrainedModel]:
    """Inspect all registered model metadata files and synchronize with the database.

    For any model present on disk:
    - If no entry exists with that (name, version), inserts a new active record.
    - If a newer version of a model is found, older versions are set to `is_active = False`.

    Returns:
        List of all currently active TrainedModel ORM objects.
    """
    disk_models = list_registered_models()
    synced_models: List[TrainedModel] = []

    for meta in disk_models:
        # Determine disease domain from model_id
        if "cardio" in meta.model_id.lower():
            target_disease = "cardiovascular"
        elif "diab" in meta.model_id.lower():
            target_disease = "diabetes"
        elif "symptom" in meta.model_id.lower():
            target_disease = "symptoms"
        else:
            target_disease = meta.target_column

        # Check if record already exists in database
        stmt = select(TrainedModel).where(
            TrainedModel.name == meta.model_id,
            TrainedModel.version == meta.version,
        )
        existing = db.scalars(stmt).first()

        if existing:
            # Update metrics if changed
            existing.metrics = meta.metrics
            existing.artifact_path = f"models/saved/{meta.artifact_filename}"
            existing.algorithm = meta.model_type
            synced_models.append(existing)
        else:
            # Deactivate any previous versions of this model family
            deact_stmt = (
                update(TrainedModel)
                .where(TrainedModel.target_disease == target_disease)
                .values(is_active=False)
            )
            db.execute(deact_stmt)

            # Insert new record
            new_model = TrainedModel(
                name=meta.model_id,
                version=meta.version,
                target_disease=target_disease,
                algorithm=meta.model_type,
                dataset_source=meta.dataset_name,
                artifact_path=f"models/saved/{meta.artifact_filename}",
                metrics=meta.metrics,
                feature_names=meta.feature_columns,
                is_active=True,
            )
            db.add(new_model)
            synced_models.append(new_model)

    db.commit()
    for m in synced_models:
        db.refresh(m)

    return synced_models
