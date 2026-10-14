"""Initial MedOracle database schema.

Revision ID: 001_initial_schema
Revises: 
Create Date: 2026-10-14 21:30:00

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = "001_initial_schema"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. Users Table
    op.create_table(
        "users",
        sa.Column("id", sa.String(length=36), primary_key=True),
        sa.Column("email", sa.String(length=255), nullable=False),
        sa.Column("hashed_password", sa.String(length=255), nullable=False),
        sa.Column("full_name", sa.String(length=255), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("is_verified", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_users_email", "users", ["email"], unique=True)

    # 2. Patient Profiles Table
    op.create_table(
        "patient_profiles",
        sa.Column("id", sa.String(length=36), primary_key=True),
        sa.Column(
            "user_id",
            sa.String(length=36),
            sa.ForeignKey("users.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("date_of_birth", sa.Date(), nullable=True),
        sa.Column("gender", sa.String(length=20), nullable=True),
        sa.Column("height_cm", sa.Float(), nullable=True),
        sa.Column("weight_kg", sa.Float(), nullable=True),
        sa.Column("waist_circumference_cm", sa.Float(), nullable=True),
        sa.Column("smoking_status", sa.String(length=30), nullable=True),
        sa.Column("activity_level", sa.String(length=30), nullable=True),
        sa.Column("blood_group", sa.String(length=10), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_patient_profiles_user_id", "patient_profiles", ["user_id"], unique=True)

    # 3. Medical Histories Table
    op.create_table(
        "medical_histories",
        sa.Column("id", sa.String(length=36), primary_key=True),
        sa.Column(
            "user_id",
            sa.String(length=36),
            sa.ForeignKey("users.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("chronic_conditions", sa.JSON(), nullable=False),
        sa.Column("past_surgeries", sa.JSON(), nullable=False),
        sa.Column("current_medications", sa.JSON(), nullable=False),
        sa.Column("allergies", sa.JSON(), nullable=False),
        sa.Column("family_history", sa.JSON(), nullable=False),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_medical_histories_user_id", "medical_histories", ["user_id"])

    # 4. Symptom Reports Table
    op.create_table(
        "symptom_reports",
        sa.Column("id", sa.String(length=36), primary_key=True),
        sa.Column(
            "user_id",
            sa.String(length=36),
            sa.ForeignKey("users.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("reported_text", sa.Text(), nullable=False),
        sa.Column("duration_days", sa.Integer(), nullable=True),
        sa.Column("severity_self_rating", sa.Integer(), nullable=True),
        sa.Column("body_locations", sa.JSON(), nullable=False),
        sa.Column("triggers", sa.JSON(), nullable=False),
        sa.Column("structured_symptoms", sa.JSON(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_symptom_reports_user_id", "symptom_reports", ["user_id"])

    # 5. Lab Results Table
    op.create_table(
        "lab_results",
        sa.Column("id", sa.String(length=36), primary_key=True),
        sa.Column(
            "user_id",
            sa.String(length=36),
            sa.ForeignKey("users.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("test_date", sa.Date(), nullable=False),
        sa.Column("lab_name", sa.String(length=255), nullable=True),
        sa.Column("biomarkers", sa.JSON(), nullable=False),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_lab_results_user_id", "lab_results", ["user_id"])

    # 6. Analysis Sessions Table
    op.create_table(
        "analysis_sessions",
        sa.Column("id", sa.String(length=36), primary_key=True),
        sa.Column(
            "user_id",
            sa.String(length=36),
            sa.ForeignKey("users.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "symptom_report_id",
            sa.String(length=36),
            sa.ForeignKey("symptom_reports.id", ondelete="SET NULL"),
            nullable=True,
        ),
        sa.Column("status", sa.String(length=30), nullable=False),
        sa.Column("current_phase", sa.String(length=50), nullable=False),
        sa.Column("progress_percent", sa.Integer(), nullable=False),
        sa.Column("consensus_verdict", sa.JSON(), nullable=True),
        sa.Column("debate_summary", sa.JSON(), nullable=True),
        sa.Column("disease_trajectory", sa.JSON(), nullable=True),
        sa.Column("counterfactuals", sa.JSON(), nullable=True),
        sa.Column("reasoning_graph", sa.JSON(), nullable=True),
        sa.Column("recommended_specialty", sa.String(length=100), nullable=True),
        sa.Column("error_message", sa.Text(), nullable=True),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_analysis_sessions_user_id", "analysis_sessions", ["user_id"])
    op.create_index("ix_analysis_sessions_status", "analysis_sessions", ["status"])

    # 7. Agent Outputs Table
    op.create_table(
        "agent_outputs",
        sa.Column("id", sa.String(length=36), primary_key=True),
        sa.Column(
            "analysis_session_id",
            sa.String(length=36),
            sa.ForeignKey("analysis_sessions.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("agent_role", sa.String(length=50), nullable=False),
        sa.Column("findings", sa.Text(), nullable=False),
        sa.Column("confidence", sa.Float(), nullable=False),
        sa.Column("reasoning_chain", sa.JSON(), nullable=False),
        sa.Column("evidence", sa.JSON(), nullable=False),
        sa.Column("challenges", sa.JSON(), nullable=False),
        sa.Column("metadata_payload", sa.JSON(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_agent_outputs_session_id", "agent_outputs", ["analysis_session_id"])
    op.create_index("ix_agent_outputs_agent_role", "agent_outputs", ["agent_role"])

    # 8. Risk Results Table
    op.create_table(
        "risk_results",
        sa.Column("id", sa.String(length=36), primary_key=True),
        sa.Column(
            "analysis_session_id",
            sa.String(length=36),
            sa.ForeignKey("analysis_sessions.id", ondelete="SET NULL"),
            nullable=True,
        ),
        sa.Column(
            "user_id",
            sa.String(length=36),
            sa.ForeignKey("users.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("model_name", sa.String(length=100), nullable=False),
        sa.Column("model_type", sa.String(length=30), nullable=False),
        sa.Column("risk_score", sa.Float(), nullable=False),
        sa.Column("risk_category", sa.String(length=50), nullable=False),
        sa.Column("horizon", sa.String(length=30), nullable=True),
        sa.Column("input_parameters", sa.JSON(), nullable=False),
        sa.Column("missing_or_assumed", sa.JSON(), nullable=False),
        sa.Column("disclaimer", sa.Text(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_risk_results_user_id", "risk_results", ["user_id"])
    op.create_index("ix_risk_results_session_id", "risk_results", ["analysis_session_id"])

    # 9. Doctors Table
    op.create_table(
        "doctors",
        sa.Column("id", sa.String(length=36), primary_key=True),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("specialty", sa.String(length=100), nullable=False),
        sa.Column("sub_specialty", sa.String(length=100), nullable=True),
        sa.Column("hospital_clinic", sa.String(length=255), nullable=False),
        sa.Column("city", sa.String(length=100), nullable=False),
        sa.Column("area", sa.String(length=150), nullable=False),
        sa.Column("address", sa.Text(), nullable=True),
        sa.Column("contact_phone", sa.String(length=50), nullable=True),
        sa.Column("contact_email", sa.String(length=100), nullable=True),
        sa.Column("latitude", sa.Float(), nullable=True),
        sa.Column("longitude", sa.Float(), nullable=True),
        sa.Column("rating", sa.Float(), nullable=False, server_default="5.0"),
        sa.Column("is_available", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_doctors_specialty", "doctors", ["specialty"])
    op.create_index("ix_doctors_city", "doctors", ["city"])

    # 10. Trained Models Table
    op.create_table(
        "trained_models",
        sa.Column("id", sa.String(length=36), primary_key=True),
        sa.Column("name", sa.String(length=100), nullable=False),
        sa.Column("version", sa.String(length=30), nullable=False),
        sa.Column("target_disease", sa.String(length=100), nullable=False),
        sa.Column("algorithm", sa.String(length=100), nullable=False),
        sa.Column("dataset_source", sa.String(length=100), nullable=False),
        sa.Column("artifact_path", sa.String(length=255), nullable=False),
        sa.Column("metrics", sa.JSON(), nullable=False),
        sa.Column("feature_names", sa.JSON(), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_trained_models_name", "trained_models", ["name"])


def downgrade() -> None:
    op.drop_table("trained_models")
    op.drop_table("doctors")
    op.drop_table("risk_results")
    op.drop_table("agent_outputs")
    op.drop_table("analysis_sessions")
    op.drop_table("lab_results")
    op.drop_table("symptom_reports")
    op.drop_table("medical_histories")
    op.drop_table("patient_profiles")
    op.drop_table("users")
