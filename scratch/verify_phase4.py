import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from fastapi.testclient import TestClient
from backend.main import app

client = TestClient(app)

print("--- Phase 4: Runtime Verification ---")

hospital_payload = {
    "status": "HOSPITALIZED",
    "person": {
        "first_name": "Test",
        "last_name": "Patient",
        "gender": "Male"
    },
    "hospital_record": {
        "hospital_name": "Test Hospital",
        "condition_summary": "Critical"
    },
    "location": {
        "location_type": "Found",
        "address": "Route 66"
    }
}
res = client.post("/api/cases/", json=hospital_payload)
print(f"Hospital Record Create Status Code: {res.status_code}")
assert res.status_code == 200

shelter_payload = {
    "status": "IN_SHELTER",
    "person": {
        "first_name": "Test",
        "last_name": "Person 2",
        "gender": "Female"
    },
    "shelter_record": {
        "shelter_name": "Test Shelter A"
    },
    "location": {
        "location_type": "Found",
        "address": "Zone 5"
    }
}
res = client.post("/api/cases/", json=shelter_payload)
print(f"Shelter Record Create Status Code: {res.status_code}")
assert res.status_code == 200

rescue_payload = {
    "status": "FOUND",
    "person": {
        "first_name": "Unknown",
        "last_name": "Child",
        "age": 10
    },
    "rescue_record": {
        "rescue_team": "Test Rescue Team"
    },
    "location": {
        "location_type": "Found",
        "address": "Lake Area"
    }
}
res = client.post("/api/cases/", json=rescue_payload)
print(f"Rescue Record Create Status Code: {res.status_code}")
assert res.status_code == 200

print("\n--- PHASE 4 RUNTIME CHECKS PASSED SUCCESSFULLY ---")
