import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from fastapi.testclient import TestClient
from backend.main import app
from backend.database.seed import seed_data

print("--- 1. Database Initialization & Seeding ---")
seed_data()

client = TestClient(app)

print("\n--- 2. API Health Check ---")
res_health = client.get("/api/health")
print(f"Health Status Code: {res_health.status_code}")
print(f"Health Response: {res_health.json()}")
assert res_health.status_code == 200

print("\n--- 3. Case Creation (POST /api/cases) ---")
new_case_payload = {
    "status": "New",
    "person": {
        "first_name": "Antigravity",
        "last_name": "TestUser",
        "age": 28,
        "gender": "Male",
        "distinguishing_features": "Tattoo on right shoulder"
    }
}
res_create = client.post("/api/cases/", json=new_case_payload)
print(f"Create Status Code: {res_create.status_code}")
created_case = res_create.json()
print(f"Created VRN ID: {created_case.get('vrn_id')}")
print(f"Created Case Details: {created_case}")
assert res_create.status_code == 200
assert created_case.get("vrn_id").startswith("VRN-")

vrn_id = created_case.get("vrn_id")
case_id = created_case.get("id")

print("\n--- 4. Case Retrieval (GET /api/cases) ---")
res_all = client.get("/api/cases/")
print(f"List Cases Status Code: {res_all.status_code}")
all_cases = res_all.json()
print(f"Total Cases Count: {len(all_cases)}")
assert res_all.status_code == 200

print("\n--- 5. Case Retrieval by VRN ID (GET /api/cases/{case_id}) ---")
res_single = client.get(f"/api/cases/{vrn_id}")
print(f"Single Case Status Code: {res_single.status_code}")
single_case = res_single.json()
print(f"Retrieved Person: {single_case.get('person')}")
assert res_single.status_code == 200

print("\n--- 6. Case Patch Status (PATCH /api/cases/{case_id}) ---")
res_patch = client.patch(f"/api/cases/{vrn_id}", json={"status": "Verified"})
print(f"Patch Status Code: {res_patch.status_code}")
patched_case = res_patch.json()
print(f"Updated Status: {patched_case.get('status')}")
assert res_patch.status_code == 200
assert patched_case.get("status") == "Verified"

print("\n--- ALL PHASE 2 RUNTIME CHECKS PASSED SUCCESSFULLY ---")
