"""Longitudinal clinical data processing and temporal feature extraction.

Extracts biomarker and symptom trajectories from irregularly sampled patient records
without fabricating or interpolating missing clinical measurements.
"""

from datetime import datetime, timezone
import math
from typing import Any, Dict, List, Optional, Tuple

from app.schemas.trajectory import (
    BiomarkerTrendSummary,
    LongitudinalFeatureVector,
    TrajectoryDirection,
)


# Canonical biomarker clinical reference thresholds (upper normal / abnormal cutoffs)
BIOMARKER_SPECS: Dict[str, Dict[str, Any]] = {
    "systolic_bp": {"unit": "mmHg", "abnormal_high": 140.0, "abnormal_low": 90.0, "higher_is_worse": True},
    "diastolic_bp": {"unit": "mmHg", "abnormal_high": 90.0, "abnormal_low": 60.0, "higher_is_worse": True},
    "fasting_blood_glucose_mg_dl": {"unit": "mg/dL", "abnormal_high": 126.0, "abnormal_low": 70.0, "higher_is_worse": True},
    "hba1c_percent": {"unit": "%", "abnormal_high": 6.5, "abnormal_low": None, "higher_is_worse": True},
    "ldl_cholesterol_mg_dl": {"unit": "mg/dL", "abnormal_high": 130.0, "abnormal_low": None, "higher_is_worse": True},
    "total_cholesterol_mg_dl": {"unit": "mg/dL", "abnormal_high": 200.0, "abnormal_low": None, "higher_is_worse": True},
    "hdl_cholesterol_mg_dl": {"unit": "mg/dL", "abnormal_high": None, "abnormal_low": 40.0, "higher_is_worse": False},
    "triglycerides_mg_dl": {"unit": "mg/dL", "abnormal_high": 150.0, "abnormal_low": None, "higher_is_worse": True},
    "serum_creatinine_mg_dl": {"unit": "mg/dL", "abnormal_high": 1.3, "abnormal_low": None, "higher_is_worse": True},
    "egfr_ml_min": {"unit": "mL/min/1.73m2", "abnormal_high": None, "abnormal_low": 60.0, "higher_is_worse": False},
    "bnp_pg_ml": {"unit": "pg/mL", "abnormal_high": 100.0, "abnormal_low": None, "higher_is_worse": True},
    "cardiac_troponin_ng_ml": {"unit": "ng/mL", "abnormal_high": 0.04, "abnormal_low": None, "higher_is_worse": True},
}


def parse_utc_timestamp(raw_ts: Any) -> Optional[datetime]:
    """Parse date/datetime/ISO string into timezone-aware UTC datetime."""
    if raw_ts is None:
        return None
    if isinstance(raw_ts, datetime):
        return raw_ts.replace(tzinfo=timezone.utc) if raw_ts.tzinfo is None else raw_ts.astimezone(timezone.utc)
    if hasattr(raw_ts, "year") and hasattr(raw_ts, "month") and hasattr(raw_ts, "day"):
        return datetime(raw_ts.year, raw_ts.month, raw_ts.day, tzinfo=timezone.utc)
    try:
        dt = datetime.fromisoformat(str(raw_ts).replace("Z", "+00:00"))
        return dt.replace(tzinfo=timezone.utc) if dt.tzinfo is None else dt.astimezone(timezone.utc)
    except (ValueError, TypeError):
        return None


