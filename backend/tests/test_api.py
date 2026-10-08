import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from fastapi.testclient import TestClient
from backend.main import app

client = TestClient(app)

def test_health_check():
    response = client.get("/api/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok", "message": "Backend is running"}

def test_create_and_manage_case():
    # 1. Create a case
    payload = {
        "status": "New",
        "person": {
            "first_name": "Jane",
            "last_name": "Doe",
            "age": 30,
            "gender": "Female",
            "distinguishing_features": "Scare on left arm"
        }
    }
    response = client.post("/api/cases/", json=payload)
    assert response.status_code == 200, response.json()
    data = response.json()
    assert "id" in data
    assert "vrn_id" in data
    assert data["vrn_id"].startswith("VRN-")
    assert data["person"]["first_name"] == "Jane"
    assert data["status"] == "New"
    case_id = data["id"]
    vrn_id = data["vrn_id"]

    # 2. Get all cases
    response = client.get("/api/cases/")
    assert response.status_code == 200
    cases = response.json()
    assert len(cases) >= 1

    # 3. Get case by integer id
    response = client.get(f"/api/cases/{case_id}")
    assert response.status_code == 200
    fetched_by_id = response.json()
    assert fetched_by_id["vrn_id"] == vrn_id

    # 4. Get case by VRN ID string
    response = client.get(f"/api/cases/{vrn_id}")
    assert response.status_code == 200
    fetched_by_vrn = response.json()
    assert fetched_by_vrn["id"] == case_id

    # 5. Patch case status
    patch_payload = {"status": "In Progress"}
    response = client.patch(f"/api/cases/{vrn_id}", json=patch_payload)
    assert response.status_code == 200
    updated_case = response.json()
    assert updated_case["status"] == "In Progress"

def test_family_report_registration():
    payload = {
        "status": "New",
        "person": {
            "first_name": "John",
            "last_name": "Smith",
            "age": 45,
            "gender": "Male",
            "distinguishing_features": "Scars on face"
        },
        "family_report": {
            "reporter_name": "Alice Smith",
            "reporter_contact": "555-0199",
            "relationship_to_person": "Spouse"
        },
        "location": {
            "location_type": "Last Known",
            "address": "Downtown Central"
        }
    }
    
    response = client.post("/api/cases/", json=payload)
    assert response.status_code == 200, response.json()
    data = response.json()
    
    # 1. Case status is New
    assert data["status"] == "New"
    
    # 2. VRN ID is generated
    assert "vrn_id" in data
    assert data["vrn_id"].startswith("VRN-")
    
    # 3. Person record is created
    assert data["person"]["first_name"] == "John"
    
    # 4. FamilyReport record is created
    assert len(data["family_reports"]) == 1
    assert data["family_reports"][0]["reporter_name"] == "Alice Smith"
    
    # 5. Location record is created
    assert len(data["location_records"]) == 1
    assert data["location_records"][0]["address"] == "Downtown Central"

def test_invalid_family_report():
    # Invalid age (string instead of int)
    payload = {
        "status": "New",
        "person": {
            "first_name": "John",
            "last_name": "Smith",
            "age": "forty-five", # Invalid
            "gender": "Male"
        }
    }
    response = client.post("/api/cases/", json=payload)
    assert response.status_code == 422 # Validation Error
    
    # Missing required field (first_name)
    payload2 = {
        "status": "New",
        "person": {
            "last_name": "Smith",
            "age": 45
        }
    }
    response2 = client.post("/api/cases/", json=payload2)
    assert response2.status_code == 422 # Validation Error

def test_hospital_record_registration():
    payload = {
        "status": "HOSPITALIZED",
        "person": {
            "first_name": "Unknown",
            "last_name": "Unknown",
            "age": 30,
            "gender": "Male"
        },
        "hospital_record": {
            "hospital_name": "City General",
            "condition_summary": "Stable"
        },
        "location": {
            "location_type": "Found",
            "address": "Downtown"
        }
    }
    response = client.post("/api/cases/", json=payload)
    assert response.status_code == 200, response.json()
    data = response.json()
    assert data["status"] == "HOSPITALIZED"
    assert len(data["hospital_records"]) == 1
    assert data["hospital_records"][0]["hospital_name"] == "City General"

def test_shelter_record_registration():
    payload = {
        "status": "IN_SHELTER",
        "person": {
            "first_name": "Jane",
            "last_name": "Doe"
        },
        "shelter_record": {
            "shelter_name": "Relief Shelter A"
        }
    }
    response = client.post("/api/cases/", json=payload)
    assert response.status_code == 200, response.json()
    data = response.json()
    assert data["status"] == "IN_SHELTER"
    assert len(data["shelter_records"]) == 1

def test_rescue_record_registration():
    payload = {
        "status": "FOUND",
        "person": {
            "first_name": "John"
        },
        "rescue_record": {
            "rescue_team": "NDRF Alpha"
        }
    }
    response = client.post("/api/cases/", json=payload)
    assert response.status_code == 422 # Because last_name is required for person
