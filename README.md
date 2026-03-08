# PennyPilot

PennyPilot is an AI-powered personal finance copilot that turns bank statements into actionable guidance.

It helps users:

- understand where money goes,
- get AI insights on spending behavior,
- set personalized savings goals,
- run category-level strategy simulations,
- and receive practical coaching to improve financial habits.

## What we built

### 1) Statement intelligence pipeline

- Upload and parse statement files (`.pdf` and `.csv`)
- Normalize transactions into a structured schema
- Auto-categorize spending by category and merchant
- Generate summary metrics and visual charts

### 2) AI CFO insights

- Gemini-generated spending analysis
- Spending Overview with top-category concentration in sentence form
- Key Patterns and Suggestions with merchant ranking included

### 3) Personalized strategy simulator

- Add multiple personal goals (example: camera lens, vacation)
- Enter goal amount manually, or let AI estimate goal cost
- Optional target date (default planning horizon if omitted)
- Dynamic category reductions across all available categories
- Monthly and annual savings projections
- AI strategy analysis with coaching guidance

### 4) Database privacy and security hardening

- Auth-protected API access with user identity extraction
- Statement ownership model (`owner_id`) and owner-scoped reads
- IDOR prevention by checking `statement_id + owner_id`
- Upload hardening:
  - file size limit,
  - extension/content-type validation,
  - generic error responses for safer exposure
- CORS tightened for safer defaults
- Access-control tests for owner/non-owner behavior

## Tech stack

### Frontend

- Next.js (App Router)
- React + TypeScript
- Tailwind CSS
- Recharts
- Auth0 Next.js SDK (`@auth0/nextjs-auth0`)

### Backend

- FastAPI
- SQLAlchemy
- SQLite or Postgres via `DATABASE_URL`
- Gemini (`google-genai`)
- `pandas`, `pdfplumber`, `pypdf` for parsing

## Project structure

```text
ai-cfo/
  backend/    # API routes, parsing, categorization, simulation, auth, db models
  frontend/   # Next.js UI, charts, simulator, auth-aware client
```

## Quick start

### 1) Clone

```bash
git clone https://github.com/Ryo0326-hub/PennyPilot.git
cd PennyPilot
```

### 2) Backend setup

```bash
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
uvicorn app.main:app --reload
```

Backend runs at `http://127.0.0.1:8000`.

### 3) Frontend setup

```bash
cd frontend
npm install
cp .env.example .env.local
npm run dev
```

Frontend runs at `http://localhost:3000`.

## Required environment variables

### Frontend (`frontend/.env.local`)

- `APP_BASE_URL` (example: `http://localhost:3000`)
- `AUTH0_DOMAIN`
- `AUTH0_CLIENT_ID`
- `AUTH0_CLIENT_SECRET`
- `AUTH0_SECRET`
- `NEXT_PUBLIC_API_BASE_URL` (example: `http://127.0.0.1:8000`)
- `AUTH0_AUDIENCE` (optional)

### Backend (`backend/.env`)

- `DATABASE_URL`
- `GEMINI_API_KEY`
- `ALLOWED_ORIGINS`
- `AUTH_REQUIRED` (`true`/`false`)
- `AUTH_ISSUER` (Auth0 issuer URL)
- `AUTH_JWKS_URL`
- `AUTH_AUDIENCE` (optional)
- `MAX_UPLOAD_BYTES`
- `ALLOW_TEST_AUTH_HEADER` (development helper)
- `ENVIRONMENT` (`development` or `production`)

## Core API endpoints

- `GET /health`
- `POST /upload/statement`
- `POST /upload/csv`
- `GET /statements/{statement_id}`
- `GET /summary/{statement_id}`
- `GET /insights/{statement_id}`
- `POST /simulate/{statement_id}`
- `POST /simulation-insights/{statement_id}`

## Security notes

- Never commit real secrets (`.env`, Auth0 secrets, API keys).
- Use `.env.example` as template only.
- Rotate keys immediately if exposed.
- Keep `ALLOW_TEST_AUTH_HEADER=false` and strict auth in production.

## Testing

Backend tests:

```bash
cd backend
python3 -m pytest -q
```

Frontend lint:

```bash
cd frontend
npm run lint
```

## Current status

PennyPilot currently supports:

- authenticated, owner-scoped statement privacy,
- AI-driven insights,
- personalized goal-based financial planning,
- and dynamic multi-category strategy simulation.
