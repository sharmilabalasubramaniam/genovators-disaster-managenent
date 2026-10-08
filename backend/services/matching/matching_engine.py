import json
from sqlalchemy.orm import Session
from backend.models import models
from .name_matcher import compare_names
from .attribute_matcher import compare_age, compare_gender, compare_physical
from .location_matcher import compare_location
from .time_matcher import compare_time
from .face_matcher import compare_faces
from .scoring import calculate_weighted_score, calculate_confidence

def _get_case_organization(case: models.Case) -> str:
    if case.hospital_records:
        return case.hospital_records[0].hospital_name
    elif case.shelter_records:
        return case.shelter_records[0].shelter_name
    elif case.rescue_records:
        return case.rescue_records[0].rescue_team
    return "Unknown Organization"

def run_matching_for_case(db: Session, family_case_id: int):
    # 1. Retrieve the family report case
    family_case = db.query(models.Case).filter(models.Case.id == family_case_id).first()
    if not family_case or not family_case.family_reports:
        return None
        
    family_person = family_case.person
    
    # Get family location/time if any
    family_location = None
    family_time = None
    if family_case.location_records:
        family_location = family_case.location_records[0].address
        family_time = family_case.location_records[0].recorded_at

    # 2. Retrieve all potential found persons
    # (Excluding family reports, picking only FOUND/SHELTER/HOSPITALIZED style or anything with org records)
    candidates = db.query(models.Case).filter(
        models.Case.id != family_case_id,
        models.Case.family_reports == None # simple filter for found persons
    ).all()
    
    results = []
    
    for candidate_case in candidates:
        cand_person = candidate_case.person
        
        cand_location = None
        cand_time = candidate_case.created_at # fallback
        if candidate_case.location_records:
            cand_location = candidate_case.location_records[0].address
            cand_time = candidate_case.location_records[0].recorded_at
            
        # 5. Compare the records
        signals = {
            "name": compare_names(f"{family_person.first_name} {family_person.last_name}", f"{cand_person.first_name} {cand_person.last_name}"),
            "age": compare_age(family_person.age, cand_person.age),
            "gender": compare_gender(family_person.gender, cand_person.gender),
            "location": compare_location(family_location, cand_location),
            "time": compare_time(family_time, cand_time),
            "physical": compare_physical(family_person.distinguishing_features, cand_person.distinguishing_features),
            "face": compare_faces(family_person.photo_url, cand_person.photo_url)
        }
        
        score = calculate_weighted_score(signals)
        confidence = calculate_confidence(score)
        
        # 8. Store match result
        match_result = models.MatchResult(
            case_id=family_case_id,
            candidate_case_id=candidate_case.id,
            score=score,
            confidence=confidence,
            signals=json.dumps(signals)
        )
        db.add(match_result)
        db.flush()
        
        results.append({
            "record_id": candidate_case.vrn_id,
            "organization": _get_case_organization(candidate_case),
            "score": score,
            "confidence": confidence
        })
        
    db.commit()
    
    # 6. Rank candidates
    results.sort(key=lambda x: x["score"], reverse=True)
    return results
