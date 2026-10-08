from backend.services.matching.name_matcher import compare_names
from backend.services.matching.attribute_matcher import compare_age, compare_gender, compare_physical
from backend.services.matching.location_matcher import compare_location
from backend.services.matching.time_matcher import compare_time
from backend.services.matching.scoring import calculate_weighted_score, calculate_confidence
from datetime import datetime, timedelta

def test_exact_name_match():
    assert compare_names("Arjun Kumar", "arjun kumar") == 1.0

def test_fuzzy_name_match():
    score = compare_names("Arjun Kumar", "Arjun K")
    assert score > 0.7 # Should have a high score

def test_age_compatibility():
    assert compare_age(32, 32) == 1.0
    assert compare_age(32, 35) == 0.8
    assert compare_age(32, 40) == 0.5

def test_age_mismatch():
    assert compare_age(32, 64) == 0.0

def test_location_proximity():
    # Right now our mock just does fuzzy string match
    assert compare_location("Shelter A", "shelter a") == 1.0
    assert compare_location("Shelter A", "Shelter B") > 0.5 # sequence matcher

def test_time_compatibility():
    now = datetime.now()
    assert compare_time(now, now) == 1.0
    assert compare_time(now, now - timedelta(hours=1)) == 1.0
    assert compare_time(now, now - timedelta(hours=5)) == 0.8
    assert compare_time(now, now - timedelta(hours=20)) == 0.5
    assert compare_time(now, now - timedelta(hours=50)) == 0.2

def test_physical_similarity():
    assert compare_physical("Blue jacket, scar", "Blue jacket") > 0.5

def test_missing_attributes():
    assert compare_age(None, 32) is None
    assert compare_gender("Male", "Unknown") is None
    assert compare_physical(None, "Scar") is None

def test_weighted_scoring_strong():
    signals = {
        "name": 0.94,
        "age": 1.0,
        "gender": 1.0,
        "location": 0.87,
        "time": 0.91,
        "physical": 0.82,
        "face": 0.95
    }
    score = calculate_weighted_score(signals)
    assert score > 0.90
    assert calculate_confidence(score) == "HIGH"

def test_weighted_scoring_weak():
    signals = {
        "name": 0.2,
        "age": 0.0,
        "gender": 0.0,
        "location": 0.2,
        "time": 0.5,
        "physical": 0.1,
        "face": 0.1
    }
    score = calculate_weighted_score(signals)
    assert score < 0.3
    assert calculate_confidence(score) == "LOW"

def test_scoring_with_missing_signals():
    # Only name and age available
    signals = {
        "name": 1.0,
        "age": 1.0,
        "gender": None,
        "location": None,
        "time": None,
        "physical": None,
        "face": None
    }
    score = calculate_weighted_score(signals)
    assert score == 1.0 # Should normalize to available weight
