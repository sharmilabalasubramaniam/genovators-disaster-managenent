import requests
import json
import io
import time

BASE_URL = "http://127.0.0.1:8000/api"

print("Starting E2E API Verification...")

def test_endpoint():
    # 1. Test Dashboard
    print("\n--- Testing Dashboard ---")
    r = requests.get(f"{BASE_URL}/dashboard/stats")
    print(f"Stats status: {r.status_code}")
    if r.status_code == 200:
        print(r.json())

    from PIL import Image

    def create_mock_image(color="red"):
        img = Image.new('RGB', (100, 100), color=color)
        img_byte_arr = io.BytesIO()
        img.save(img_byte_arr, format='JPEG')
        img_byte_arr.seek(0)
        return img_byte_arr

    print("\n--- E2E Flow Simulation ---")
    print("1. Uploading photo for missing person...")
    img_file = create_mock_image('blue')
    r = requests.post(f"{BASE_URL}/uploads/", files={'file': ('missing.jpg', img_file, 'image/jpeg')})
    missing_photo_url = None
    if r.status_code == 200:
        missing_photo_url = r.json().get('url')
        print(f"Uploaded: {missing_photo_url}")
    else:
        print(f"Failed to upload photo: {r.text}")

    print("2. Creating Family Report...")
    report_data = {
        "status": "MISSING",
        "person": {
            "first_name": "Test",
            "last_name": "Missing",
            "age": 10,
            "gender": "M",
            "distinguishing_features": "Wearing blue shirt",
            "photo_url": missing_photo_url
        },
        "family_report": {
            "reporter_name": "Test Reporter",
            "reporter_contact": "555-0101",
            "relationship_to_person": "Parent"
        },
        "location": {
            "location_type": "LAST_SEEN",
            "address": "Central Park"
        }
    }
    r = requests.post(f"{BASE_URL}/cases/", json=report_data)
    missing_case_id = None
    if r.status_code == 200:
        missing_case = r.json()
        missing_case_id = missing_case['id']
        vrn_id = missing_case['vrn_id']
        print(f"Created Missing Case: {missing_case_id} ({vrn_id})")
    else:
        print(f"Failed: {r.status_code} {r.text}")

    print("3. Uploading photo for found person...")
    img_file2 = create_mock_image('blue')
    r = requests.post(f"{BASE_URL}/uploads/", files={'file': ('found.jpg', img_file2, 'image/jpeg')})
    found_photo_url = None
    if r.status_code == 200:
        found_photo_url = r.json().get('url')
        print(f"Uploaded: {found_photo_url}")

    print("4. Creating Hospital Record (Found Person)...")
    hospital_data = {
        "status": "HOSPITALIZED",
        "person": {
            "first_name": "Unknown",
            "last_name": "Boy",
            "age": 10,
            "gender": "M",
            "distinguishing_features": "Blue shirt",
            "photo_url": found_photo_url
        },
        "hospital_record": {
            "hospital_name": "City General",
            "condition_summary": "Stable"
        }
    }
    r = requests.post(f"{BASE_URL}/cases/", json=hospital_data)
    found_case_id = None
    if r.status_code == 200:
        found_case = r.json()
        found_case_id = found_case['id']
        found_vrn_id = found_case['vrn_id']
        print(f"Created Found Case (Hospital): {found_case_id} ({found_vrn_id})")
    else:
        print(f"Failed: {r.status_code} {r.text}")

    print("5. Running Matching Engine...")
    r = requests.post(f"{BASE_URL}/matching/{vrn_id}/run")
    if r.status_code == 200:
        matches = r.json()
        print(f"Matches found: {len(matches.get('candidates', []))}")
        print(json.dumps(matches, indent=2))
    else:
        print(f"Matching failed: {r.status_code} {r.text}")

test_endpoint()
