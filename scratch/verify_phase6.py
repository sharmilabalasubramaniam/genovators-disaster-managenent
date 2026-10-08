import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from fastapi.testclient import TestClient
from backend.main import app

client = TestClient(app)

print("--- Phase 6: Runtime Verification ---")

res = client.get("/api/cases/")
assert res.status_code == 200
cases = res.json()

family_case = None
for c in cases:
    if c['family_reports']:
        family_case = c
        break

assert family_case, "No family case found."
vrn_id = family_case['vrn_id']

print(f"Running Matching for {vrn_id}")
match_res = client.post(f"/api/matching/cases/{vrn_id}")
assert match_res.status_code == 200
candidates = match_res.json()['candidates']
assert len(candidates) > 0

candidate_vrn_id = candidates[0]['record_id']
print(f"Starting verification for {vrn_id} against {candidate_vrn_id}")

start_res = client.post(f"/api/verification/{vrn_id}/start", json={"candidate_vrn_id": candidate_vrn_id})
assert start_res.status_code == 200

ver_res = client.get(f"/api/verification/{vrn_id}/candidate/{candidate_vrn_id}")
assert ver_res.status_code == 200
ver_data = ver_res.json()
print(f"Verification Status: {ver_data['status']}")
print(f"Evidence Strength Score: {ver_data['strength']['strength_score']:.2f}")

req_res = client.post(f"/api/verification/{vrn_id}/request-evidence", json={"notes": "Need more context from shelter"})
assert req_res.status_code == 200
print(f"Status after request-evidence: {req_res.json()['verification_status']}")

app_res = client.post(f"/api/verification/{vrn_id}/approve")
assert app_res.status_code == 200
print(f"Status after approve: {app_res.json()['verification_status']}")

case_res = client.get(f"/api/cases/{vrn_id}")
case_status = case_res.json()['status']
print(f"Final Case Status: {case_status}")

assert case_status == "Verified", "Case should be VERIFIED"
assert case_status != "Reunified", "Case cannot be REUNITED in Phase 6"

print("--- PHASE 6 RUNTIME CHECKS PASSED ---")
