import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from sqlalchemy.orm import Session
from backend.database.db import SessionLocal, engine, Base
from backend.models import models
from backend.api.deps import get_password_hash
import random
from datetime import datetime, timedelta
from faker import Faker

fake = Faker()

# Geo coordinates around Indian disaster prone / relief areas (Chennai, Kerala, Delhi, Uttarakhand, Mumbai)
CITIES_GEO = [
    {"city": "Chennai", "lat": 13.0827, "lon": 80.2707},
    {"city": "Coimbatore", "lat": 11.0168, "lon": 76.9558},
    {"city": "Kochi", "lat": 9.9312, "lon": 76.2673},
    {"city": "Wayanad", "lat": 11.6854, "lon": 76.1320},
    {"city": "Delhi Relief Hub", "lat": 28.6139, "lon": 77.2090},
    {"city": "Dehradun", "lat": 30.3165, "lon": 78.0322},
    {"city": "Mumbai Central", "lat": 19.0760, "lon": 72.8777},
    {"city": "Kolkata Camp", "lat": 22.5726, "lon": 88.3639},
]

HOSPITALS = [
    "Apollo Emergency Care, Chennai",
    "Coimbatore Medical College Hospital",
    "General Hospital Kochi",
    "AIIMS Disaster Response Unit, Delhi",
    "KEM Hospital Trauma Care, Mumbai"
]

SHELTERS = [
    "Red Cross Relief Camp Alpha",
    "Community Hall Shelter #4, Wayanad",
    "St. Mary's Relief Center, Kochi",
    "Municipal High School Relief Camp, Dehradun",
    "Central Relief Pavilion, Chennai"
]

RESCUE_TEAMS = [
    "NDRF Battalion 04",
    "SDRF Rapid Response Team Bravo",
    "Coast Guard SAR Unit 2",
    "Civil Defense Volunteer Wing",
    "Indian Navy Disaster Assistance Group"
]

