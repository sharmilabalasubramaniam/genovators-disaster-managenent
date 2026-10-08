"""Plain-Python tools. These are wrapped for the LLM in agent.py.

Security model
--------------
* The LLM can READ records, compute matches and run the firewall.
* The LLM can NOT set identity_verified / relationship_verified, mark a case
  REUNITED, or notify anyone. Those actions live in `human_actions` below and are
  only reachable through the authenticated HTTP endpoints in main.py.
"""
from datetime import datetime

from app.database import audit, get_db, now_iso
from app.matching import calculate_match

MATCH_THRESHOLD = 50       # minimum score to list a candidate
FIREWALL_MIN_SCORE = 70    # minimum score to proceed past the firewall
CANDIDATE_STATUSES = ("RESCUED", "FOUND")


def _row(r):
    return dict(r) if r is not None else None


def _normalize_name_query(name: str | None) -> str:
    return ("" if name is None else str(name).strip())


def _get_person(db, person_id: int):
    return _row(db.execute("SELECT * FROM persons WHERE id = ?", (person_id,)).fetchone())


# ------------------------------------------------------------------ search tools
def search_person_records(name: str | None) -> list[dict]:
    query = _normalize_name_query(name)
    with get_db() as db:
        rows = db.execute(
            "SELECT * FROM persons WHERE name LIKE ? ORDER BY id", (f"%{query}%",)
        ).fetchall()
    return [dict(r) for r in rows]


def search_rescue_records(name: str | None = "") -> list[dict]:
    """Rescued/found people, optionally filtered by name."""
    query = _normalize_name_query(name)
    with get_db() as db:
        rows = db.execute(
            "SELECT * FROM persons WHERE status IN ('RESCUED','FOUND') AND name LIKE ? ORDER BY id",
            (f"%{query}%",),
        ).fetchall()
    return [dict(r) for r in rows]


def search_hospital_records_by_person_id(person_id: int) -> list[dict]:
    with get_db() as db:
        rows = db.execute("SELECT * FROM hospital_records WHERE person_id = ?", (person_id,)).fetchall()
    return [dict(r) for r in rows]


def search_shelter_records_by_person_id(person_id: int) -> list[dict]:
    with get_db() as db:
        rows = db.execute("SELECT * FROM shelter_records WHERE person_id = ?", (person_id,)).fetchall()
    return [dict(r) for r in rows]


def search_hospital_records_by_name(name: str | None) -> list[dict]:
    query = _normalize_name_query(name)
    with get_db() as db:
        rows = db.execute("SELECT * FROM hospital_records WHERE name LIKE ?", (f"%{query}%",)).fetchall()
    return [dict(r) for r in rows]


def search_shelter_records_by_name(name: str | None) -> list[dict]:
    query = _normalize_name_query(name)
    with get_db() as db:
        rows = db.execute("SELECT * FROM shelter_records WHERE name LIKE ?", (f"%{query}%",)).fetchall()
    return [dict(r) for r in rows]


def get_case_records(person_id: int) -> dict:
    """Cross-record correlation: everything we know about one record ID."""
    with get_db() as db:
        person = _get_person(db, person_id)
    if not person:
        return {"error": f"No person record with id {person_id}"}
    return {
        "person": person,
        "hospital_records": search_hospital_records_by_person_id(person_id),
        "shelter_records": search_shelter_records_by_person_id(person_id),
    }


# --------------------------------------------------------------------- matching
def find_possible_matches(missing_person_id: int) -> list[dict] | dict:
    with get_db() as db:
        missing = _get_person(db, missing_person_id)
        if not missing:
            return {"error": "Missing person not found"}
        if missing["status"] != "MISSING":
            return {"error": f"Record {missing_person_id} has status {missing['status']}, not MISSING"}
        rows = db.execute(
            "SELECT * FROM persons WHERE id != ? AND status IN ('RESCUED','FOUND')", (missing_person_id,)
        ).fetchall()

    candidates = []
    for row in rows:
        cand = dict(row)
        result = calculate_match(missing, cand)
        if result["score"] >= MATCH_THRESHOLD:
            candidates.append(
                {
                    "candidate_id": cand["id"],
                    "candidate": cand,
                    "match_score": result["score"],
                    "reasons": result["reasons"],
                    "conflicts": result["conflicts"],
                    "hospital_records": search_hospital_records_by_person_id(cand["id"]),
                    "shelter_records": search_shelter_records_by_person_id(cand["id"]),
                }
            )
    candidates.sort(key=lambda c: c["match_score"], reverse=True)
    audit("system", "find_possible_matches", f"missing={missing_person_id} results={len(candidates)}")
    return candidates


# --------------------------------------------------------------------- firewall
def reunification_firewall(
    match_score: int,
    identity_verified: bool,
    relationship_verified: bool,
    timeline_consistent: bool,
    conflicts: list[str] | None = None,
) -> dict:
    """Pure decision function. Inputs must come from trusted sources, never the LLM."""
    if conflicts:
        return {"decision": "BLOCKED", "reason": "Conflicting evidence: " + "; ".join(conflicts)}
    if match_score < FIREWALL_MIN_SCORE:
        return {"decision": "BLOCKED", "reason": "Match score is too low"}
    if not timeline_consistent:
        return {"decision": "REVIEW", "reason": "Timeline inconsistency detected"}
    if not identity_verified:
        return {"decision": "REVIEW", "reason": "Identity verification by an authorized officer is required"}
    if not relationship_verified:
        return {"decision": "REVIEW", "reason": "Family relationship verification by an authorized officer is required"}
    return {"decision": "SAFE_TO_VERIFY", "reason": "All checks passed; final release still needs an authorized human"}


