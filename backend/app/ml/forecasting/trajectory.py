"""Disease Trajectory Forecasting models and leakage-free training/evaluation pipelines.

Implements:
1. ClinicalTrendForecaster: Transparent longitudinal slope + Step 12 epistemic-doubt-aware
   trajectory projection baseline (30-day, 6-month, 1-year).
2. LongitudinalMLForecaster: Patient-grouped, temporally split scikit-learn forecasting
   pipeline (LogisticRegression, RandomForest, GradientBoosting) with strict leakage prevention.
"""

from datetime import datetime, timedelta, timezone
import math
from typing import Any, Dict, List, Optional, Sequence, Tuple
import uuid
import numpy as np
from sklearn.ensemble import GradientBoostingClassifier, RandomForestClassifier
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    average_precision_score,
    brier_score_loss,
    confusion_matrix,
    recall_score,
    roc_auc_score,
)
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

from app.ml.forecasting.longitudinal import LongitudinalFeatureExtractor
from app.ml.model_registry import ModelMetadata, load_model_bundle, save_model_bundle
from app.schemas.trajectory import (
    DiseaseTrajectoryResult,
    HorizonProjection,
    LongitudinalFeatureVector,
    TrajectoryDirection,
)


class ClinicalTrendForecaster:
    """Transparent rule-based longitudinal trajectory forecaster integrated with Step 12 consensus.

    Strictly separates current-state assessment from future-state projection.
    Never overrides Step 12 safety warnings and widens uncertainty intervals under
    missingness, irregular sampling, or unresolved epistemic doubt.
    """

    MODEL_VERSION = "clinical_trend_forecaster_v1.0.0"

    def forecast(
        self,
        longitudinal_features: LongitudinalFeatureVector,
        current_risk_percent: Optional[float] = None,
        horizons_days: Optional[List[int]] = None,
        disease_domain: str = "cardiovascular",
        consensus_resolution: Optional[Dict[str, Any]] = None,
        epistemic_doubt_score: Optional[float] = None,
        analysis_session_id: Optional[str] = None,
    ) -> DiseaseTrajectoryResult:
        """Project future risk trajectories across configured horizons."""
        horizons = horizons_days or [30, 180, 365]
        forecast_id = f"FC-{uuid.uuid4().hex[:10]}"

        # Extract Step 12 consensus metadata (preserving safety warnings intact)
        cr = consensus_resolution or {}
        preserved_warnings = list(cr.get("clinical_safety_warnings") or [])
        doubt = (
            float(epistemic_doubt_score)
            if epistemic_doubt_score is not None
            else float(cr.get("global_epistemic_doubt_score") or 0.0)
        )
        doubt = max(0.0, min(1.0, doubt))

        unresolved_count = len(cr.get("unresolved_issues") or [])
        if cr.get("overall_outcome") in ["UNRESOLVED_CONSENSUS", "unresolved_consensus"]:
            unresolved_count = max(unresolved_count, 1)

        # Collect active biomarker trends with >= 2 observations
        active_trends = [
            t for t in longitudinal_features.biomarker_trends.values()
            if not t.is_missing and not t.insufficient_history
        ]
        present_markers = [
            t for t in longitudinal_features.biomarker_trends.values()
            if not t.is_missing
        ]

        evidence_refs = list(longitudinal_features.source_record_ids)
        for t in present_markers:
            evidence_refs.append(f"biomarker:{t.biomarker_name}")
        evidence_refs = list(dict.fromkeys(evidence_refs))

        limitations: List[str] = [
            "Rule-based longitudinal projection; not a substitute for prospective clinical cohort validation.",
            "Irregular sampling intervals and unmeasured confounders widen forecast uncertainty bounds.",
        ]
        if doubt > 0.25:
            limitations.append(
                f"Elevated Step 12 epistemic doubt ({doubt:.2f}) widened prediction uncertainty intervals."
            )
        if longitudinal_features.adherence_inconsistent:
            limitations.append("Documented medication non-adherence increases worsening trajectory risk.")

        # Insufficient data guard: never fabricate history or predictions when no clinical data exists
        if current_risk_percent is None and not present_markers and longitudinal_features.symptom_severity_latest is None:
            return DiseaseTrajectoryResult(
                forecast_id=forecast_id,
                patient_id=longitudinal_features.patient_id,
                analysis_session_id=analysis_session_id,
                model_version=self.MODEL_VERSION,
                model_type="deterministic_longitudinal_trend",
                is_clinically_validated=False,
                current_risk_percent=None,
                overall_direction=TrajectoryDirection.INSUFFICIENT_DATA,
                horizons=[
                    HorizonProjection(
                        horizon_days=h,
                        horizon_label=self._format_horizon_label(h),
                        projected_risk_percent=None,
                        uncertainty_lower_percent=None,
                        uncertainty_upper_percent=None,
                        confidence_level=0.0,
                        is_calibrated_probability=False,
                        direction=TrajectoryDirection.INSUFFICIENT_DATA,
                        status_label="insufficient_data",
                        key_drivers=["No baseline risk or longitudinal observations available."],
                    )
                    for h in horizons
                ],
                epistemic_doubt_score=doubt,
                unresolved_contradiction_count=unresolved_count,
                preserved_safety_warnings=preserved_warnings,
                longitudinal_summary=longitudinal_features,
                input_evidence_references=evidence_refs,
                limitations=limitations + ["Insufficient patient observations to project trajectory."],
            )

        base_risk = float(current_risk_percent) if current_risk_percent is not None else self._estimate_baseline_proxy(longitudinal_features)

        # Compute net monthly risk drift from observed longitudinal slopes (capped for physiological plausibility)
        monthly_drift = 0.0
        drivers: List[str] = []

        worsening_count = sum(1 for t in active_trends if t.trend_direction == TrajectoryDirection.WORSENING)
        improving_count = sum(1 for t in active_trends if t.trend_direction == TrajectoryDirection.IMPROVING)

        for t in active_trends:
            if t.trend_direction == TrajectoryDirection.WORSENING:
                monthly_drift += 0.65
                drivers.append(f"Worsening {t.biomarker_name} ({t.rate_of_change_per_30d:+.2f}/30d)")
            elif t.trend_direction == TrajectoryDirection.IMPROVING:
                monthly_drift -= 0.45
                drivers.append(f"Improving {t.biomarker_name} ({t.rate_of_change_per_30d:+.2f}/30d)")

        if longitudinal_features.symptom_severity_slope_per_30d is not None:
            slope = longitudinal_features.symptom_severity_slope_per_30d
            if slope >= 0.5:
                monthly_drift += 0.4
                drivers.append(f"Escalating symptom severity ({slope:+.2f}/30d)")
            elif slope <= -0.5:
                monthly_drift -= 0.35
                drivers.append(f"Improving symptom severity ({slope:+.2f}/30d)")

        if longitudinal_features.adherence_inconsistent:
            monthly_drift += 0.5
            drivers.append("Documented medication non-adherence")

        if not active_trends:
            limitations.append("Single-point or sparse longitudinal history: slope-based drift unavailable.")
            drivers.append("Single-timepoint baseline only; longitudinal slope unavailable")

        # Determine overall trajectory direction
        if not active_trends and longitudinal_features.symptom_severity_slope_per_30d is None:
            overall_dir = TrajectoryDirection.STABLE if current_risk_percent is not None else TrajectoryDirection.INSUFFICIENT_DATA
        elif monthly_drift >= 0.35 or worsening_count > improving_count:
            overall_dir = TrajectoryDirection.WORSENING
        elif monthly_drift <= -0.35 or improving_count > worsening_count:
            overall_dir = TrajectoryDirection.IMPROVING
        else:
            overall_dir = TrajectoryDirection.STABLE

        projections: List[HorizonProjection] = []
        for h in horizons:
            months = h / 30.0
            # Diminishing marginal drift over longer horizons (square-root damping after 3 months)
            effective_months = months if months <= 3.0 else 3.0 + math.sqrt(months - 3.0)
            projected = max(0.5, min(99.0, base_risk + (monthly_drift * effective_months)))

            # Uncertainty half-width grows with horizon, missingness, and Step 12 epistemic doubt
            base_width = 3.0 + (1.8 * math.sqrt(months))
            missing_penalty = 8.0 * longitudinal_features.missingness_rate
            doubt_penalty = 12.0 * doubt
            sparse_penalty = 4.0 if not active_trends else 0.0
            half_width = base_width + missing_penalty + doubt_penalty + sparse_penalty

            lower = max(0.0, round(projected - half_width, 2))
            upper = min(100.0, round(projected + half_width, 2))
            conf = max(15.0, min(95.0, 88.0 - (doubt * 35.0) - (longitudinal_features.missingness_rate * 25.0) - (months * 1.5)))

            h_dir = overall_dir
            if h_dir == TrajectoryDirection.WORSENING:
                status_label = "progressive_elevated" if projected >= 20.0 else "progressive"
            elif h_dir == TrajectoryDirection.IMPROVING:
                status_label = "improving"
            else:
                status_label = "stable_high" if projected >= 20.0 else "stable"

            projections.append(
                HorizonProjection(
                    horizon_days=h,
                    horizon_label=self._format_horizon_label(h),
                    projected_risk_percent=round(projected, 2),
                    uncertainty_lower_percent=lower,
                    uncertainty_upper_percent=upper,
                    confidence_level=round(conf, 2),
                    is_calibrated_probability=False,
                    direction=h_dir,
                    status_label=status_label,
                    key_drivers=drivers[:5],
                )
            )

        return DiseaseTrajectoryResult(
            forecast_id=forecast_id,
            patient_id=longitudinal_features.patient_id,
            analysis_session_id=analysis_session_id,
            model_version=self.MODEL_VERSION,
            model_type="deterministic_longitudinal_trend",
            is_clinically_validated=False,
            current_risk_percent=round(base_risk, 2),
            overall_direction=overall_dir,
            horizons=projections,
            epistemic_doubt_score=round(doubt, 4),
            unresolved_contradiction_count=unresolved_count,
            preserved_safety_warnings=preserved_warnings,
            longitudinal_summary=longitudinal_features,
            input_evidence_references=evidence_refs,
            limitations=limitations,
        )

    @staticmethod
    def _format_horizon_label(days: int) -> str:
        if days == 30:
            return "30_days"
        if days == 180:
            return "6_months"
        if days == 365:
            return "1_year"
        return f"{days}_days"

    @staticmethod
    def _estimate_baseline_proxy(features: LongitudinalFeatureVector) -> float:
        """Conservative heuristic baseline risk proxy when no Framingham/ML score was passed."""
        score = 10.0
        sbp = features.biomarker_trends.get("systolic_bp")
        if sbp and sbp.latest_value is not None and sbp.latest_value >= 140.0:
            score += 8.0
        a1c = features.biomarker_trends.get("hba1c_percent")
        if a1c and a1c.latest_value is not None and a1c.latest_value >= 6.5:
            score += 7.0
        ldl = features.biomarker_trends.get("ldl_cholesterol_mg_dl")
        if ldl and ldl.latest_value is not None and ldl.latest_value >= 160.0:
            score += 6.0
        if features.adherence_inconsistent:
            score += 4.0
        return min(65.0, score)


