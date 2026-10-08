"""Identity Recovery Agent: cluster, score, detect conflicts, verify."""
import uuid
from datetime import datetime, timezone
from itertools import combinations
from typing import Optional

from .database import clusters, records
from .matching import (
    calculate_similarity,
    detect_conflicts,
    determine_identity_stage,
    possible_identity,
)


class AgentError(Exception):
    def __init__(self, message: str, status_code: int = 400):
        super().__init__(message)
        self.message = message
        self.status_code = status_code


def find_record(record_id: str) -> Optional[dict]:
    return next((r for r in records if r["record_id"] == record_id), None)


def find_cluster(cluster_id: str) -> Optional[dict]:
    return next((c for c in clusters if c["cluster_id"] == cluster_id), None)


def create_identity_cluster(record_ids: list[str]) -> dict:
    unique_ids = list(dict.fromkeys(record_ids))  # drop duplicates, keep order

    missing = [rid for rid in unique_ids if not find_record(rid)]
    if missing:
        raise AgentError(f"Record(s) not found: {', '.join(missing)}", 404)
    if len(unique_ids) < 2:
        raise AgentError("At least two distinct records are required")

    # Return the existing cluster instead of creating a duplicate.
    for c in clusters:
        if set(c["record_ids"]) == set(unique_ids):
            return c

    selected = [find_record(rid) for rid in unique_ids]

    # Compare every pair, not just "first record vs the rest".
    pair_scores = []
    evidence_by_pair = []
    for a, b in combinations(selected, 2):
        score, evidence = calculate_similarity(a, b)
        pair_scores.append(score)
        evidence_by_pair.append(
            {
                "records": [a["record_id"], b["record_id"]],
                "score": score,
                "evidence": evidence,
            }
        )

    confidence = round(sum(pair_scores) / len(pair_scores), 1)
    conflicts = detect_conflicts(selected)
    stage = determine_identity_stage(confidence, has_conflicts=bool(conflicts))

    cluster = {
        "cluster_id": "UP-" + uuid.uuid4().hex[:8].upper(),
        "record_ids": unique_ids,
        "confidence": confidence,
        "identity_stage": stage,
        "possible_identity": possible_identity(selected),
        "evidence": sorted({e for p in evidence_by_pair for e in p["evidence"]}),
        "pair_evidence": evidence_by_pair,
        "conflicts": conflicts,
        "status": "REVIEW_REQUIRED" if conflicts else "ACTIVE",
        "created_at": datetime.now(timezone.utc).isoformat(),
    }
    clusters.append(cluster)
    return cluster


def recover_identity(record_ids: list[str]) -> dict:
    return create_identity_cluster(record_ids)


def build_evidence_graph(cluster_id: str) -> dict:
    cluster = find_cluster(cluster_id)
    if not cluster:
        raise AgentError("Cluster not found", 404)

    nodes = [{"id": cluster["cluster_id"], "type": "cluster"}]
    edges = []
    for rid in cluster["record_ids"]:
        r = find_record(rid)
        nodes.append(
            {
                "id": rid,
                "type": r["source_type"],
                "timestamp": r.get("timestamp"),
                "location": r.get("location"),
            }
        )
        edges.append({"from": rid, "to": cluster["cluster_id"], "relation": "belongs_to"})

    for pair in cluster["pair_evidence"]:
        edges.append(
            {
                "from": pair["records"][0],
                "to": pair["records"][1],
                "relation": "similar",
                "score": pair["score"],
                "evidence": pair["evidence"],
            }
        )

    if cluster.get("possible_identity"):
        nodes.append({"id": cluster["possible_identity"], "type": "possible_identity"})
        edges.append(
            {
                "from": cluster["cluster_id"],
                "to": cluster["possible_identity"],
                "relation": "possible_identity",
                "verified": cluster["identity_stage"] == "VERIFIED_PERSON",
            }
        )

    return {"cluster_id": cluster_id, "nodes": nodes, "edges": edges}


def verify_identity(
    cluster_id: str,
    verified_name: str,
    officer_name: str,
    notes: Optional[str] = None,
) -> dict:
    cluster = find_cluster(cluster_id)
    if not cluster:
        raise AgentError("Cluster not found", 404)
    if cluster["identity_stage"] == "VERIFIED_PERSON":
        raise AgentError("Cluster is already verified", 409)

    cluster["identity_stage"] = "VERIFIED_PERSON"
    cluster["verified_identity"] = verified_name
    cluster["verified_by"] = officer_name
    cluster["verification_notes"] = notes
    cluster["verified_at"] = datetime.now(timezone.utc).isoformat()
    cluster["status"] = "VERIFIED"
    return cluster
