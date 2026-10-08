"""SQLite storage for ResQLink. Uses only the standard library.

The database path is read on every connection so tests can point to a temp file.
"""
import os
import sqlite3
from contextlib import contextmanager
from datetime import datetime, timezone

SCHEMA = """
CREATE TABLE IF NOT EXISTS persons (
    id            INTEGER PRIMARY KEY,
    name          TEXT NOT NULL,
    age           INTEGER,
    gender        TEXT,
    status        TEXT NOT NULL CHECK (status IN ('MISSING','RESCUED','FOUND','REUNITED')),
    last_location TEXT,
    last_seen     TEXT,            -- ISO 8601 timestamp
    description   TEXT
);

CREATE TABLE IF NOT EXISTS hospital_records (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    person_id   INTEGER NOT NULL REFERENCES persons(id),
    name        TEXT,
    age         INTEGER,
    hospital    TEXT,
    admitted_at TEXT,
    location    TEXT
);

CREATE TABLE IF NOT EXISTS shelter_records (
    id           INTEGER PRIMARY KEY AUTOINCREMENT,
    person_id    INTEGER NOT NULL REFERENCES persons(id),
    name         TEXT,
    age          INTEGER,
    shelter      TEXT,
    arrival_time TEXT,
    location     TEXT
);

-- One case per (missing person, candidate record) pair.
-- identity_verified / relationship_verified can ONLY be set by an authorized human
-- through the authenticated API. The AI agent has no tool that writes them.
CREATE TABLE IF NOT EXISTS cases (
    id                    INTEGER PRIMARY KEY AUTOINCREMENT,
    missing_person_id     INTEGER NOT NULL REFERENCES persons(id),
    candidate_id          INTEGER NOT NULL REFERENCES persons(id),
    identity_verified     INTEGER NOT NULL DEFAULT 0,
    relationship_verified INTEGER NOT NULL DEFAULT 0,
    verified_by           TEXT,
    verified_at           TEXT,
    status                TEXT NOT NULL DEFAULT 'OPEN',
    UNIQUE (missing_person_id, candidate_id)
);

CREATE TABLE IF NOT EXISTS audit_log (
    id     INTEGER PRIMARY KEY AUTOINCREMENT,
    ts     TEXT NOT NULL,
    actor  TEXT NOT NULL,
    action TEXT NOT NULL,
    detail TEXT
);
"""

D = "2026-10-08"  # demo date

SEED_PERSONS = [
    (1, "Arun Kumar", 24, "Male", "MISSING", "Zone A", f"{D}T10:00:00", "Blue shirt and black pants"),
    (2, "Unknown Male", 24, "Male", "RESCUED", "Zone A", f"{D}T10:40:00", "Blue t-shirt and black trousers"),
    (3, "Unknown Male", 61, "Male", "RESCUED", "Zone C", f"{D}T12:10:00", "Grey kurta, white beard"),
    (4, "Meena Devi", 62, "Female", "MISSING", "Zone C", f"{D}T09:30:00", "Green saree and spectacles"),
    (5, "Unknown Female", 60, "Female", "FOUND", "Zone C", f"{D}T13:05:00", "Green saree, wearing spectacles"),
]
SEED_HOSPITAL = [
    (2, "Unknown Male", 24, "City Government Hospital", f"{D}T11:20:00", "Zone A"),
    (5, "Unknown Female", 60, "District Medical Centre", f"{D}T14:00:00", "Zone C"),
]
SEED_SHELTER = [
    (2, "Unknown Male", 24, "Relief Shelter A", f"{D}T14:30:00", "Zone B"),
]


def db_path() -> str:
    return os.getenv("RESQLINK_DB", "resqlink.db")


def _ensure_parent_dir(path: str) -> None:
    parent = os.path.dirname(path)
    if parent:
        os.makedirs(parent, exist_ok=True)


@contextmanager
def get_db():
    path = db_path()
    _ensure_parent_dir(path)
    conn = sqlite3.connect(path)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def init_db(seed: bool = True) -> None:
    with get_db() as db:
        db.executescript(SCHEMA)
        if seed and db.execute("SELECT COUNT(*) FROM persons").fetchone()[0] == 0:
            db.executemany("INSERT INTO persons VALUES (?,?,?,?,?,?,?,?)", SEED_PERSONS)
            db.executemany(
                "INSERT INTO hospital_records (person_id,name,age,hospital,admitted_at,location) VALUES (?,?,?,?,?,?)",
                SEED_HOSPITAL,
            )
            db.executemany(
                "INSERT INTO shelter_records (person_id,name,age,shelter,arrival_time,location) VALUES (?,?,?,?,?,?)",
                SEED_SHELTER,
            )


def audit(actor: str, action: str, detail: str = "") -> None:
    with get_db() as db:
        db.execute(
            "INSERT INTO audit_log (ts, actor, action, detail) VALUES (?,?,?,?)",
            (now_iso(), actor, action, detail),
        )