def temporal_patient_split(
    records: List[Dict[str, Any]],
    patient_id_key: str = "patient_id",
    time_key: str = "prediction_time",
    train_frac: float = 0.6,
    val_frac: float = 0.2,
) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]], List[Dict[str, Any]]]:
    """Split longitudinal records with strict patient-grouping AND temporal ordering.

    Ensures:
    1. No patient_id appears in more than one partition (preventing patient leakage).
    2. Patients are ordered by their earliest prediction timestamp so test patients
       represent later temporal cohorts.
    """
    if not records:
        return [], [], []

    patient_earliest: Dict[str, str] = {}
    for rec in records:
        pid = str(rec[patient_id_key])
        ts = str(rec[time_key])
        if pid not in patient_earliest or ts < patient_earliest[pid]:
            patient_earliest[pid] = ts

    ordered_patients = sorted(patient_earliest.keys(), key=lambda p: (patient_earliest[p], p))
    n = len(ordered_patients)
    n_train = max(1, int(n * train_frac))
    n_val = max(1, int(n * val_frac)) if n >= 3 else 0

    train_pids = set(ordered_patients[:n_train])
    val_pids = set(ordered_patients[n_train : n_train + n_val])
    test_pids = set(ordered_patients[n_train + n_val :])

    train_recs = [r for r in records if str(r[patient_id_key]) in train_pids]
    val_recs = [r for r in records if str(r[patient_id_key]) in val_pids]
    test_recs = [r for r in records if str(r[patient_id_key]) in test_pids]
    return train_recs, val_recs, test_recs


