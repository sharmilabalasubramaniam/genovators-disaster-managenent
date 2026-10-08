from fastapi.testclient import TestClient
from backend.main import app

client = TestClient(app)

def test_verification_flow():
    # 1. Create family case
    person_data = {
        "first_name": "John",
        "last_name": "Doe",
        "age": 30,
        "gender": "Male"
    }
    case_data = {
        "status": "New",
        "person": person_data,
        "family_report": {
            "reporter_name": "Jane Doe",
            "reporter_contact": "555-0100",
            "relationship_to_person": "Sister"
        }
    }
    res1 = client.post("/api/cases/", json=case_data)
    family_case = res1.json()
    vrn_id = family_case["vrn_id"]

    # 2. Create organization case
    org_case_data = {
        "status": "New",
        "person": person_data,
        "hospital_record": {
            "hospital_name": "City Hospital"
        }
    }
    res2 = client.post("/api/cases/", json=org_case_data)
    org_case = res2.json()
    candidate_vrn_id = org_case["vrn_id"]
    
    # 3. Start Verification
    start_res = client.post(f"/api/verification/{vrn_id}/start", json={"candidate_vrn_id": candidate_vrn_id})
    assert start_res.status_code == 200
    
    # 4. Get Verification
    get_res = client.get(f"/api/verification/{vrn_id}/candidate/{candidate_vrn_id}")
    assert get_res.status_code == 200
    assert get_res.json()["status"] == "IN_REVIEW"
    
    # 5. Add Evidence
    ev_data = {
        "candidate_vrn_id": candidate_vrn_id,
        "evidence_type": "ORGANIZATION",
        "description": "Hospital admits John Doe",
        "status": "SUPPORTED"
    }
    ev_res = client.post(f"/api/verification/{vrn_id}/evidence", json=ev_data)
    assert ev_res.status_code == 200
    
    # 6. Request More Evidence
    req_res = client.post(f"/api/verification/{vrn_id}/request-evidence", json={"notes": "Need ID"})
    assert req_res.status_code == 200
    assert req_res.json()["verification_status"] == "MORE_EVIDENCE_REQUIRED"
    
    # 7. Approve
    app_res = client.post(f"/api/verification/{vrn_id}/approve")
    assert app_res.status_code == 200
    assert app_res.json()["verification_status"] == "VERIFIED"
    
    # 8. Check Case Status
    final_case = client.get(f"/api/cases/{vrn_id}").json()
    assert final_case["status"] == "Verified"

def test_reject_verification():
    # 1. Create cases
    person_data = {"first_name": "Alice", "last_name": "Smith"}
    res1 = client.post("/api/cases/", json={"status": "New", "person": person_data, "family_report": {"reporter_name": "Bob", "reporter_contact": "555-0101", "relationship_to_person": "Brother"}})
    vrn_id = res1.json()["vrn_id"]
    
    res2 = client.post("/api/cases/", json={"status": "New", "person": person_data, "hospital_record": {"hospital_name": "Gen Hosp"}})
    candidate_vrn_id = res2.json()["vrn_id"]
    
    # 2. Start
    client.post(f"/api/verification/{vrn_id}/start", json={"candidate_vrn_id": candidate_vrn_id})
    
    # 3. Reject
    rej_res = client.post(f"/api/verification/{vrn_id}/reject", json={"reason": "Mismatch"})
    assert rej_res.status_code == 200
    assert rej_res.json()["verification_status"] == "REJECTED"
    
    # 4. Check Case Status is back to In Progress
    final_case = client.get(f"/api/cases/{vrn_id}").json()
    assert final_case["status"] == "In Progress"
