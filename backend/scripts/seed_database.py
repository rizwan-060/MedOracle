"""Database seeding script for MedOracle.

Inserts clinically authentic sample data matching the specifications documented
in docs/architecture/DATABASE_SCHEMA.md.
"""

from datetime import date, datetime, timezone
import os
import sys
from pathlib import Path
import bcrypt

# Ensure backend root is on sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.database.session import SessionLocal
from app.database.models import (
    AgentOutput,
    AnalysisSession,
    Doctor,
    LabResult,
    MedicalHistory,
    PatientProfile,
    RiskResult,
    SymptomReport,
    TrainedModel,
    User,
)


def hash_password(password: str) -> str:
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode("utf-8"), salt).decode("utf-8")


def seed_database():
    db = SessionLocal()
    try:
        # Check if already seeded
        if db.query(User).filter_by(email="ahmed.khan@example.com").first():
            print("[INFO] Database already contains seed data. Skipping.")
            return

        print("[INFO] Seeding MedOracle PostgreSQL database...")

        # 1. Users
        user1 = User(
            id="a1b2c3d4-e5f6-4a1b-8c2d-111111111111",
            email="ahmed.khan@example.com",
            hashed_password=hash_password("Password123!"),
            full_name="Ahmed Khan",
            is_active=True,
            is_verified=True,
        )
        user2 = User(
            id="b2c3d4e5-f6a1-4b2c-9d3e-222222222222",
            email="fatima.noor@example.com",
            hashed_password=hash_password("SecurePass456!"),
            full_name="Fatima Noor",
            is_active=True,
            is_verified=True,
        )
        db.add_all([user1, user2])
        db.flush()

        # 2. Patient Profiles
        profile1 = PatientProfile(
            id="11111111-2222-3333-4444-555555555555",
            user_id=user1.id,
            date_of_birth=date(1972, 4, 18),
            gender="male",
            height_cm=175.0,
            weight_kg=86.5,
            waist_circumference_cm=98.0,
            smoking_status="current_smoker",
            activity_level="low",
            blood_group="B+",
        )
        profile2 = PatientProfile(
            id="22222222-3333-4444-5555-666666666666",
            user_id=user2.id,
            date_of_birth=date(1985, 11, 25),
            gender="female",
            height_cm=162.0,
            weight_kg=68.0,
            waist_circumference_cm=82.0,
            smoking_status="never",
            activity_level="moderate",
            blood_group="O+",
        )
        db.add_all([profile1, profile2])

        # 3. Medical Histories
        history1 = MedicalHistory(
            id="33333333-4444-5555-6666-777777777777",
            user_id=user1.id,
            chronic_conditions=["hypertension", "dyslipidemia"],
            past_surgeries=[],
            current_medications=[{"name": "Amlodipine", "dosage": "5mg", "freq": "once_daily"}],
            allergies=["penicillin"],
            family_history=[
                {"relative": "father", "condition": "myocardial_infarction", "age_at_onset": 52}
            ],
            notes="Patient complies with antihypertensive therapy.",
        )
        history2 = MedicalHistory(
            id="44444444-5555-6666-7777-888888888888",
            user_id=user2.id,
            chronic_conditions=["gestational_diabetes_history"],
            past_surgeries=[],
            current_medications=[],
            allergies=[],
            family_history=[
                {"relative": "mother", "condition": "type_2_diabetes", "age_at_onset": 58}
            ],
            notes="Annual screening recommended.",
        )
        db.add_all([history1, history2])

        # 4. Symptom Reports
        symptom1 = SymptomReport(
            id="55555555-6666-7777-8888-999999999999",
            user_id=user1.id,
            reported_text="Tight squeezing chest sensation radiating to left shoulder and jaw during morning brisk walking.",
            duration_days=4,
            severity_self_rating=8,
            body_locations=["chest", "left_shoulder", "jaw"],
            triggers=["brisk_walking", "cold_air"],
            structured_symptoms=["chest_tightness", "radiating_pain", "exertional_dyspnea"],
        )
        symptom2 = SymptomReport(
            id="66666666-7777-8888-9999-000000000000",
            user_id=user2.id,
            reported_text="Unusual fatigue, increased thirst, and frequent nighttime urination over past month.",
            duration_days=30,
            severity_self_rating=5,
            body_locations=["systemic"],
            triggers=["none"],
            structured_symptoms=["polydipsia", "polyuria", "fatigue"],
        )
        db.add_all([symptom1, symptom2])
        db.flush()

        # 5. Lab Results
        lab1 = LabResult(
            id="77777777-8888-9999-0000-111111111111",
            user_id=user1.id,
            test_date=date(2026, 10, 10),
            lab_name="Chughtai Lab, Lahore",
            biomarkers={
                "systolic_bp": 146,
                "diastolic_bp": 92,
                "total_cholesterol_mg_dl": 242,
                "hdl_cholesterol_mg_dl": 37,
                "ldl_cholesterol_mg_dl": 164,
                "fasting_blood_glucose_mg_dl": 118,
                "serum_creatinine_mg_dl": 1.12,
                "hba1c_percent": 6.2,
            },
            notes="Lipid panel indicates atherogenic dyslipidemia.",
        )
        lab2 = LabResult(
            id="88888888-9999-0000-1111-222222222222",
            user_id=user2.id,
            test_date=date(2026, 10, 8),
            lab_name="Shaukat Khanum Diagnostics",
            biomarkers={
                "systolic_bp": 122,
                "diastolic_bp": 78,
                "total_cholesterol_mg_dl": 185,
                "hdl_cholesterol_mg_dl": 52,
                "fasting_blood_glucose_mg_dl": 134,
                "serum_creatinine_mg_dl": 0.85,
                "hba1c_percent": 6.9,
            },
            notes="Fasting glucose and HbA1c suggest impaired glycemic control.",
        )
        db.add_all([lab1, lab2])

        # 6. Analysis Sessions
        session1 = AnalysisSession(
            id="99999999-0000-1111-2222-333333333333",
            user_id=user1.id,
            symptom_report_id=symptom1.id,
            status="completed",
            current_phase="completed",
            progress_percent=100,
            consensus_verdict={
                "primary_risk_category": "Coronary Artery Disease Risk",
                "overall_urgency": "high",
                "consensus_confidence": 88.5,
                "summary": "Exertional angina supported by dyslipidemia and hereditary premature CAD history.",
            },
            debate_summary={
                "rounds_conducted": 2,
                "contradictions_detected": ["Lab agent noted normal renal markers vs Symptom agent rating severity 8"],
                "resolution": "Symptom agent maintained high urgency; consensus weighted exertional nature.",
            },
            disease_trajectory={
                "30_days": {"projected_risk": 24.0, "status": "stable_high"},
                "6_months": {"projected_risk": 26.5, "status": "progressive"},
                "1_year": {"projected_risk": 29.8, "status": "progressive_elevated"},
            },
            counterfactuals=[
                {"intervention": "Smoking cessation", "projected_risk_1_year": 18.5, "absolute_risk_reduction": 11.3},
                {"intervention": "Daily 30-min walking", "projected_risk_1_year": 24.2, "absolute_risk_reduction": 5.6},
            ],
            reasoning_graph={
                "nodes": [
                    {"id": "n_symptom", "label": "Exertional Angina (Severity 8)", "type": "symptom"},
                    {"id": "n_history", "label": "Paternal MI Age 52", "type": "history"},
                    {"id": "n_lab", "label": "Total Cholesterol 242 mg/dL", "type": "lab"},
                    {"id": "n_risk", "label": "Framingham Risk: 23.8%", "type": "risk"},
                ],
                "edges": [
                    {"source": "n_symptom", "target": "n_risk"},
                    {"source": "n_history", "target": "n_risk"},
                    {"source": "n_lab", "target": "n_risk"},
                ],
            },
            recommended_specialty="Cardiology",
            completed_at=datetime.now(timezone.utc),
        )
        db.add(session1)
        db.flush()

        # 7. Agent Outputs
        agent_out1 = AgentOutput(
            id="aaaa1111-bbbb-2222-cccc-333333333333",
            analysis_session_id=session1.id,
            agent_role="symptom_agent",
            findings="Symptom profile indicates probable exertional angina pectoris.",
            confidence=86.0,
            reasoning_chain=["Exertional tightness triggered by brisk walking", "Radiation to jaw and shoulder"],
            evidence=["Severity rating 8/10", "Duration 4 days"],
            challenges=[],
        )
        agent_out2 = AgentOutput(
            id="bbbb2222-cccc-3333-dddd-444444444444",
            analysis_session_id=session1.id,
            agent_role="medical_history_agent",
            findings="Significant hereditary risk multiplier from first-degree premature CAD.",
            confidence=91.0,
            reasoning_chain=["Paternal myocardial infarction at age 52", "Active tobacco smoking adds compounding injury"],
            evidence=["Father MI at age 52", "Current smoker status"],
            challenges=[],
        )
        db.add_all([agent_out1, agent_out2])

        # 8. Risk Results
        risk1 = RiskResult(
            id="cccc3333-dddd-4444-eeee-555555555555",
            analysis_session_id=session1.id,
            user_id=user1.id,
            model_name="Framingham 10-Year General CVD",
            model_type="clinical_formula",
            risk_score=23.8,
            risk_category="high",
            horizon="10_year",
            input_parameters={"age": 54, "total_chol": 242, "hdl": 37, "sbp": 146, "treated_bp": True, "smoker": True},
            missing_or_assumed=[],
            disclaimer="MedOracle decision support only; does not provide diagnosis.",
        )
        db.add(risk1)

        # 9. Doctors
        doc1 = Doctor(
            id="dddd4444-eeee-5555-ffff-666666666666",
            name="Dr. Sarah Khan, FCPS",
            specialty="Cardiology",
            sub_specialty="Interventional Cardiology",
            hospital_clinic="Punjab Institute of Cardiology",
            city="Lahore",
            area="Jail Road",
            address="Jail Rd, Shadman, Lahore, Punjab",
            contact_phone="+92-42-99203051",
            latitude=31.5401,
            longitude=74.3312,
            rating=4.9,
            is_available=True,
        )
        doc2 = Doctor(
            id="eeee5555-ffff-6666-aaaa-777777777777",
            name="Dr. Tariq Mahmood, MRCP",
            specialty="Endocrinology",
            sub_specialty="Diabetology & Metabolism",
            hospital_clinic="Shaukat Khanum Memorial Hospital",
            city="Lahore",
            area="Johar Town",
            address="7A Block R3, Johar Town, Lahore",
            contact_phone="+92-42-35905000",
            latitude=31.4721,
            longitude=74.2785,
            rating=4.85,
            is_available=True,
        )
        db.add_all([doc1, doc2])

        # 10. Trained Models
        mod1 = TrainedModel(
            id="ffff6666-aaaa-7777-bbbb-888888888888",
            name="cardiovascular_rf_classifier",
            version="v1.0.0",
            target_disease="Cardiovascular Disease",
            algorithm="RandomForestClassifier",
            dataset_source="UCI Heart Disease",
            artifact_path="backend/app/ml/models/cardio_rf_v1.joblib",
            metrics={"roc_auc": 0.884, "f1_score": 0.821, "accuracy": 0.845, "precision": 0.835, "recall": 0.808},
            feature_names=["age", "sex", "cp", "trestbps", "chol", "fbs", "restecg"],
            is_active=True,
        )
        mod2 = TrainedModel(
            id="00007777-bbbb-8888-cccc-999999999999",
            name="diabetes_lightgbm_classifier",
            version="v1.0.0",
            target_disease="Type 2 Diabetes",
            algorithm="LGBMClassifier",
            dataset_source="PIMA Indians Diabetes",
            artifact_path="backend/app/ml/models/diabetes_lgbm_v1.joblib",
            metrics={"roc_auc": 0.852, "f1_score": 0.774, "accuracy": 0.812, "precision": 0.791, "recall": 0.758},
            feature_names=["pregnancies", "glucose", "blood_pressure", "skin_thickness", "insulin", "bmi", "dpf", "age"],
            is_active=True,
        )
        db.add_all([mod1, mod2])

        db.commit()
        print("[SUCCESS] Successfully seeded all 10 tables in PostgreSQL medoracle_db!")

    except Exception as e:
        db.rollback()
        print(f"[ERROR] Database seeding failed: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    seed_database()