class LongitudinalMLForecaster:
    """Supervised ML trajectory forecaster with leakage-free sklearn Pipeline and temporal evaluation."""

    FEATURE_NAMES: List[str] = [
        "systolic_bp_latest",
        "systolic_bp_slope_30d",
        "hba1c_latest",
        "hba1c_slope_30d",
        "ldl_latest",
        "ldl_slope_30d",
        "egfr_latest",
        "symptom_severity_latest",
        "missingness_rate",
        "adherence_inconsistent",
    ]

    def __init__(self, algorithm: str = "logistic_regression", horizon_days: int = 180) -> None:
        self.algorithm = algorithm
        self.horizon_days = horizon_days
        self.pipeline: Optional[Pipeline] = None
        self.metadata: Optional[ModelMetadata] = None

    @staticmethod
    def _build_estimator(algorithm: str) -> Any:
        if algorithm == "random_forest":
            return RandomForestClassifier(n_estimators=100, max_depth=5, class_weight="balanced", random_state=42)
        if algorithm == "gradient_boosting":
            return GradientBoostingClassifier(n_estimators=80, max_depth=3, learning_rate=0.05, random_state=42)
        return LogisticRegression(C=1.0, class_weight="balanced", max_iter=500, random_state=42)

    @classmethod
    def featurize_vector(cls, fv: LongitudinalFeatureVector) -> List[float]:
        """Convert LongitudinalFeatureVector into fixed numeric feature vector (NaN for missing)."""
        def _get(marker: str, attr: str) -> float:
            t = fv.biomarker_trends.get(marker)
            if t is None:
                return float("nan")
            val = getattr(t, attr, None)
            return float(val) if val is not None else float("nan")

        return [
            _get("systolic_bp", "latest_value"),
            _get("systolic_bp", "rate_of_change_per_30d"),
            _get("hba1c_percent", "latest_value"),
            _get("hba1c_percent", "rate_of_change_per_30d"),
            _get("ldl_cholesterol_mg_dl", "latest_value"),
            _get("ldl_cholesterol_mg_dl", "rate_of_change_per_30d"),
            _get("egfr_ml_min", "latest_value"),
            float(fv.symptom_severity_latest) if fv.symptom_severity_latest is not None else float("nan"),
            float(fv.missingness_rate),
            1.0 if fv.adherence_inconsistent else 0.0,
        ]

    def train_and_evaluate(
        self,
        records: List[Dict[str, Any]],
        dataset_name: str = "synthetic_longitudinal_benchmark",
        version: str = "1.0.0",
    ) -> Dict[str, Any]:
        """Train using strict patient-grouped temporal split and fit preprocessing ONLY on X_train."""
        train_recs, val_recs, test_recs = temporal_patient_split(records)
        if not train_recs or not test_recs:
            raise ValueError("Insufficient distinct patients for temporal train/test split.")

        x_train = np.array([r["features"] for r in train_recs], dtype=np.float64)
        y_train = np.array([int(r["label"]) for r in train_recs], dtype=np.int64)
        x_test = np.array([r["features"] for r in test_recs], dtype=np.float64)
        y_test = np.array([int(r["label"]) for r in test_recs], dtype=np.int64)

        # Imputer & Scaler inside Pipeline are fitted strictly on X_train
        self.pipeline = Pipeline([
            ("imputer", SimpleImputer(strategy="median")),
            ("scaler", StandardScaler()),
            ("classifier", self._build_estimator(self.algorithm)),
        ])
        self.pipeline.fit(x_train, y_train)

        test_metrics = self._compute_metrics(x_test, y_test)
        val_metrics = {}
        if val_recs:
            x_val = np.array([r["features"] for r in val_recs], dtype=np.float64)
            y_val = np.array([int(r["label"]) for r in val_recs], dtype=np.int64)
            val_metrics = self._compute_metrics(x_val, y_val)

        self.metadata = ModelMetadata(
            model_id=f"trajectory_{self.algorithm}_{self.horizon_days}d_v{version}",
            model_name=f"Disease Trajectory Forecaster ({self.algorithm}, {self.horizon_days}d)",
            model_type=self.algorithm,
            version=version,
            dataset_name=dataset_name,
            target_column=f"worsening_within_{self.horizon_days}d",
            feature_columns=list(self.FEATURE_NAMES),
            metrics=test_metrics,
            hyperparameters={"horizon_days": self.horizon_days, "algorithm": self.algorithm},
        )
        return {
            "model_id": self.metadata.model_id,
            "train_count": len(train_recs),
            "val_count": len(val_recs),
            "test_count": len(test_recs),
            "val_metrics": val_metrics,
            "test_metrics": test_metrics,
        }

    def _compute_metrics(self, x: np.ndarray, y: np.ndarray) -> Dict[str, float]:
        assert self.pipeline is not None
        probs = self.pipeline.predict_proba(x)[:, 1]
        preds = (probs >= 0.5).astype(int)
        try:
            auroc = float(roc_auc_score(y, probs))
        except ValueError:
            auroc = 0.5
        try:
            auprc = float(average_precision_score(y, probs))
        except ValueError:
            auprc = 0.0
        sens = float(recall_score(y, preds, zero_division=0))
        cm = confusion_matrix(y, preds, labels=[0, 1])
        tn, fp = int(cm[0][0]), int(cm[0][1])
        spec = float(tn / (tn + fp)) if (tn + fp) > 0 else 0.0
        brier = float(brier_score_loss(y, probs))
        return {
            "auroc": round(auroc, 4),
            "auprc": round(auprc, 4),
            "sensitivity": round(sens, 4),
            "specificity": round(spec, 4),
            "brier_score": round(brier, 4),
        }

    def predict_worsening_probability(self, fv: LongitudinalFeatureVector) -> float:
        """Predict probability of worsening within horizon_days."""
        if self.pipeline is None:
            raise RuntimeError("LongitudinalMLForecaster has not been trained or loaded.")
        vec = np.array([self.featurize_vector(fv)], dtype=np.float64)
        return round(float(self.pipeline.predict_proba(vec)[0, 1]), 4)

    def save(self, models_dir: Optional[Any] = None) -> Tuple[Any, Any]:
        if self.pipeline is None or self.metadata is None:
            raise RuntimeError("Cannot save untrained model.")
        return save_model_bundle(self.pipeline, self.metadata, models_dir=models_dir)

    @classmethod
    def load(cls, model_id: str, models_dir: Optional[Any] = None) -> "LongitudinalMLForecaster":
        pipeline, metadata = load_model_bundle(model_id, models_dir=models_dir)
        inst = cls(
            algorithm=metadata.model_type,
            horizon_days=int(metadata.hyperparameters.get("horizon_days", 180)),
        )
        inst.pipeline = pipeline
        inst.metadata = metadata
        return inst


