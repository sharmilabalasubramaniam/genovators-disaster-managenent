import os
import sys

# Add backend directory to sys path so we can import modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from backend.database.db import engine, Base
from backend.models import models
import seed

def reset_demo():
    print("WARNING: This is a DEVELOPMENT ONLY command.")
    print("Clearing database...")
    
    # Drop all tables
    Base.metadata.drop_all(bind=engine)
    
    print("Recreating tables...")
    # Recreate all tables
    Base.metadata.create_all(bind=engine)
    
    print("Seeding demo scenario...")
    # Run seed script
    seed.seed_data()
    print("Demo reset complete! System is ready for hackathon demonstration.")

if __name__ == "__main__":
    reset_demo()
