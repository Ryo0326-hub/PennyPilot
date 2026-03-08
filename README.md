# PennyPilot

PennyPilot is an AI-powered financial agent that helps you understand your spending and improve your financial habits.

Upload your bank statement and PennyPilot will:

- parse your transactions,
- categorize your spending,
- show clear charts and summaries,
- suggest ways to reduce unnecessary expenses,
- simulate savings strategies so you can test "what if" scenarios.

The goal is simple: make personal finance insights easy for everyone to understand.

## Why this project exists

Most bank statements are hard to read and act on.  
PennyPilot turns raw statement data into plain, practical guidance.

## Main features

- Statement upload (`.pdf`)
- Automatic transaction parsing and categorization
- Spending summary cards and category charts
- AI-generated spending insights
- Strategy simulator for restaurants, subscriptions, and shopping cuts
- AI explanation of your simulated strategy results

## Tech stack

### Frontend
- Next.js
- React + TypeScript
- Tailwind CSS
- Recharts

### Backend
- FastAPI
- SQLAlchemy
- SQLite (or any SQLAlchemy-compatible database URL)
- Google Gemini API (`google-genai`)
- pandas + pdfplumber/pypdf for statement parsing

## Project structure

```text
ai-cfo/
  backend/    # FastAPI API, parsing, categorization, summaries, AI services
  frontend/   # Next.js user interface
```

## How it works

1. You upload a statement file.
2. The backend parses transactions and stores them in the database.
3. Transactions are categorized (for example: restaurants, shopping, subscriptions).
4. The app calculates totals, merchant stats, and category breakdowns.
5. Gemini generates readable insights and suggestions.
6. You can run a strategy simulation to estimate monthly and annual savings.

## Quick start

### 1) Clone the repo

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
```

Edit `backend/.env`:

```env
GEMINI_API_KEY=your_real_api_key
DATABASE_URL=sqlite:///./app.db
```

Run backend server:

```bash
uvicorn app.main:app --reload
```

Backend runs at `http://127.0.0.1:8000`.

### 3) Frontend setup

In a new terminal:

```bash
cd frontend
npm install
npm run dev
```

Frontend runs at `http://localhost:3000`.

## API endpoints (core)

- `GET /health` - health check
- `POST /upload/statement` - upload and parse statement file
- `GET /statements/{statement_id}` - list parsed transactions for a statement
- `GET /summary/{statement_id}` - spending summary
- `GET /insights/{statement_id}` - AI-generated spending insights
- `POST /simulate/{statement_id}` - run savings simulation
- `POST /simulation-insights/{statement_id}` - simulation + AI explanation

## Environment variables

Backend (`backend/.env`):

- `GEMINI_API_KEY` - required for AI insights
- `DATABASE_URL` - required database connection string

## Security note

- Never commit real `.env` files or API keys.
- Commit only `.env.example` with placeholder values.
- If a key is accidentally exposed, rotate/revoke it immediately.

## Current status

PennyPilot is in active development and focused on:

- better statement compatibility across banks,
- more robust categorization,
- smarter, more actionable AI recommendations.
