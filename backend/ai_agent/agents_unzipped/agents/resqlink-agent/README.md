# ResQLink AI Agent (v2)

AI-assisted disaster family reunification: **the AI finds leads, authorized humans verify.**

Stack: Python, FastAPI, LangGraph, SQLite.

## Quick start (Windows / VS Code)

```powershell
cd resqlink-agent
python -m venv venv
# If PowerShell blocks activation:
# Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
.\venv\Scripts\activate
pip install -r requirements-dev.txt
copy .env.example .env      # then edit .env: OPENAI_API_KEY and AUTHORITY_API_KEY
pytest                      # optional: 9 tests, no API key needed
uvicorn app.main:app --reload
```

Open http://127.0.0.1:8000/docs. A demo SQLite database (`resqlink.db`) is created and seeded on first start.

## Try it

**Agent (needs OPENAI_API_KEY):** `POST /agent/chat`
```json
{ "message": "Find Arun Kumar who went missing during the flood." }
```

**No-LLM endpoints (work without any API key):**
- `GET /persons/1/matches` - scored candidates with hospital + shelter trail
- `GET /cases/1/2/firewall` - firewall decision for missing #1 vs candidate #2

**Human-only endpoints (header `X-Authority-Key: <AUTHORITY_API_KEY>`):**
- `POST /cases/verify` - officer records identity / relationship verification
- `POST /cases/reunite` - allowed only when the firewall returns `SAFE_TO_VERIFY`

Demo flow: matches -> firewall says `REVIEW` -> officer verifies -> firewall says `SAFE_TO_VERIFY` -> reunite.

## What changed from v1

| Issue | Fix |
|---|---|
| Wrong example score | Scores are normalised over comparable factors; unnamed records are capped at 90; conflicts cap at 49 |
| Hospital/shelter lookup by name missed "Unknown Male" | Lookups by `person_id`; `find_matches` returns the full trail |
| Brittle `==` description match | Fuzzy token + sequence similarity with synonyms (t-shirt/shirt, trousers/pants) |
| LLM supplied firewall flags | Firewall takes only IDs; flags come from the `cases` table, writable only via authenticated endpoints; timeline is computed from timestamps |
| In-memory lists | Real SQLite schema, seeded demo data, audit log |
| Unpinned deps | Exact versions in `requirements.txt` |
| PII sent to third-party LLM | Read-only tools, audit trail, `OPENAI_BASE_URL` for a private/self-hosted endpoint |

## Project layout

```
app/
  database.py   SQLite schema, seed data, audit log
  matching.py   fuzzy multi-factor scoring
  tools.py      search, matching, firewall, human-only actions
  agent.py      LangGraph agent (read-only tools)
  main.py       FastAPI app
tests/test_core.py
```

## Privacy notes

Missing-person records are sensitive. Before real use: run the LLM on a private endpoint, add real
authentication (per-officer accounts instead of one shared key), encrypt the database at rest, and
define a retention policy. Real deployments should also add rate limiting and HTTPS.

## Next steps

PostgreSQL migration, face-match tool, nearby shelter lookup, family notification (human-triggered).
