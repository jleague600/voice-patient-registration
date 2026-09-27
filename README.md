# Voice AI Patient Registration System

A voice-based AI agent that collects U.S. patient demographic information
through natural conversation over a real phone number, persists it to a
Postgres database, and exposes it through a REST API.

## Live Demo

- **Phone number**: [TO BE ADDED once Vapi number is provisioned]
- **API base URL**: [TO BE ADDED once deployed to Vercel]
- **Repository**: https://github.com/jleague600/voice-patient-registration

## Architecture


- **Telephony + Voice**: Vapi provides the phone number, speech-to-text,
  text-to-speech, and conversation orchestration. The system prompt and
  tool definitions live in `voice_agent/`.
- **LLM**: Google Gemini, configured as Vapi's model provider.
- **Backend**: Python (FastAPI), organized by layer:
  - `app/api/routes/` -- HTTP endpoints only (parsing requests, shaping responses)
  - `app/services/` -- business logic (create, list, update, soft-delete, duplicate lookup)
  - `app/models/` -- `patient.py` (SQLAlchemy ORM/DB schema) and `schemas.py` (Pydantic request/response validation) are kept separate on purpose: the database model and the API's public shape are allowed to diverge (e.g. `deleted_at` exists in the DB but is never exposed over the API).
  - `app/core/` -- shared validation helpers (US state, zip, phone normalization) and structured logging.
  - `app/db/` -- database connection/session management, separate from table definitions.
- **Database**: PostgreSQL via Supabase, connected through Supabase's transaction-mode connection pooler.
- **Hosting**: Vercel (serverless).

## Tech Stack Justification

| Choice | Why |
|---|---|
| Vapi (telephony/voice) | Abstracts STT/TTS/telephony entirely, letting effort go into prompt engineering and backend integration rather than reimplementing speech infrastructure, within a 3-hour constraint. |
| Gemini (LLM) | Free-tier access, natively supported as a model provider inside Vapi with no custom integration code required. |
| FastAPI | Async-native (pairs well with an async Postgres driver), automatic request validation via Pydantic, and free interactive API docs (`/docs`) that were used for manual testing throughout development. |
| Supabase (Postgres) | Real persistence across restarts (a hard requirement), prior familiarity, and a generous free tier. |
| Vercel | Fast to deploy from a GitHub repo, generous free tier, no server management. |

## Data Model

The `patients` table implements the full spec's field list, with:
- Required fields enforced via `nullable=False` at the database level and via Pydantic validators at the API level (defense in depth -- the spec explicitly calls for not relying solely on the voice agent for validation).
- Soft-delete via a `deleted_at` timestamp column; every read query filters `WHERE deleted_at IS NULL`. `DELETE /patients/:id` sets this timestamp rather than removing the row.
- Auto-generated `patient_id` (UUID), `created_at`, `updated_at`.

## API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| GET | `/patients` | List patients. Supports `?last_name=`, `?date_of_birth=`, `?phone_number=` filters. |
| GET | `/patients/{id}` | Retrieve a single patient by UUID. |
| POST | `/patients` | Create a new patient. Returns the created record with `patient_id`. |
| PUT | `/patients/{id}` | Partial update of an existing patient. |
| DELETE | `/patients/{id}` | Soft-delete (sets `deleted_at`; does not remove the row). |

All responses use the envelope `{ "data": ..., "error": ... }`. Validation
errors return `422` with details on every failing field; missing records
return `404`.

## Voice Agent Design

The full system prompt and design rationale are documented in
`voice_agent/system_prompt.md`. Key decisions:
- Fields are collected in natural groups (e.g. full address together), not one-by-one, to avoid feeling like an IVR menu.
- Corrections are framed as "I may have misheard" rather than "you were wrong," to keep the tone natural.
- The agent checks for an existing patient by phone number (`check_existing_patient`) before registering, offering to update instead of duplicate (see Bonus Challenges).
- All collected information is read back for explicit confirmation before any save.
- Tool-call failures are handled explicitly in the prompt (retry once, then a graceful human-handoff message) rather than left to the LLM's default behavior, which otherwise tends to go silent or hallucinate success.

Tool/function definitions the agent uses to call the API are in
`voice_agent/tool_schema.json`.

## Setup Instructions

### Prerequisites
- Python 3.12 (not 3.14 -- some dependencies don't yet ship pre-built wheels for it)
- A Supabase account/project
- A Vapi account
- A Vercel account (for deployment)

### Local setup

```bash
git clone <repo-url>
cd voice-patient-registration
python -m venv venv
venv\Scripts\Activate.ps1        # Windows
# source venv/bin/activate       # macOS/Linux
pip install -r requirements.txt
```

Copy `.env.example` to `.env` and fill in real values (see Environment
Variables below).

Run locally:
```bash
uvicorn app.main:app --reload
```
Visit `http://127.0.0.1:8000/docs` for interactive API testing.

### Environment Variables

See `.env.example` for the full list.