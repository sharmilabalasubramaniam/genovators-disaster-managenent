from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.database.db import engine, Base
from backend.api import (
    cases, dashboard, locations, matching, 
    notifications, uploads, verification, 
    reunification, announcements, ocr, predictions
)

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Verified Reunification Network API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(cases.router)
app.include_router(dashboard.router)
app.include_router(locations.router)
app.include_router(matching.router)
app.include_router(notifications.router)
app.include_router(uploads.router)
app.include_router(verification.router)
app.include_router(reunification.router)
app.include_router(announcements.router)
app.include_router(ocr.router)
app.include_router(predictions.router)

from backend.identity_recovery.app.main import app as identity_recovery_app
app.mount("/api/identity_recovery", identity_recovery_app)

@app.get("/api/health")
def health_check():
    return {"status": "ok", "message": "Backend is running"}
