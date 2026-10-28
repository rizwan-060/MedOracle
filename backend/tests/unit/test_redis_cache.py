"""Unit tests for Redis & In-Memory Caching Architecture and DB Query Caching (Step 9.1)."""

from datetime import date, datetime, timezone
import time
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.core.cache import (
    CacheManager,
    InMemoryCacheBackend,
    dict_to_model,
    model_to_dict,
)
from app.database.models import Base, LabResult, MedicalHistory, PatientProfile, User
from app.database.repositories import (
    LabResultRepository,
    MedicalHistoryRepository,
    PatientProfileRepository,
    UserRepository,
)


@pytest.fixture
def clean_cache() -> CacheManager:
    """Provide an isolated, memory-backed CacheManager for testing."""
    backend = InMemoryCacheBackend()
    manager = CacheManager(backend=backend)
    manager.clear()
    return manager


@pytest.fixture
def in_memory_db():
    """Create an isolated in-memory SQLite database session."""
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    session_factory = sessionmaker(bind=engine)
    session = session_factory()
    try:
        yield session
    finally:
        session.close()


# =============================================================================
# 1. In-Memory Cache CRUD & Expiration Tests
# =============================================================================
def test_in_memory_cache_crud(clean_cache: CacheManager):
    """Verify basic set, get, delete, and overwrite operations."""
    key = clean_cache.build_key("test", "user", "123")

    # Initially missing
    assert clean_cache.get(key) is None

    # Set value
    assert clean_cache.set(key, {"role": "patient", "name": "Alice"}, ttl=300) is True

    # Retrieve value
    cached = clean_cache.get(key)
    assert cached is not None
    assert cached["role"] == "patient"
    assert cached["name"] == "Alice"

    # Delete
    assert clean_cache.delete(key) is True
    assert clean_cache.get(key) is None


def test_in_memory_cache_ttl_expiration(clean_cache: CacheManager):
    """Verify that entries expire after their TTL has elapsed."""
    key = clean_cache.build_key("test", "temp_token")

    # Set with 1-second TTL
    clean_cache.set(key, "short_lived_val", ttl=1)
    assert clean_cache.get(key) == "short_lived_val"

    # Sleep past expiration
    time.sleep(1.05)
    assert clean_cache.get(key) is None


def test_in_memory_cache_pattern_deletion(clean_cache: CacheManager):
    """Verify delete_pattern and namespace invalidation."""
    k1 = clean_cache.build_key("db", "patient", "user_1", "profile")
    k2 = clean_cache.build_key("db", "patient", "user_1", "labs")
    k3 = clean_cache.build_key("db", "patient", "user_2", "profile")

    clean_cache.set(k1, {"p": 1})
    clean_cache.set(k2, {"l": 1})
    clean_cache.set(k3, {"p": 2})

    # Invalidate user_1 pattern
    deleted = clean_cache.delete_pattern(clean_cache.build_key("db", "patient", "user_1", "*"))
    assert deleted == 2

    # user_1 keys gone, user_2 key remains
    assert clean_cache.get(k1) is None
    assert clean_cache.get(k2) is None
    assert clean_cache.get(k3) == {"p": 2}


# =============================================================================
# 2. ORM Model Serialization & Reconstruction Tests
# =============================================================================
def test_model_serialization_and_reconstruction():
    """Verify model_to_dict and dict_to_model on PatientProfile without session attachment."""
    profile = PatientProfile(
        user_id="usr_abc_123",
        date_of_birth=date(1985, 4, 12),
        gender="female",
        height_cm=165.5,
        weight_kg=62.0,
        blood_group="O+",
    )

    data = model_to_dict(profile)
    assert data is not None
    assert data["user_id"] == "usr_abc_123"
    assert data["date_of_birth"] == "1985-04-12"
    assert data["height_cm"] == 165.5

    # Reconstruct unmanaged model instance
    reconstructed = dict_to_model(PatientProfile, data)
    assert reconstructed is not None
    assert isinstance(reconstructed, PatientProfile)
    assert reconstructed.user_id == "usr_abc_123"
    assert reconstructed.date_of_birth == date(1985, 4, 12)
    assert reconstructed.gender == "female"
    assert reconstructed.height_cm == 165.5


def test_cache_manager_model_helpers(clean_cache: CacheManager):
    """Test get_model, set_model, get_model_list, set_model_list."""
    lab1 = LabResult(
        id="lab_1",
        user_id="usr_1",
        test_date=datetime(2026, 10, 20, 10, 0, 0, tzinfo=timezone.utc),
        biomarkers={"glucose": 95.0, "total_cholesterol": 180.0},
    )
    lab2 = LabResult(
        id="lab_2",
        user_id="usr_1",
        test_date=datetime(2026, 10, 25, 10, 0, 0, tzinfo=timezone.utc),
        biomarkers={"glucose": 98.0, "total_cholesterol": 182.0},
    )

    key_single = clean_cache.build_key("db", "labs", "usr_1", "latest")
    key_list = clean_cache.build_key("db", "labs", "usr_1", "list")

    # 1. Single model cache
    assert clean_cache.set_model(key_single, lab2) is True
    retrieved_single = clean_cache.get_model(key_single, LabResult)
    assert retrieved_single is not None
    assert retrieved_single.id == "lab_2"
    assert retrieved_single.biomarkers["glucose"] == 98.0

    # 2. Model list cache
    assert clean_cache.set_model_list(key_list, [lab1, lab2]) is True
    retrieved_list = clean_cache.get_model_list(key_list, LabResult)
    assert retrieved_list is not None
    assert len(retrieved_list) == 2
    assert retrieved_list[0].id == "lab_1"
    assert retrieved_list[1].id == "lab_2"


