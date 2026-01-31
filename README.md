# AI-Powered Document & Multimedia Q&A App

This repository contains a full-stack prototype for an AI-powered Q&A application supporting PDF, audio, and video uploads, transcription, summarization, and an LLM-powered chatbot.

## What I scaffolded
- FastAPI backend (endpoints: `/api/upload`, `/api/chat`, `/api/summarize`)
- React frontend (upload UI, chat UI)
- Docker Compose with `backend`, `frontend`, and `mongo`
- GitHub Actions CI to run backend tests
- Example tests for backend

## Quick start (local)
1. Copy `.env.example` to `.env` and set `OPENAI_API_KEY`.
2. Start with Docker Compose:

```bash
docker compose up --build
```

- Backend will be on `http://localhost:8000`
- Frontend (Vite) will be on `http://localhost:3000`

## Testing
Backend tests live in `backend/tests`. Run locally:

```bash
cd backend
pip install -r requirements.txt
pytest -q
```

## Notes & Next Steps
- PDF extraction, persistent DB storage, vector search (FAISS/Pinecone), and video timestamp extraction are scaffolded as TODOs.
- Replace placeholder LLM/transcription calls with your preferred provider and API keys.
- I can continue implementing PDF parsing, Mongo persistence, vector index, and frontend media player controls on request.