class LongitudinalFeatureExtractor:
    """Extracts temporal clinical features from irregular multi-visit records.

    Never interpolates missing clinical measurements to fabricate observations.
    """

    def __init__(self, tracked_biomarkers: Optional[List[str]] = None) -> None:
        self.tracked_biomarkers = tracked_biomarkers or list(BIOMARKER_SPECS.keys())

    def extract(
        self,
        lab_history: Optional[List[Dict[str, Any]]] = None,
        symptom_history: Optional[List[Dict[str, Any]]] = None,
        medical_history: Optional[Dict[str, Any]] = None,
        patient_id: Optional[str] = None,
        cutoff_time: Optional[datetime] = None,
    ) -> LongitudinalFeatureVector:
        """Extract chronological temporal features strictly up to cutoff_time (preventing future leakage)."""
        cutoff_utc = parse_utc_timestamp(cutoff_time)
        labs = lab_history or []
        symptoms = symptom_history or []
        history = medical_history or {}

        # Filter and sort lab visits chronologically (strictly <= cutoff_time)
        parsed_labs: List[Tuple[datetime, str, Dict[str, Any]]] = []
        all_source_ids: List[str] = []
        for idx, item in enumerate(labs):
            ts = parse_utc_timestamp(item.get("test_date") or item.get("timestamp") or item.get("created_at"))
            if ts is None:
                continue
            if cutoff_utc is not None and ts > cutoff_utc:
                continue
            rec_id = str(item.get("id") or item.get("record_id") or f"lab_{idx}")
            biomarkers = item.get("biomarkers") if isinstance(item.get("biomarkers"), dict) else item
            parsed_labs.append((ts, rec_id, biomarkers))
            all_source_ids.append(rec_id)

        parsed_labs.sort(key=lambda x: x[0])

        # Compute per-biomarker trends without interpolating missing values
        trends: Dict[str, BiomarkerTrendSummary] = {}
        missing_count = 0
        for marker in self.tracked_biomarkers:
            spec = BIOMARKER_SPECS.get(marker, {})
            points: List[Tuple[datetime, float, str]] = []
            for ts, rec_id, bmap in parsed_labs:
                val = bmap.get(marker)
                if val is None or isinstance(val, bool):
                    continue
                try:
                    num = float(val)
                    if not math.isnan(num) and not math.isinf(num):
                        points.append((ts, num, rec_id))
                except (ValueError, TypeError):
                    continue

            summary = self._summarize_biomarker_series(marker, points, spec)
            trends[marker] = summary
            if summary.is_missing:
                missing_count += 1

        # Symptom severity progression (strictly <= cutoff_time)
        sym_points: List[Tuple[datetime, float, str]] = []
        for idx, s in enumerate(symptoms):
            ts = parse_utc_timestamp(s.get("created_at") or s.get("timestamp") or s.get("reported_at"))
            if ts is None:
                continue
            if cutoff_utc is not None and ts > cutoff_utc:
                continue
            sev = s.get("severity_self_rating") if s.get("severity_self_rating") is not None else s.get("severity")
            if sev is not None:
                try:
                    sev_num = float(sev)
                    rec_id = str(s.get("id") or f"sym_{idx}")
                    sym_points.append((ts, sev_num, rec_id))
                    all_source_ids.append(rec_id)
                except (ValueError, TypeError):
                    continue

        sym_points.sort(key=lambda x: x[0])
        sym_latest = sym_points[-1][1] if sym_points else None
        sym_slope = None
        if len(sym_points) >= 2:
            dt_days = (sym_points[-1][0] - sym_points[0][0]).total_seconds() / 86400.0
            if dt_days > 0:
                sym_slope = round(((sym_points[-1][1] - sym_points[0][1]) / dt_days) * 30.0, 4)

        # Medication & adherence context
        meds = history.get("current_medications") or []
        notes = str(history.get("notes") or "").lower()
        adherence_inconsistent = any(
            str(m.get("adherence") or "").lower() in ["inconsistent", "poor", "non_compliant", "partial", "non-adherent"]
            for m in meds
            if isinstance(m, dict)
        ) or any(w in notes for w in ["non-compliance", "forgets", "inconsistent", "misses doses", "non-adherent"])

        # Overall window & missingness
        all_ts = [p[0] for p in parsed_labs] + [p[0] for p in sym_points]
        window_days = ((max(all_ts) - min(all_ts)).total_seconds() / 86400.0) if len(all_ts) >= 2 else 0.0
        missingness_rate = round(missing_count / max(1, len(self.tracked_biomarkers)), 4)

        return LongitudinalFeatureVector(
            patient_id=patient_id,
            total_lab_visits=len(parsed_labs),
            total_symptom_reports=len(sym_points),
            observation_window_days=round(window_days, 2),
            missingness_rate=missingness_rate,
            biomarker_trends=trends,
            symptom_severity_latest=sym_latest,
            symptom_severity_slope_per_30d=sym_slope,
            medication_count=len(meds),
            adherence_inconsistent=adherence_inconsistent,
            source_record_ids=all_source_ids,
        )

    def _summarize_biomarker_series(
        self,
        marker: str,
        points: List[Tuple[datetime, float, str]],
        spec: Dict[str, Any],
    ) -> BiomarkerTrendSummary:
        unit = spec.get("unit")
        if not points:
            return BiomarkerTrendSummary(
                biomarker_name=marker,
                unit=unit,
                observation_count=0,
                is_missing=True,
                insufficient_history=True,
                trend_direction=TrajectoryDirection.INSUFFICIENT_DATA,
            )

        count = len(points)
        latest_ts, latest_val, _ = points[-1]
        rec_ids = [p[2] for p in points]

        if count == 1:
            return BiomarkerTrendSummary(
                biomarker_name=marker,
                unit=unit,
                observation_count=1,
                latest_value=round(latest_val, 4),
                latest_timestamp=latest_ts.isoformat(),
                is_missing=False,
                insufficient_history=True,
                trend_direction=TrajectoryDirection.INSUFFICIENT_DATA,
                source_record_ids=rec_ids,
            )

        prev_ts, prev_val, _ = points[-2]
        first_ts, first_val, _ = points[0]
        dt_prev_days = max(0.0, (latest_ts - prev_ts).total_seconds() / 86400.0)
        span_days = max(0.0, (latest_ts - first_ts).total_seconds() / 86400.0)
        freq_30d = round((count / max(span_days, 1.0)) * 30.0, 4) if span_days > 0 else None

        abs_change = round(latest_val - prev_val, 4)
        pct_change = round(((latest_val - prev_val) / abs(prev_val)) * 100.0, 2) if prev_val != 0 else None
        rate_30d = round(((latest_val - prev_val) / dt_prev_days) * 30.0, 4) if dt_prev_days > 0 else None

        vals = [p[1] for p in points]
        ma3 = round(sum(vals[-3:]) / 3.0, 4) if count >= 3 else None
        mean_v = sum(vals) / count
        std_v = round(math.sqrt(sum((v - mean_v) ** 2 for v in vals) / (count - 1)), 4)

        # Abnormal value duration (sum of intervals where observation was abnormal)
        ab_high = spec.get("abnormal_high")
        ab_low = spec.get("abnormal_low")
        abnormal_days = 0.0
        for i in range(len(points) - 1):
            v_curr = points[i][1]
            is_ab = (ab_high is not None and v_curr >= ab_high) or (ab_low is not None and v_curr <= ab_low)
            if is_ab:
                abnormal_days += max(0.0, (points[i + 1][0] - points[i][0]).total_seconds() / 86400.0)

        # Determine clinical trend direction
        higher_worse = spec.get("higher_is_worse", True)
        direction = TrajectoryDirection.STABLE
        if rate_30d is not None:
            rel_threshold = max(abs(prev_val) * 0.03, 1e-4)
            if abs(abs_change) > rel_threshold:
                if (abs_change > 0 and higher_worse) or (abs_change < 0 and not higher_worse):
                    direction = TrajectoryDirection.WORSENING
                else:
                    direction = TrajectoryDirection.IMPROVING

        return BiomarkerTrendSummary(
            biomarker_name=marker,
            unit=unit,
            observation_count=count,
            latest_value=round(latest_val, 4),
            previous_value=round(prev_val, 4),
            latest_timestamp=latest_ts.isoformat(),
            time_since_previous_days=round(dt_prev_days, 2),
            observation_span_days=round(span_days, 2),
            sampling_frequency_per_30d=freq_30d,
            absolute_change=abs_change,
            percentage_change=pct_change,
            rate_of_change_per_30d=rate_30d,
            moving_average_3=ma3,
            variability_std=std_v,
            abnormal_value_duration_days=round(abnormal_days, 2),
            is_missing=False,
            insufficient_history=False,
            trend_direction=direction,
            source_record_ids=rec_ids,
        )
