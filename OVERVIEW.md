# OVERVIEW.md

## Project Overview

**1000 Soccer Players** is a web-based guessing game where users try to name as many soccer players as possible from memory. When a player is correctly guessed, the app displays their nationality, position, and complete club history. Users can filter their guessed players by club or nationality to help recall additional players.

The player database is populated from Wikidata using SPARQL queries, covering players from top European leagues (Premier League, La Liga, Bundesliga, Serie A, Ligue 1) and women's leagues.

## Architecture

### Core Components

```
┌─────────────────────────────────────────────────────────┐
│                      Frontend                           │
│  Vanilla JavaScript SPA (index.html, app.js, styles.css)│
│  - Session ID stored in localStorage                    │
│  - Player data cached in memory                         │
└─────────────────────┬───────────────────────────────────┘
                      │ REST API (JSON)
┌─────────────────────▼───────────────────────────────────┐
│                      Backend                            │
│  FastAPI Application (app/main.py)                      │
│  ├── Players Router (routers/players.py)                │
│  │   - Player lookup with fuzzy name matching           │
│  │   - Database statistics                              │
│  └── Sessions Router (routers/sessions.py)              │
│      - Session creation and retrieval                   │
│      - Guess recording                                  │
│      - Filtering by club/nationality                    │
└─────────────────────┬───────────────────────────────────┘
                      │
┌─────────────────────▼───────────────────────────────────┐
│                    Data Layer                           │
│  SQLite Database (backend/data/players.db)              │
│  - Initialized via models/database.py                   │
│  - Populated via scripts/extract_wikidata.py            │
└─────────────────────────────────────────────────────────┘
```

### Data Flow

1. User enters a player name in the frontend
2. Frontend sends GET request to `/api/players/lookup?name=...`
3. Backend normalizes the name (lowercase, remove diacritics) and queries SQLite
4. If found, backend returns player data with club history
5. Frontend sends POST to `/api/sessions/{id}/guess/{player_id}` to record the guess
6. Session state is persisted in the database; frontend caches session ID in localStorage

## Data Model

### Tables

**players**
| Column | Type | Description |
|--------|------|-------------|
| id | INTEGER | Primary key |
| wikidata_id | TEXT | Unique Wikidata entity ID |
| name | TEXT | Display name |
| normalized_name | TEXT | Lowercase, no diacritics (for matching) |
| first_name | TEXT | Parsed first name |
| last_name | TEXT | Parsed last name |
| nationality | TEXT | Country of citizenship |
| position | TEXT | Playing position |
| birth_date | TEXT | Date of birth |
| gender | TEXT | 'male' or 'female' |

**clubs**
| Column | Type | Description |
|--------|------|-------------|
| id | INTEGER | Primary key |
| wikidata_id | TEXT | Unique Wikidata entity ID |
| name | TEXT | Club name |
| normalized_name | TEXT | Lowercase, no diacritics |
| country | TEXT | Club's country |
| league | TEXT | League name |

**player_clubs** (career history)
| Column | Type | Description |
|--------|------|-------------|
| player_id | INTEGER | FK to players |
| club_id | INTEGER | FK to clubs |
| start_date | TEXT | Start of tenure |
| end_date | TEXT | End of tenure |
| is_national_team | BOOLEAN | True if national team |

**sessions**
| Column | Type | Description |
|--------|------|-------------|
| id | INTEGER | Primary key |
| created_at | TIMESTAMP | Session creation time |
| updated_at | TIMESTAMP | Last activity time |

**guessed_players**
| Column | Type | Description |
|--------|------|-------------|
| session_id | INTEGER | FK to sessions |
| player_id | INTEGER | FK to players |
| guessed_at | TIMESTAMP | When guessed |

### Indexes
- `idx_players_normalized_name` - Fast name lookups
- `idx_players_name` - Display name searches
- `idx_player_clubs_player` - Club history queries
- `idx_guessed_players_session` - Session filtering

## API Endpoints

Base URL: `http://localhost:8000/api`

### Players

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/players/lookup?name={name}` | Look up player by name. Returns player data or ambiguity message. |
| GET | `/players/stats` | Get database statistics (total players, top nationalities, positions) |

### Sessions

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/sessions/` | Create new guessing session |
| GET | `/sessions/{id}` | Get session with all guessed players |
| POST | `/sessions/{id}/guess/{player_id}` | Record a guess (prevents duplicates) |
| GET | `/sessions/{id}/players/by-club?club_name={name}` | Filter guessed players by club |
| GET | `/sessions/{id}/players/by-nationality?nationality={country}` | Filter guessed players by nationality |

Auto-generated API docs available at `http://localhost:8000/docs` when backend is running.

## Technology Stack

