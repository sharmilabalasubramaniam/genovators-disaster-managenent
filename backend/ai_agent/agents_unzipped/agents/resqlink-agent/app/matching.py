"""Multi-factor matching with fuzzy comparison.

Scores are normalised over the factors that can actually be compared, so a record
with an unknown name is not unfairly penalised. Hard conflicts (e.g. different
gender) cap the score, and a record without a comparable name is capped at 90
because name-based confirmation is unavailable.
"""
import re
from difflib import SequenceMatcher

WEIGHTS = {"name": 30, "age": 20, "gender": 10, "location": 20, "description": 20}
NO_NAME_CAP = 90
CONFLICT_CAP = 49
MIN_EVIDENCE_WEIGHT = 40  # need at least this much comparable weight to score at all

_STOPWORDS = {"and", "with", "a", "the", "wearing", "in", "of"}
_SYNONYMS = {
    "tshirt": "shirt", "tee": "shirt", "tshirts": "shirt",
    "trousers": "pants", "jeans": "pants", "pant": "pants",
    "spectacles": "glasses", "specs": "glasses", "eyeglasses": "glasses",
}


def _tokens(text: str) -> list[str]:
    text = (text or "").lower().replace("t-shirt", "tshirt")
    out = []
    for w in re.findall(r"[a-z]+", text):
        w = _SYNONYMS.get(w, w)
        if w not in _STOPWORDS:
            out.append(w)
    return out


def text_similarity(a: str, b: str) -> float:
    ta, tb = _tokens(a), _tokens(b)
    if not ta or not tb:
        return 0.0
    sa, sb = set(ta), set(tb)
    jaccard = len(sa & sb) / len(sa | sb)
    seq = SequenceMatcher(None, " ".join(sorted(sa)), " ".join(sorted(sb))).ratio()
    return 0.6 * jaccard + 0.4 * seq


def is_unknown_name(name) -> bool:
    n = (name or "").strip().lower()
    return n == "" or n.startswith("unknown") or n.startswith("unidentified")


def _str_similarity(a: str, b: str) -> float:
    return SequenceMatcher(None, a.lower().strip(), b.lower().strip()).ratio()


def calculate_match(missing: dict, candidate: dict) -> dict:
    earned = 0.0
    available = 0
    reasons: list[str] = []
    conflicts: list[str] = []

    # Name
    name_comparable = not is_unknown_name(missing.get("name")) and not is_unknown_name(candidate.get("name"))
    if name_comparable:
        available += WEIGHTS["name"]
        sim = _str_similarity(missing["name"], candidate["name"])
        if sim >= 0.8:
            earned += WEIGHTS["name"] * sim
            reasons.append(f"Name similar ({sim:.0%})")
    else:
        reasons.append("Name not comparable (unidentified record)")

    # Age (tolerance: records made during a disaster are often estimates)
    if missing.get("age") is not None and candidate.get("age") is not None:
        available += WEIGHTS["age"]
        diff = abs(missing["age"] - candidate["age"])
        if diff == 0:
            earned += WEIGHTS["age"]
            reasons.append("Age matches")
        elif diff <= 2:
            earned += WEIGHTS["age"] * 0.6
            reasons.append(f"Age within {diff} year(s)")
        elif diff <= 5:
            earned += WEIGHTS["age"] * 0.25
            reasons.append(f"Age differs by {diff} years")
        elif diff > 10:
            conflicts.append(f"Age differs by {diff} years")

    # Gender
    if missing.get("gender") and candidate.get("gender"):
        available += WEIGHTS["gender"]
        if missing["gender"].lower() == candidate["gender"].lower():
            earned += WEIGHTS["gender"]
            reasons.append("Gender matches")
        else:
            conflicts.append("Gender mismatch")

    # Location
    if missing.get("last_location") and candidate.get("last_location"):
        available += WEIGHTS["location"]
        if _str_similarity(missing["last_location"], candidate["last_location"]) >= 0.85:
            earned += WEIGHTS["location"]
            reasons.append("Location matches")

    # Description (fuzzy)
    if missing.get("description") and candidate.get("description"):
        available += WEIGHTS["description"]
        sim = text_similarity(missing["description"], candidate["description"])
        if sim >= 0.4:
            earned += WEIGHTS["description"] * sim
            reasons.append(f"Description similar ({sim:.0%})")

    if available < MIN_EVIDENCE_WEIGHT:
        return {"score": 0, "reasons": reasons, "conflicts": conflicts, "insufficient_evidence": True}

    score = round(earned / available * 100)
    if not name_comparable:
        score = min(score, NO_NAME_CAP)
    if conflicts:
        score = min(score, CONFLICT_CAP)
    return {"score": score, "reasons": reasons, "conflicts": conflicts, "insufficient_evidence": False}
