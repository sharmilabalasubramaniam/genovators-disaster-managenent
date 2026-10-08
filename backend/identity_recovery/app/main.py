from fastapi import FastAPI, HTTPException

from .agent import (
    AgentError,
    build_evidence_graph,
    find_cluster,
    recover_identity,
    verify_identity,
)
from .database import clusters, records
from .models import IdentityClusterRequest, VerificationRequest

app = FastAPI(
    title="ResQLink Identity Recovery Agent",
    description="AI-assisted identity recovery for unknown disaster victims. "
    "The system only recommends; an authorized officer verifies.",
    version="1.1",
)


def _wrap(fn, *args):
    try:
        return fn(*args)
    except AgentError as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)


@app.get("/")
def home():
    return {"message": "ResQLink Identity Recovery Agent", "status": "online"}


@app.get("/records")
def get_records():
    return records


@app.post("/identity/recover")
def recover(request: IdentityClusterRequest):
    return _wrap(recover_identity, request.record_ids)


@app.get("/clusters")
def get_clusters():
    return clusters


@app.get("/clusters/{cluster_id}")
def get_cluster(cluster_id: str):
    cluster = find_cluster(cluster_id)
    if not cluster:
        raise HTTPException(status_code=404, detail="Cluster not found")
    return cluster


@app.get("/clusters/{cluster_id}/graph")
def get_graph(cluster_id: str):
    return _wrap(build_evidence_graph, cluster_id)


@app.post("/identity/verify")
def verify(request: VerificationRequest):
    return _wrap(
        verify_identity,
        request.cluster_id,
        request.verified_name,
        request.officer_name,
        request.notes,
    )
