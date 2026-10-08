import re
from sqlalchemy.orm import Session
from backend.models.models import User, Case, UserRole, FamilyReport, Person

def process_message(message: str, case_vrn: str, db: Session, current_user: User) -> dict:
    msg = message.lower()
    
    # 1. Project Knowledge
    if "what is sahyat" in msg or "what problem does sahyat solve" in msg:
        return {
            "answer": "Sahyat is an AI-powered disaster reunification platform. It helps unify fragmented records during a disaster, matching missing persons using AI and human verification.",
            "category": "PROJECT",
            "sources": ["README.md", "PROJECT_STATUS.md"],
            "data_used": False
        }
    
    if "disaster predictions" in msg or "disaster models" in msg:
        return {
            "answer": "Sahyat supports predicting Cyclone, Earthquake, Flood, and Landslide using dedicated ML models.",
            "category": "DISASTER ML",
            "sources": ["ml_models/"],
            "data_used": False
        }

    if "face matching" in msg or "face recognition" in msg:
        return {
            "answer": "Sahyat uses a real DeepFace implementation to match candidates based on facial similarity.",
            "category": "AI",
            "sources": ["matching service"],
            "data_used": False
        }

    if "verification work" in msg:
        return {
            "answer": "AI recommends potential matches, but human verification by an authorized officer is required to confirm identity based on evidence.",
            "category": "WORKFLOW",
            "sources": ["verification service"],
            "data_used": False
        }

    if "reunification work" in msg:
        return {
            "answer": "After verification, an authorized officer approves reunification. AI does not automatically reunite people.",
            "category": "WORKFLOW",
            "sources": ["reunification service"],
            "data_used": False
        }

    if "map work" in msg:
        return {
            "answer": "The map displays OpenStreetMap with markers for recorded disaster locations, shelters, and hospitals.",
            "category": "SYSTEM",
            "sources": ["map service"],
            "data_used": False
        }

    if "how do i report a missing person" in msg:
        return {
            "answer": "You can report a missing person through the Family dashboard by creating a new missing person report.",
            "category": "WORKFLOW",
            "sources": [],
            "data_used": False
        }
        
    # 2. Database Queries
    if "how many active cases" in msg or "how many cases" in msg:
        if current_user.role not in [UserRole.ADMIN.value, UserRole.OFFICER.value]:
            return {
                "answer": "You do not have permission to view all active cases.",
                "category": "SECURITY",
                "sources": [],
                "data_used": False
            }
        count = db.query(Case).count()
        return {
            "answer": f"There are currently {count} active cases in the system.",
            "category": "DATA",
            "sources": ["cases table"],
            "data_used": True
        }

    if "list out the missing persons" in msg or "list missing persons" in msg or "who is missing" in msg:
        if current_user.role not in [UserRole.ADMIN.value, UserRole.OFFICER.value]:
            return {
                "answer": "You do not have permission to view the full list of missing persons. Please use your dashboard.",
                "category": "SECURITY",
                "sources": [],
                "data_used": False
            }
        
        # Get cases that might indicate missing persons (e.g. New or In Progress)
        cases = db.query(Case).join(Person).limit(10).all()
        if not cases:
            return {
                "answer": "There are no active missing person cases recorded.",
                "category": "DATA",
                "sources": ["cases table"],
                "data_used": True
            }
        
        person_names = [f"- {c.vrn_id}: {c.person.first_name} {c.person.last_name}" for c in cases]
        list_str = "\n".join(person_names)
        
        return {
            "answer": f"Here are some of the active missing persons cases:\n\n{list_str}\n\n(Showing up to 10 recent cases)",
            "category": "DATA",
            "sources": ["cases table", "persons table"],
            "data_used": True
        }

    if "show my cases" in msg:
        if current_user.role == UserRole.FAMILY.value:
            # For hackathon demo, we find cases reported by this user's name
            reports = db.query(FamilyReport).filter(FamilyReport.reporter_name == current_user.name).all()
            case_ids = [r.case_id for r in reports]
            cases = db.query(Case).filter(Case.id.in_(case_ids)).all()
            return {
                "answer": f"You have {len(cases)} cases reported.",
                "category": "DATA",
                "sources": ["cases table", "family_reports table"],
                "data_used": True
            }
        else:
            return {
                "answer": "You can view cases in your dashboard.",
                "category": "SYSTEM",
                "sources": [],
                "data_used": False
            }
            
    # Refusals
    if "password" in msg or "token" in msg or "secret" in msg:
        return {
            "answer": "I cannot provide sensitive authentication data or secrets.",
            "category": "SECURITY",
            "sources": [],
            "data_used": False
        }
        
    if "show another family" in msg:
        return {
            "answer": "You do not have permission to view another family's information.",
            "category": "SECURITY",
            "sources": [],
            "data_used": False
        }
        
    # Contextual VRN queries
    if case_vrn:
        case = db.query(Case).filter(Case.vrn_id == case_vrn).first()
        if not case:
            return {
                "answer": "I could not find that case.",
                "category": "DATA",
                "sources": [],
                "data_used": False
            }
            
        # IDOR check
        if current_user.role == UserRole.FAMILY.value:
            reports = db.query(FamilyReport).filter(FamilyReport.case_id == case.id, FamilyReport.reporter_name == current_user.name).first()
            if not reports:
                return {
                    "answer": "You do not have permission to view this case.",
                    "category": "SECURITY",
                    "sources": [],
                    "data_used": False
                }
                
        if "status" in msg:
            return {
                "answer": f"The current status of {case_vrn} is {case.status}.",
                "category": "DATA",
                "sources": ["cases table"],
                "data_used": True
            }

    # Default fallback
    return {
        "answer": "I don't have enough verified information in Sahyat to answer that. I can help with Sahyat's disaster response, reunification workflow, matching, verification, maps, notifications, and disaster prediction modules.",
        "category": "UNKNOWN",
        "sources": [],
        "data_used": False
    }