# =============================================================================
# 3. Database Repository Caching & Invalidation Tests
# =============================================================================
def test_patient_profile_repository_caching_and_invalidation(in_memory_db, clean_cache: CacheManager):
    """Verify that PatientProfileRepository queries are cached and invalidated on update."""
    repo = PatientProfileRepository(in_memory_db, cache=clean_cache)
    user_id = "test_user_pat_1"

    # Create profile in DB
    created = repo.create_or_update(
        user_id=user_id,
        gender="male",
        height_cm=178.0,
        weight_kg=75.0,
    )
    assert created.gender == "male"

    # First get: fetches from DB and stores into cache
    cache_key = clean_cache.build_key("db", "patient_profile", user_id)
    assert clean_cache.get(cache_key) is None

    p1 = repo.get_by_user_id(user_id)
    assert p1 is not None
    assert p1.height_cm == 178.0

    # Verify key is now present in cache
    cached_val = clean_cache.get(cache_key)
    assert cached_val is not None
    assert cached_val["height_cm"] == 178.0

    # Update profile: must invalidate cache
    updated = repo.create_or_update(user_id=user_id, weight_kg=78.5)
    assert updated.weight_kg == 78.5
    assert clean_cache.get(cache_key) is None  # Invalidated!

    # Re-fetch: repopulates cache with new values
    p2 = repo.get_by_user_id(user_id)
    assert p2.weight_kg == 78.5
    assert clean_cache.get(cache_key)["weight_kg"] == 78.5


def test_medical_history_and_labs_caching(in_memory_db, clean_cache: CacheManager):
    """Verify caching and invalidation across MedicalHistory and LabResult repositories."""
    med_repo = MedicalHistoryRepository(in_memory_db, cache=clean_cache)
    lab_repo = LabResultRepository(in_memory_db, cache=clean_cache)
    user_id = "test_user_med_2"

    # 1. Medical History
    history = med_repo.create_or_update(
        user_id=user_id,
        chronic_conditions=["hypertension"],
        current_medications=["lisinopril"],
    )
    hist_key = clean_cache.build_key("db", "medical_history_latest", user_id)

    # First read caches it
    h1 = med_repo.get_latest_by_user_id(user_id)
    assert h1.chronic_conditions == ["hypertension"]
    assert clean_cache.get(hist_key) is not None

    # Update invalidates it
    med_repo.create_or_update(user_id=user_id, allergies=["penicillin"])
    assert clean_cache.get(hist_key) is None

    # 2. Lab Results
    lab = lab_repo.create(
        user_id=user_id,
        test_date=date(2026, 10, 28),
        biomarkers={"fasting_glucose": 105.0},
    )
    lab_key = clean_cache.build_key("db", "lab_result_latest", user_id)

    # Read caches it
    l1 = lab_repo.get_latest_by_user_id(user_id)
    assert l1.biomarkers["fasting_glucose"] == 105.0
    assert clean_cache.get(lab_key) is not None

    # Deleting invalidates it
    lab_repo.delete(lab.id, user_id=user_id)
    assert clean_cache.get(lab_key) is None


def test_user_repository_jwt_caching(in_memory_db, clean_cache: CacheManager):
    """Verify that UserRepository caches get_by_id calls for fast JWT auth verification."""
    repo = UserRepository(in_memory_db, cache=clean_cache)
    user = repo.create("cached_user@example.com", "hashed_pwd_123", "Cached User")

    user_key = clean_cache.build_key("db", "user", user.id)
    assert clean_cache.get(user_key) is None

    # First get caches user
    u1 = repo.get_by_id(user.id)
    assert u1 is not None
    assert u1.email == "cached_user@example.com"
    assert clean_cache.get(user_key) is not None

    # Second get returns from cache without hit to DB
    u2 = repo.get_by_id(user.id)
    assert u2.email == "cached_user@example.com"
    assert clean_cache.hits >= 1


def test_cache_manager_stats_and_health(clean_cache: CacheManager):
    """Verify stats tracking, hit ratio, and health checks."""
    k = clean_cache.build_key("test", "stat_key")
    clean_cache.get(k)  # Miss (+1)
    clean_cache.set(k, "val")
    clean_cache.get(k)  # Hit (+1)

    stats = clean_cache.get_stats()
    assert stats["hits"] == 1
    assert stats["misses"] == 1
    assert stats["hit_ratio_pct"] == 50.0
    assert stats["is_healthy"] is True
    assert stats["backend"] == "in_memory"
