import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from fastapi.testclient import TestClient
from backend.main import app

client = TestClient(app)

print("--- Phase 5: Runtime Verification ---")

# First verify we can get a family case VRN id.
res = client.get("/api/cases/")
assert res.status_code == 200
cases = res.json()

family_case = None
for c in cases:
    if c['family_reports']:
        family_case = c
        break

assert family_case, "No family case found to run matching on."
vrn_id = family_case['vrn_id']

print(f"Running AI Matching for Case: {vrn_id}")
match_res = client.post(f"/api/matching/cases/{vrn_id}")
print(f"Matching Request Status: {match_res.status_code}")
assert match_res.status_code == 200

match_data = match_res.json()
print(f"Matching Status: {match_data['status']}")
print(f"Total Candidates Found: {len(match_data['candidates'])}")

if len(match_data['candidates']) > 0:
    top = match_data['candidates'][0]
    print(f"Top Candidate: {top['record_id']} - Score: {top['score']:.2f} ({top['confidence']}) from {top['organization']}")

# Verify case status did NOT change to VERIFIED
case_res = client.get(f"/api/cases/{vrn_id}")
case_data = case_res.json()
print(f"Case status after matching: {case_data['status']}")
assert case_data['status'] != "Verified"

print("\n--- PHASE 5 RUNTIME CHECKS PASSED SUCCESSFULLY ---")