def seed_data():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    
    db = SessionLocal()
    
    # 1. Create Demo Users
    demo_users = [
        {"username": "admin@sahyat.demo", "role": "ADMIN", "name": "System Admin"},
        {"username": "officer@sahyat.demo", "role": "OFFICER", "name": "Officer Jane"},
        {"username": "family@sahyat.demo", "role": "FAMILY", "name": "Family Member"},
        {"username": "hospital@sahyat.demo", "role": "HOSPITAL", "name": "City Hospital"},
        {"username": "shelter@sahyat.demo", "role": "SHELTER", "name": "Relief Shelter"},
        {"username": "rescue@sahyat.demo", "role": "RESCUE", "name": "Rescue Squad Alpha"},
    ]
    
    for u in demo_users:
        user = models.User(
            username=u["username"],
            hashed_password=get_password_hash("password123"),
            role=u["role"],
            name=u["name"]
        )
        db.add(user)
    db.commit()

    # 2. Status distribution to create rich dashboard & portal data
    case_types = [
        # (Status, has_family, has_hospital, has_shelter, has_rescue)
        ("New", True, False, False, False),
        ("New", True, False, False, False),
        ("In Progress", True, False, True, False),
        ("In Progress", False, True, False, True),
        ("In Verification", True, True, False, False),
        ("In Verification", True, False, True, False),
        ("Verified", True, True, False, False),
        ("Verified", True, False, True, False),
        ("Reunification Ready", True, True, False, False),
        ("Reunification In Progress", True, False, True, True),
        ("Reunified", True, False, True, False),
        ("Reunified", True, True, False, False),
        ("New", False, False, False, True),
        ("In Progress", False, True, False, False),
        ("Verified", False, False, True, True),
    ]

    created_cases = []

    for i, (status, has_fam, has_hosp, has_shelt, has_resc) in enumerate(case_types):
        person = models.Person(
            first_name=fake.first_name(),
            last_name=fake.last_name(),
            age=random.randint(6, 78),
            gender=random.choice(["Male", "Female"]),
            distinguishing_features=random.choice([
                "Scar on left cheek", 
                "Wearing blue rain jacket", 
                "Silver ring on right hand", 
                "Tattoo on right forearm", 
                "Black glasses", 
                "None"
            ])
        )
        db.add(person)
        db.flush()

        vrn_id = f"VRN-{4000 + i}"
        created_time = datetime.now() - timedelta(hours=random.randint(2, 72))
        case = models.Case(
            vrn_id=vrn_id,
            person_id=person.id,
            status=status,
            created_at=created_time,
            updated_at=created_time + timedelta(hours=random.randint(1, 10))
        )
        db.add(case)
        db.flush()
        created_cases.append(case)

        # Family report
        if has_fam:
            fam_report = models.FamilyReport(
                case_id=case.id,
                reporter_name=fake.name(),
                reporter_contact=fake.phone_number(),
                relationship_to_person=random.choice(["Parent", "Sibling", "Spouse", "Child"]),
                reported_at=created_time
            )
            db.add(fam_report)

        # Hospital record
        if has_hosp:
            hosp_record = models.HospitalRecord(
                case_id=case.id,
                hospital_name=random.choice(HOSPITALS),
                admission_date=created_time + timedelta(hours=2),
                condition_summary=random.choice([
                    "Mild dehydration, stable",
                    "Minor abrasions, receiving medical observation",
                    "Recovering from hypothermia",
                    "Conscious, awaiting guardian identification"
                ])
            )
            db.add(hosp_record)

        # Shelter record
        if has_shelt:
            shelt_record = models.ShelterRecord(
                case_id=case.id,
                shelter_name=random.choice(SHELTERS),
                check_in_date=created_time + timedelta(hours=4)
            )
            db.add(shelt_record)

        # Rescue record
        if has_resc:
            resc_record = models.RescueRecord(
                case_id=case.id,
                rescue_team=random.choice(RESCUE_TEAMS),
                rescue_date=created_time + timedelta(hours=1),
                rescue_location=random.choice(CITIES_GEO)["city"]
            )
            db.add(resc_record)

        # Location Records (provide lat/lon for the MapView)
        loc_city = random.choice(CITIES_GEO)
        loc_type = "Last Known" if has_fam else ("Hospital" if has_hosp else ("Shelter" if has_shelt else "Rescue"))
        loc_record = models.LocationRecord(
            case_id=case.id,
            location_type=loc_type,
            address=f"{loc_city['city']} Relief Sector {random.randint(1, 12)}",
            recorded_at=created_time
        )
        db.add(loc_record)

        # Verifications
        if status in ["In Verification", "Verified", "Reunification Ready", "Reunified"]:
            ver = models.Verification(
                case_id=case.id,
                step="Timeline & Evidence Check",
                status="Approved" if status != "In Verification" else "Pending",
                notes="Biometric features and family contact verified with rescue log.",
                verified_by="Officer Jane",
                verified_at=created_time + timedelta(hours=5)
            )
            db.add(ver)

        # Audit logs
        audit = models.AuditLog(
            case_id=case.id,
            action=f"Case initialized with status {status}",
            performed_by="Officer Jane",
            timestamp=created_time
        )
        db.add(audit)

    db.commit()

    # 3. Create realistic MatchResults for identity matching and verification
    if len(created_cases) >= 4:
        match1 = models.MatchResult(
            case_id=created_cases[0].id,
            candidate_case_id=created_cases[2].id,
            score=0.91,
            confidence="High",
            signals="Face Match 94%, Location Match 88%, Description Match 91%",
            created_at=datetime.now() - timedelta(hours=6)
        )
        match2 = models.MatchResult(
            case_id=created_cases[1].id,
            candidate_case_id=created_cases[3].id,
            score=0.84,
            confidence="Medium",
            signals="Location Proximity 90%, Age & Gender Match, Distinctive Marks 78%",
            created_at=datetime.now() - timedelta(hours=4)
        )
        match3 = models.MatchResult(
            case_id=created_cases[4].id,
            candidate_case_id=created_cases[5].id,
            score=0.96,
            confidence="High",
            signals="Exact Face Feature Alignment, Clothing Match confirmed by Hospital",
            created_at=datetime.now() - timedelta(hours=2)
        )
        db.add_all([match1, match2, match3])

    # 4. Create Notifications
    notifications_data = [
        {
            "title": "High Confidence Match Detected",
            "message": "AI Matching Engine found a 96% match between VRN-4004 and VRN-4005.",
            "priority": "HIGH",
            "notification_type": "MATCH",
            "status": "UNREAD",
            "is_read": False,
            "case_id": created_cases[4].id if created_cases else None
        },
        {
            "title": "New Hospital Admission",
            "message": "City Hospital registered an unaccompanied minor under VRN-4003.",
            "priority": "HIGH",
            "notification_type": "HOSPITAL",
            "status": "UNREAD",
            "is_read": False,
            "case_id": created_cases[3].id if len(created_cases) > 3 else None
        },
        {
            "title": "Reunification Ready",
            "message": "Case VRN-4008 is verified and marked ready for family handoff.",
            "priority": "MEDIUM",
            "notification_type": "REUNIFICATION",
            "status": "UNREAD",
            "is_read": False,
            "case_id": created_cases[8].id if len(created_cases) > 8 else None
        },
        {
            "title": "Rescue Operation Update",
            "message": "NDRF Battalion 04 safely evacuated 14 individuals to Shelter Alpha.",
            "priority": "LOW",
            "notification_type": "RESCUE",
            "status": "READ",
            "is_read": True,
            "case_id": None
        }
    ]

    for n in notifications_data:
        notif = models.Notification(
            title=n["title"],
            message=n["message"],
            priority=n["priority"],
            notification_type=n["notification_type"],
            recipient_role="OFFICER",
            status=n["status"],
            is_read=n["is_read"],
            case_id=n["case_id"],
            created_at=datetime.now() - timedelta(minutes=random.randint(10, 180))
        )
        db.add(notif)

    db.commit()
    print(f"Database successfully re-seeded with {len(created_cases)} cases, organizations, matches, and notifications.")
    db.close()

if __name__ == "__main__":
    seed_data()
