"""Evidence scoring, conflict detection and identity staging."""
from datetime import datetime
from itertools import combinations
from typing import Optional

TS_FORMAT = "%Y-%m-%d %H:%M"

# Weights sum to 100.
WEIGHTS = {
    "age": 20,
    "appearance": 15,
    "location": 15,
    "timeline": 15,
    "clothing": 10,
    "name": 10,
    "medical": 10,
    "gender": 5,
}

# Physical journey order of a found person. FAMILY reports are "last seen"
# claims, so they are not part of the movement chain.
SOURCE_ORDER = {"RESCUE": 1, "HOSPITAL": 2, "SHELTER": 3}

STOPWORDS = {"the", "a", "an", "of", "near", "area", "zone", "and", "at", "in", "with"}

# Anything below these thresholds stays at the lower stage.
PARTIAL_THRESHOLD = 40
PROBABLE_THRESHOLD = 65


def _tokens(text: Optional[str]) -> set:
    if not text:
        return set()
    cleaned = text.lower().replace(",", " ").replace("-", " ")
    return {t for t in cleaned.split() if t not in STOPWORDS}


def _parse_ts(value: Optional[str]) -> Optional[datetime]:
    if not value:
        return None
    try:
        return datetime.strptime(value, TS_FORMAT)
    except ValueError:
        return None


def _name_clues(record: dict) -> set:
    return _tokens(record.get("name")) | _tokens(record.get("partial_name"))


def _places(record: dict) -> set:
    return _tokens(record.get("location")) | _tokens(record.get("origin_location"))


def calculate_similarity(r1: dict, r2: dict) -> tuple[float, list[str]]:
    """Return (confidence 0-100, evidence list) for a pair of records.

    Only categories where BOTH records have data are evaluated. A coverage
    penalty is applied when too little can be compared, so two records that
    share one clue cannot score 100%.
    """
    earned = 0.0
    evaluable = 0.0
    evidence: list[str] = []

    # Age
    a1, a2 = r1.get("age"), r2.get("age")
    if a1 is not None and a2 is not None:
        evaluable += WEIGHTS["age"]
        diff = abs(a1 - a2)
        if diff <= 2:
            earned += WEIGHTS["age"]
            evidence.append(f"Age strongly matches ({a1} vs {a2})")
        elif diff <= 5:
            earned += WEIGHTS["age"] * 0.6
            evidence.append(f"Age approximately matches ({a1} vs {a2})")

    # Gender
    g1, g2 = r1.get("gender"), r2.get("gender")
    if g1 and g2:
        evaluable += WEIGHTS["gender"]
        if g1.lower() == g2.lower():
            earned += WEIGHTS["gender"]
            evidence.append("Gender matches")

    # Clothing
    c1, c2 = _tokens(r1.get("clothing")), _tokens(r2.get("clothing"))
    if c1 and c2:
        evaluable += WEIGHTS["clothing"]
        if c1 == c2:
            earned += WEIGHTS["clothing"]
            evidence.append("Clothing matches")
        elif c1 & c2:
            earned += WEIGHTS["clothing"] * 0.5
            evidence.append("Clothing partially matches")

    # Appearance (shared descriptive words)
    p1, p2 = _tokens(r1.get("physical_description")), _tokens(r2.get("physical_description"))
    if p1 and p2:
        evaluable += WEIGHTS["appearance"]
        common = p1 & p2
        if len(common) >= 2:
            earned += WEIGHTS["appearance"]
            evidence.append(f"Physical characteristics match ({', '.join(sorted(common))})")
        elif len(common) == 1:
            earned += WEIGHTS["appearance"] * 0.5
            evidence.append(f"Physical characteristics partially match ({', '.join(common)})")

    # Location continuity: shared place words across location / origin fields.
    # Different places are NOT penalised, because people legitimately move.
    l1, l2 = _places(r1), _places(r2)
    if l1 & l2:
        evaluable += WEIGHTS["location"]
        earned += WEIGHTS["location"]
        evidence.append(f"Location continuity ({', '.join(sorted(l1 & l2))})")

    # Timeline
    t1, t2 = _parse_ts(r1.get("timestamp")), _parse_ts(r2.get("timestamp"))
    if t1 and t2:
        evaluable += WEIGHTS["timeline"]
        hours = abs((t1 - t2).total_seconds()) / 3600
        if hours <= 6:
            earned += WEIGHTS["timeline"]
            evidence.append(f"Timeline is close ({hours:.1f} h apart)")
        elif hours <= 24:
            earned += WEIGHTS["timeline"] * 0.5
            evidence.append(f"Timeline is plausible ({hours:.1f} h apart)")

    # Name / partial name (symmetric)
    n1, n2 = _name_clues(r1), _name_clues(r2)
    if n1 and n2:
        evaluable += WEIGHTS["name"]
        common = n1 & n2
        if common:
            earned += WEIGHTS["name"]
            evidence.append(f"Name clue matches ({', '.join(sorted(common))})")

    # Medical (only meaningful if both mention a condition)
    m1, m2 = _tokens(r1.get("medical_condition")), _tokens(r2.get("medical_condition"))
    if m1 and m2:
        evaluable += WEIGHTS["medical"]
        if m1 & m2:
            earned += WEIGHTS["medical"]
            evidence.append("Medical information matches")

    if evaluable == 0:
        return 0.0, []

    raw = earned / evaluable * 100
    coverage = min(1.0, evaluable / 60)  # need >= 60 weight of comparable data
    return min(99.0, round(raw * coverage, 1)), evidence  # never 100%: only a human verifies