| Component | Technology |
|-----------|------------|
| Backend Framework | FastAPI 0.109+ |
| ASGI Server | Uvicorn 0.27+ |
| Data Validation | Pydantic 2.0+ |
| Database | SQLite 3 |
| HTTP Client | Requests 2.31+ |
| Frontend | Vanilla JavaScript (ES6+) |
| Styling | CSS3 with CSS variables |
| Data Source | Wikidata SPARQL API |

## Project Structure

```
1000-soccer-players/
├── backend/
│   ├── app/
│   │   ├── main.py              # FastAPI app, CORS config, router registration
│   │   ├── models/
│   │   │   └── database.py      # Schema definition, connection management
│   │   └── routers/
│   │       ├── players.py       # Player lookup and stats endpoints
│   │       └── sessions.py      # Session management endpoints
│   ├── data/
│   │   └── players.db           # SQLite database (generated)
│   ├── scripts/
│   │   ├── extract_sample.py    # Extract 20 test players
│   │   └── extract_wikidata.py  # Full extraction (47k+ players)
│   └── requirements.txt
├── frontend/
│   ├── index.html               # Single-page app structure
│   ├── app.js                   # Application logic, API calls, state management
│   └── styles.css               # Responsive mobile-first styling
├── run.sh                       # Start both servers
├── CLAUDE.md                    # Claude Code guidance
└── OVERVIEW.md                  # This file
```

## Testing Strategy

No automated tests are currently implemented. Manual testing workflow:

1. Run sample data extraction: `python3 backend/scripts/extract_sample.py`
2. Start servers: `./run.sh`
3. Test player lookup via API: `curl "http://localhost:8000/api/players/lookup?name=Theo%20Walcott"`
4. Test frontend at `http://localhost:3000`

## Development Commands

```bash
# Start both backend and frontend
./run.sh

# Backend only (port 8000)
cd backend && python3 -m uvicorn app.main:app --host 0.0.0.0 --port 8000

# Frontend only (port 3000)
cd frontend && python3 -m http.server 3000

# Verify backend health
curl http://localhost:8000/health

# Sample data extraction (20 players, fast)
python3 backend/scripts/extract_sample.py

# Full Wikidata extraction (47k+ players, several minutes)
python3 backend/scripts/extract_wikidata.py

# Kill running servers
pkill -f "uvicorn app.main"
pkill -f "http.server 3000"
```

## Environment Setup

**Prerequisites:**
- Python 3.10+
- pip

**Installation:**
```bash
# Install backend dependencies
pip install -r backend/requirements.txt

# Initialize database with sample data
python3 backend/scripts/extract_sample.py

# Start the app
./run.sh
```

No environment variables or external configuration required. The SQLite database is created automatically at `backend/data/players.db`.

## Development Guidelines

1. **Name Matching**: Always normalize player names (lowercase, remove diacritics) before database operations. Use the `normalize_name()` function in `routers/players.py`.

2. **Ambiguity Handling**: When multiple players match a name (different nationalities), return `ambiguous: true` rather than guessing. Let the user be more specific.

3. **Session State**: Keep the backend stateless. All user progress must be stored in the database. Frontend localStorage only caches the session ID.

4. **Club History**: Track all clubs including national teams. Use `is_national_team` boolean to distinguish and allow filtering.

5. **CORS**: The backend allows requests from `localhost:3000` and `localhost:5173`. Update `main.py` if deploying to production.

## Security Considerations

1. **SQL Injection**: All database queries use parameterized statements. Never interpolate user input directly into SQL.

2. **Input Validation**: Player names must be at least 2 characters (enforced via Pydantic). Filter inputs must be at least 2 characters.

3. **Rate Limiting**: Not currently implemented. Consider adding if deploying publicly to prevent abuse of the Wikidata extraction scripts.

4. **Session IDs**: Sessions are simple auto-incrementing integers. For production, consider UUIDs to prevent enumeration.

5. **CORS**: Currently allows localhost origins only. Restrict to specific domains in production.

## Future Considerations

1. **Multiplayer Mode**: Allow multiple users to join the same session and guess in parallel, seeing each other's progress in real-time.

2. **Additional Sports**: Extend the data model and extraction scripts to support basketball, baseball, and other sports.

3. **Hint System**: Show team rosters with blanks for unguessed players. Toggle difficulty by hiding/showing positions, years, etc.

4. **Native iOS App**: The current architecture (REST API + separate frontend) is designed to support a future React Native mobile app.

5. **User Accounts**: Add authentication to persist sessions across devices and track lifetime statistics.

6. **Expanded Leagues**: Add support for Portuguese, Dutch, Turkish, and other leagues. Women's leagues need better Wikidata coverage.

7. **Full-Text Search**: Consider SQLite FTS5 for better fuzzy matching on misspelled names.
