import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from fastapi.testclient import TestClient
from backend.main import app

client = TestClient(app)

print("--- 1. Phase 3: Runtime Verification ---")
new_case_payload = {
    "status": "New",
    "person": {
        "first_name": "Sarah",
        "last_name": "Connor",
        "age": 40,
        "gender": "Female",
        "distinguishing_features": "Notes: Needs medication"
    },
    "family_report": {
        "reporter_name": "John Connor",
        "reporter_contact": "555-0928",
        "relationship_to_person": "Son"
    },
    "location": {
        "location_type": "Last Known",
        "address": "Tech Noir Nightclub"
    }
}
res_create = client.post("/api/cases/", json=new_case_payload)
print(f"Create Status Code: {res_create.status_code}")
created_case = res_create.json()
print(f"Created VRN ID: {created_case.get('vrn_id')}")

assert res_create.status_code == 200
assert created_case.get("vrn_id").startswith("VRN-")
vrn_id = created_case.get("vrn_id")

res_single = client.get(f"/api/cases/{vrn_id}")
single_case = res_single.json()
print(f"Retrieved Person: {single_case.get('person')}")
print(f"Family Reports: {single_case.get('family_reports')}")
print(f"Location Records: {single_case.get('location_records')}")
assert single_case.get('family_reports')[0]['reporter_name'] == "John Connor"

print("\n--- PHASE 3 RUNTIME CHECKS PASSED SUCCESSFULLY ---")
