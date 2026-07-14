# EduGenie

AI Powered Learning Assistant foundation built with FastAPI, Jinja2, and vanilla JavaScript.

## Overview

EduGenie is a lightweight foundation for building AI-powered educational experiences. It provides a FastAPI backend with server-rendered frontend assets and modular router/service structure to integrate AI models (e.g., Google Gemini).

---

## Quickstart

Prerequisites:
- Python 3.11+ (3.13 was used during development)
- A virtual environment

Installation:
```bash
python -m venv .venv
.\.venv\Scripts\activate    # Windows
pip install -r requirements.txt
```

Configuration:
1. Copy the example environment file:
```bash
cp .env.example .env
```
2. Edit `.env` and set `GEMINI_API_KEY` if you have Google Cloud credentials. If not set, the app will still run but Gemini-backed endpoints will return a clear 503 error explaining missing credentials.

Run the app:
```bash
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```
Open: http://127.0.0.1:8000

---

## Environment Variables
- `GEMINI_API_KEY` — (optional) Google Gemini API key or use Application Default Credentials.
- `DEBUG` — Set to `True` for development logging.
- `HOST` — Bind host (default `127.0.0.1`).
- `PORT` — Port to run on (default `8000`).

## API Endpoints
All endpoints accept and return JSON. Routes are mounted without an additional `/api` prefix.

- `GET /` — Landing page (HTML).
- `GET /health` — Health check (returns `{status: 'ok', message: ...}`).
- `POST /qa/` — Question answering. Payload: `{question: str, context?: str}`. Response: `BaseResponse` with `markdown` and `text`.
- `POST /explain/` — Concept explanation. Payload: `{topic: str, level?: str}`.
- `POST /quiz/` — Quiz generator. Payload: `{topic: str, num_questions?: int, difficulty?: str}`.
- `POST /summarize/` — Summarizer. Payload: `{text: str, max_length?: int}`.
- `POST /roadmap/` — Learning roadmap generator. Payload: `{subject: str, goals?: str, duration_weeks?: int}`.

All feature endpoints return a `BaseResponse` JSON object: `{success: bool, markdown?: str, text?: str, meta?: dict}`.

---

## Project Structure

- `app/` — Main application package
  - `main.py` — FastAPI app, router registration, global exception handlers
  - `config.py` — Pydantic settings and `.env` loading
  - `routers/` — Feature endpoints per module (`qa.py`, `explain.py`, `quiz.py`, `summarize.py`, `roadmap.py`)
  - `services/` — AI service layers (`gemini_service.py`, `formatter.py`, `prompt_engineering.py`)
  - `templates/` — Jinja2 templates (landing page)
  - `static/` — Frontend CSS/JS
  - `utils/` — Pydantic request/response models
- `scripts/` — Local development helpers (e.g., `check_endpoints.py`)
- `tests/` — Automated tests

---

## Features
- Landing page with interactive dashboard shell
- Client-side forms for QA, explanation, quizzes, summarization, and roadmap generation
- Backend modular routers with request validation via Pydantic
- Gemini service integration (optional) with structured error handling when credentials are missing
- Lazy local LaMini-Flan-T5 fallback when Gemini is unavailable, rate-limited, or misconfigured

---

## Development Notes & Best Practices
- The app uses Pydantic settings for configuration — keep secrets out of source control and use environment variables or secret managers in production.
- If you plan to enable Gemini integration in production, configure Google Cloud Application Default Credentials or set `GEMINI_API_KEY`.
- The frontend is vanilla JS and progressively enhanced — it expects module-capable browsers.

---

## Verification
I ran an internal endpoint smoke test (`scripts/check_endpoints.py`) with a dummy Gemini service. All endpoints returned `200` and valid `BaseResponse` payloads under the test harness. When Gemini credentials are not available, the real endpoints return `503` with a helpful `detail` message.

---

If you want, I can:
- Add automated end-to-end tests using Playwright (requires Chrome/Playwright installation).
- Add CI pipeline (GitHub Actions) to run tests and linting on push.

Contact: EduGenie Team <support@edugenie.example>