def determine_identity_stage(score: float, has_conflicts: bool = False) -> str:
    """Score never produces VERIFIED_PERSON; only a human officer can."""
    if score < PARTIAL_THRESHOLD:
        stage = "UNKNOWN"
    elif score < PROBABLE_THRESHOLD:
        stage = "PARTIALLY_IDENTIFIED"
    else:
        stage = "PROBABLE_IDENTITY"

    if has_conflicts and stage == "PROBABLE_IDENTITY":
        stage = "PARTIALLY_IDENTIFIED"
    return stage


def detect_conflicts(records: list[dict]) -> list[str]:
    conflicts: list[str] = []

    genders = {r["gender"].lower() for r in records if r.get("gender")}
    if len(genders) > 1:
        conflicts.append("Gender conflict detected")

    ages = [r["age"] for r in records if r.get("age") is not None]
    if ages and max(ages) - min(ages) > 10:
        conflicts.append(f"Large age difference detected ({min(ages)}-{max(ages)})")

    # Timeline: a later stage of the journey cannot be timestamped earlier.
    for a, b in combinations(records, 2):
        ra = SOURCE_ORDER.get(a["source_type"].upper())
        rb = SOURCE_ORDER.get(b["source_type"].upper())
        ta, tb = _parse_ts(a.get("timestamp")), _parse_ts(b.get("timestamp"))
        if not (ra and rb and ta and tb) or ra == rb:
            continue
        earlier, later = (a, b) if ra < rb else (b, a)
        t_earlier, t_later = (ta, tb) if ra < rb else (tb, ta)
        if t_earlier > t_later:
            conflicts.append(
                f"Timeline inconsistency: {earlier['source_type']} record "
                f"{earlier['record_id']} is timestamped after {later['source_type']} "
                f"record {later['record_id']}"
            )

    return conflicts


def possible_identity(records: list[dict]) -> Optional[str]:
    """Best name clue: prefer a full name, else the longest partial name."""
    full = [r["name"] for r in records if r.get("name")]
    if full:
        return max(full, key=len)
    partial = [r["partial_name"] for r in records if r.get("partial_name")]
    return max(partial, key=len) if partial else None
