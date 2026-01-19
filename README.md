# 1000 Soccer Players

A web-based guessing game where users try to name as many soccer players as possible from memory. When a player is correctly guessed, the app displays their nationality, position, and complete club history.

## Quick Start

```bash
# Install dependencies
pip install -r backend/requirements.txt

# Initialize database with sample data (20 players)
python3 backend/scripts/extract_sample.py

# Start both frontend and backend
./run.sh
```

Visit [http://localhost:3000](http://localhost:3000) to play the game.

## Features

- Name-based player lookup with fuzzy matching
- Handles ambiguous names (prompts for more specific input)
- Session persistence via localStorage
- Filter guessed players by club or nationality
- Complete club history for each player
- Data sourced from Wikidata (47,000+ players available)

## Architecture

- **Backend**: FastAPI + SQLite
- **Frontend**: Vanilla JavaScript (no frameworks)
- **Data Source**: Wikidata SPARQL API

## Documentation

- [OVERVIEW.md](OVERVIEW.md) - Detailed architecture, data model, and API documentation
- [CLAUDE.md](CLAUDE.md) - Development guidance for Claude Code

## Development

```bash
# Backend only (port 8000)
cd backend && python3 -m uvicorn app.main:app --host 0.0.0.0 --port 8000

# Frontend only (port 3000)
cd frontend && python3 -m http.server 3000

# Full data extraction (47k+ players, takes several minutes)
python3 backend/scripts/extract_wikidata.py
```

API documentation is auto-generated at [http://localhost:8000/docs](http://localhost:8000/docs).

## Tech Stack

- FastAPI 0.109+
- Uvicorn 0.27+
- SQLite 3
- Vanilla JavaScript (ES6+)
- CSS3

## License

Personal project for educational purposes.
