import hmac
import os
from contextlib import asynccontextmanager

from dotenv import load_dotenv
from fastapi import Depends, FastAPI, Header, HTTPException
from pydantic import BaseModel

from app import tools
from app.database import init_db

load_dotenv()


@asynccontextmanager
async def lifespan(_: FastAPI):
    init_db(seed=True)
    yield


app = FastAPI(
    title="ResQLink AI Agent",
    description="AI-assisted disaster family reunification. AI finds leads; humans verify.",
    version="2.0",
    lifespan=lifespan,
)


# ---------------------------------------------------------------- models
class AgentRequest(BaseModel):
    message: str


class AgentResponse(BaseModel):
    response: str


class VerificationRequest(BaseModel):
    missing_person_id: int
    candidate_id: int
    identity_verified: bool
    relationship_verified: bool
    verified_by: str  # officer name / badge id


class ReuniteRequest(BaseModel):
    missing_person_id: int
    candidate_id: int
    officer: str


# ------------------------------------------------------------------ auth
def require_authority(x_authority_key: str = Header(default="")):
    """Fail closed: if no key is configured, human-action endpoints are disabled."""
    expected = os.getenv("AUTHORITY_API_KEY", "")
    if not expected:
        raise HTTPException(503, "AUTHORITY_API_KEY is not configured; human-action endpoints are disabled")
    if not hmac.compare_digest(x_authority_key, expected):
        raise HTTPException(401, "Invalid authority key")


# ------------------------------------------------------------ public routes
@app.get("/")
def home():
    return {"message": "ResQLink AI Agent is running", "status": "online"}


@app.post("/agent/chat", response_model=AgentResponse)
def chat(request: AgentRequest):
    from app.agent import run_agent  # lazy import so the API starts without LLM credentials

    try:
        return {"response": run_agent(request.message)}
    except RuntimeError as e:
        raise HTTPException(503, str(e))


# Deterministic (no-LLM) endpoints: handy for the frontend and for demos if the LLM is down.
@app.get("/persons/{person_id}/matches")
def matches(person_id: int):
    result = tools.find_possible_matches(person_id)
    if isinstance(result, dict) and "error" in result:
        raise HTTPException(404, result["error"])
    return result


@app.get("/cases/{missing_person_id}/{candidate_id}/firewall")
def firewall(missing_person_id: int, candidate_id: int):
    result = tools.run_firewall_for_case(missing_person_id, candidate_id)
    if "error" in result:
        raise HTTPException(400, result["error"])
    return result


# ------------------------------------------------- human-only routes (authenticated)
@app.post("/cases/verify", dependencies=[Depends(require_authority)])
def verify(req: VerificationRequest):
    result = tools.record_human_verification(
        req.missing_person_id, req.candidate_id, req.identity_verified, req.relationship_verified, req.verified_by
    )
    if "error" in result:
        raise HTTPException(400, result["error"])
    return result


@app.post("/cases/reunite", dependencies=[Depends(require_authority)])
def reunite(req: ReuniteRequest):
    result = tools.mark_reunited(req.missing_person_id, req.candidate_id, req.officer)
    if "error" in result:
        raise HTTPException(409, result)
    return result
