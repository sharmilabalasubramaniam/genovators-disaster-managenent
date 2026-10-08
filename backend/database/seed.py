import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from sqlalchemy.orm import Session
from backend.database.db import SessionLocal, engine, Base
from backend.models import models
import random
from datetime import datetime, timedelta
from faker import Faker

fake = Faker()

def seed_data():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    
    db = SessionLocal()
    
    statuses = ["New", "In Progress", "In Verification", "Verified", "Reunified"]
    organizations = ["Shelter A", "Hospital B", "Rescue Team 3", "Shelter C", "Hospital C"]
    
    for i in range(5):
        # Create Person
        person = models.Person(
            first_name=fake.first_name(),
            last_name=fake.last_name(),
            age=random.randint(5, 75),
            gender=random.choice(["Male", "Female"]),
            distinguishing_features="None"
        )
        db.add(person)
        db.flush()
        
        # Create Case
        vrn_id = f"VRN-{4000 + i}"
        status = random.choice(statuses)
        case = models.Case(
            vrn_id=vrn_id,
            person_id=person.id,
            status=status,
            created_at=datetime.utcnow() - timedelta(hours=random.randint(1, 48))
        )
        db.add(case)
        db.flush()
        
        # Create Family Report
        if random.choice([True, False]):
            fam_report = models.FamilyReport(
                case_id=case.id,
                reporter_name=fake.name(),
                reporter_contact=fake.phone_number(),
                relationship_to_person=random.choice(["Parent", "Sibling", "Spouse"])
            )
            db.add(fam_report)
            
        # Create Location Record
        loc_record = models.LocationRecord(
            case_id=case.id,
            location_type=random.choice(["Shelter", "Hospital", "Rescue"]),
            address=random.choice(organizations)
        )
        db.add(loc_record)
        
        # Create Verification
        ver = models.Verification(
            case_id=case.id,
            step="Timeline & Evidence Check",
            status=random.choice(["Pending", "Approved"])
        )
        db.add(ver)
        
    db.commit()
    print("Database seeded with 5 synthetic cases.")
    db.close()

if __name__ == "__main__":
    seed_data()