def _parse(ts):
    try:
        return datetime.fromisoformat(ts) if ts else None
    except ValueError:
        return None


def check_timeline(missing: dict, candidate: dict, hospitals: list[dict], shelters: list[dict]) -> dict:
    """Events on the candidate's side must not predate the missing person's last-seen time,
    and hospital/shelter events must not predate the rescue itself."""
    issues = []
    last_seen = _parse(missing.get("last_seen"))
    rescued = _parse(candidate.get("last_seen"))
    if last_seen and rescued and rescued < last_seen:
        issues.append("Candidate was recorded before the missing person was last seen")
    for h in hospitals:
        t = _parse(h.get("admitted_at"))
        if t and rescued and t < rescued:
            issues.append("Hospital admission predates the rescue record")
    for s in shelters:
        t = _parse(s.get("arrival_time"))
        if t and rescued and t < rescued:
            issues.append("Shelter arrival predates the rescue record")
    return {"consistent": not issues, "issues": issues}


def get_case_verification(missing_person_id: int, candidate_id: int) -> dict:
    with get_db() as db:
        row = db.execute(
            "SELECT * FROM cases WHERE missing_person_id = ? AND candidate_id = ?",
            (missing_person_id, candidate_id),
        ).fetchone()
    if row is None:
        return {"identity_verified": False, "relationship_verified": False, "verified_by": None, "status": "NO_CASE"}
    return {
        "identity_verified": bool(row["identity_verified"]),
        "relationship_verified": bool(row["relationship_verified"]),
        "verified_by": row["verified_by"],
        "status": row["status"],
    }


def run_firewall_for_case(missing_person_id: int, candidate_id: int) -> dict:
    """Everything is looked up server-side: score from the DB, flags from the case record."""
    with get_db() as db:
        missing = _get_person(db, missing_person_id)
        candidate = _get_person(db, candidate_id)
    if not missing or not candidate:
        return {"error": "Unknown person id"}
    if missing["status"] not in ("MISSING", "REUNITED") or candidate["status"] not in ("RESCUED", "FOUND", "REUNITED"):
        return {"error": "Pair is not a MISSING person and a RESCUED/FOUND candidate"}

    match = calculate_match(missing, candidate)
    hospitals = search_hospital_records_by_person_id(candidate_id)
    shelters = search_shelter_records_by_person_id(candidate_id)
    timeline = check_timeline(missing, candidate, hospitals, shelters)
    ver = get_case_verification(missing_person_id, candidate_id)

    decision = reunification_firewall(
        match["score"],
        ver["identity_verified"],
        ver["relationship_verified"],
        timeline["consistent"],
        match["conflicts"],
    )
    audit("system", "firewall_check", f"missing={missing_person_id} candidate={candidate_id} -> {decision['decision']}")
    return {
        "missing_person_id": missing_person_id,
        "candidate_id": candidate_id,
        "match_score": match["score"],
        "match_reasons": match["reasons"],
        "conflicts": match["conflicts"],
        "timeline": timeline,
        "verification": ver,
        **decision,
    }


# ------------------------------------------------- human-only actions (NOT agent tools)
def record_human_verification(
    missing_person_id: int,
    candidate_id: int,
    identity_verified: bool,
    relationship_verified: bool,
    verified_by: str,
) -> dict:
    with get_db() as db:
        if not _get_person(db, missing_person_id) or not _get_person(db, candidate_id):
            return {"error": "Unknown person id"}
        db.execute(
            """INSERT INTO cases (missing_person_id, candidate_id, identity_verified,
                                  relationship_verified, verified_by, verified_at)
               VALUES (?,?,?,?,?,?)
               ON CONFLICT(missing_person_id, candidate_id) DO UPDATE SET
                 identity_verified = excluded.identity_verified,
                 relationship_verified = excluded.relationship_verified,
                 verified_by = excluded.verified_by,
                 verified_at = excluded.verified_at""",
            (missing_person_id, candidate_id, int(identity_verified), int(relationship_verified), verified_by, now_iso()),
        )
    audit(
        verified_by,
        "human_verification",
        f"missing={missing_person_id} candidate={candidate_id} identity={identity_verified} relationship={relationship_verified}",
    )
    return get_case_verification(missing_person_id, candidate_id)


def mark_reunited(missing_person_id: int, candidate_id: int, officer: str) -> dict:
    check = run_firewall_for_case(missing_person_id, candidate_id)
    if "error" in check:
        return check
    if check["decision"] != "SAFE_TO_VERIFY":
        return {"error": "Firewall has not cleared this case", "firewall": check}
    with get_db() as db:
        db.execute(
            "UPDATE cases SET status = 'REUNITED' WHERE missing_person_id = ? AND candidate_id = ?",
            (missing_person_id, candidate_id),
        )
        db.execute("UPDATE persons SET status = 'REUNITED' WHERE id IN (?, ?)", (missing_person_id, candidate_id))
    audit(officer, "reunited", f"missing={missing_person_id} candidate={candidate_id}")
    return {"status": "REUNITED", "missing_person_id": missing_person_id, "candidate_id": candidate_id}
