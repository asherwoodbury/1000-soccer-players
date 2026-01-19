# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Build & Run Commands

```bash
# Start both backend and frontend
./run.sh

# Backend only (port 8000)
cd backend && python3 -m uvicorn app.main:app --host 0.0.0.0 --port 8000

# Frontend only (port 3000)
cd frontend && python3 -m http.server 3000

# Verify backend is running
curl http://localhost:8000/health

# Sample data extraction (20 players for testing)
python3 backend/scripts/extract_sample.py

# Full Wikidata extraction (47k+ players, takes several minutes)
python3 backend/scripts/extract_wikidata.py
```

API documentation is auto-generated at http://localhost:8000/docs when backend is running.

## Architecture

This is a soccer player guessing game where users try to name 1000 players from memory.

**Backend** (`backend/`): FastAPI + SQLite
- `app/main.py` - FastAPI entry point with CORS config
- `app/routers/players.py` - Player lookup with fuzzy matching and ambiguity handling
- `app/routers/sessions.py` - Session management, guess tracking, filtering by club/nationality
- `app/models/database.py` - SQLite schema (players, clubs, player_clubs, sessions, guessed_players)
- `scripts/extract_wikidata.py` - SPARQL queries to Wikidata for player data

**Frontend** (`frontend/`): Vanilla JS single-page app
- Session ID stored in localStorage for persistence
- Player data cached in memory after lookup

## Key Design Patterns

**Name Matching**: Player names are normalized (lowercase, diacritics removed) at insert time and during lookup. Lookup tries exact match first, then prefix match.

**Ambiguity Handling**: When multiple players match (different nationality), the API returns `ambiguous: true` and prompts user to be more specific rather than guessing.

**Club History**: The `player_clubs` table tracks career history with start/end dates. National teams are flagged separately via `is_national_team` boolean.

**Session State**: Backend is stateless - all user progress stored in database. Frontend localStorage only caches the session ID for recovery across page reloads.
