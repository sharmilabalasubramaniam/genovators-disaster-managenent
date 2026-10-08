# ResQLink – Identity Recovery Agent (Agent 2)

FastAPI MVP that correlates fragmented hospital / rescue / shelter / family records into
an **Unknown Person Cluster**, scores the evidence, detects conflicts and moves the person through:

`UNKNOWN → PARTIALLY_IDENTIFIED → PROBABLE_IDENTITY → VERIFIED_PERSON` (human only)

## Run (Windows / VS Code)
```
python -m venv venv
.\venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```
Open http://127.0.0.1:8000/docs

macOS/Linux: `source venv/bin/activate`

## Endpoints
| Method | Path | Purpose |
|---|---|---|
| GET | /records | List demo records |
| POST | /identity/recover | `{"record_ids": ["H-781","R-221","S-442"]}` → cluster |
| GET | /clusters, /clusters/{id} | View clusters |
| GET | /clusters/{id}/graph | Evidence graph (nodes + edges) |
| POST | /identity/verify | Officer verification |

## Tests
`pytest -q`

## Scoring weights
Age 20 · Appearance 15 · Location 15 · Timeline 15 · Clothing 10 · Name 10 · Medical 10 · Gender 5.
Only categories where both records have data are compared; a coverage penalty applies when little is comparable.
Confidence is capped at 99%. The score alone can never produce `VERIFIED_PERSON`.