def generate_synthetic_longitudinal_benchmark(
    num_patients: int = 120,
    seed: int = 42,
) -> Dict[str, Any]:
    """Generate a clearly labeled synthetic longitudinal benchmark for pipeline verification.

    WARNING: Synthetic data ONLY for reproducible software & leakage-prevention testing.
    Never present metrics from this benchmark as clinical validation.
    """
    rng = np.random.default_rng(seed)
    extractor = LongitudinalFeatureExtractor()
    records: List[Dict[str, Any]] = []
    base_date = datetime(2025, 1, 1, tzinfo=timezone.utc)

    for i in range(num_patients):
        pid = f"SYNTH-P-{i:04d}"
        start_dt = base_date + timedelta(days=int(rng.integers(0, 180)))
        sbp0 = float(rng.normal(130.0, 15.0))
        a1c0 = float(rng.normal(6.2, 1.0))
        ldl0 = float(rng.normal(125.0, 28.0))
        egfr0 = float(np.clip(rng.normal(80.0, 15.0), 25.0, 120.0))
        non_adherent = bool(rng.random() < 0.30)

        # Worsening slope driver
        drift = float(rng.normal(0.5 if non_adherent else -0.1, 0.8))
        lab_history = []
        for visit in range(3):
            dt = start_dt + timedelta(days=visit * int(rng.integers(25, 45)))
            lab_history.append({
                "id": f"{pid}-L{visit}",
                "test_date": dt.isoformat(),
                "biomarkers": {
                    "systolic_bp": round(sbp0 + visit * drift * 5.0 + float(rng.normal(0, 2.0)), 1),
                    "hba1c_percent": round(a1c0 + visit * drift * 0.25 + float(rng.normal(0, 0.1)), 2),
                    "ldl_cholesterol_mg_dl": round(ldl0 + visit * drift * 8.0 + float(rng.normal(0, 4.0)), 1),
                    "egfr_ml_min": round(max(15.0, egfr0 - visit * drift * 2.5), 1),
                },
            })

        pred_time = parse_ts = datetime.fromisoformat(lab_history[-1]["test_date"])
        fv = extractor.extract(
            lab_history=lab_history,
            medical_history={"notes": "non-adherent" if non_adherent else "adherent"},
            patient_id=pid,
            cutoff_time=pred_time,
        )
        # Future worsening outcome strictly after pred_time
        risk_logit = (
            0.04 * (sbp0 - 130.0)
            + 0.45 * (a1c0 - 6.5)
            + 0.9 * drift
            + (0.7 if non_adherent else 0.0)
            + float(rng.normal(0, 0.4))
        )
        prob = 1.0 / (1.0 + math.exp(-risk_logit))
        label = int(rng.random() < prob)

        records.append({
            "patient_id": pid,
            "prediction_time": pred_time.isoformat(),
            "features": LongitudinalMLForecaster.featurize_vector(fv),
            "label": label,
        })

    return {
        "is_synthetic_benchmark": True,
        "clinically_validated": False,
        "records": records,
    }
