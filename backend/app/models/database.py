"""
Database models and schema for the soccer players app.
"""

from datetime import date
from typing import Optional
import sqlite3
from pathlib import Path

DATABASE_PATH = Path(__file__).parent.parent.parent / "data" / "players.db"


def get_db_connection():
    """Get a database connection."""
    DATABASE_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(DATABASE_PATH))
    conn.row_factory = sqlite3.Row
    return conn


def init_database():
    """Initialize the database schema."""
    conn = get_db_connection()
    cursor = conn.cursor()

    # Players table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS players (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            wikidata_id TEXT UNIQUE NOT NULL,
            name TEXT NOT NULL,
            normalized_name TEXT NOT NULL,  -- lowercase, no accents for matching
            first_name TEXT,
            last_name TEXT,
            nationality TEXT,
            nationality_code TEXT,  -- ISO country code
            position TEXT,
            birth_date TEXT,
            gender TEXT DEFAULT 'male',  -- 'male' or 'female'
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # Clubs table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS clubs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            wikidata_id TEXT UNIQUE NOT NULL,
            name TEXT NOT NULL,
            normalized_name TEXT NOT NULL,
            country TEXT,
            league TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # Player-Club relationships (career history)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS player_clubs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            player_id INTEGER NOT NULL,
            club_id INTEGER NOT NULL,
            start_date TEXT,
            end_date TEXT,
            is_national_team BOOLEAN DEFAULT FALSE,
            FOREIGN KEY (player_id) REFERENCES players(id),
            FOREIGN KEY (club_id) REFERENCES clubs(id),
            UNIQUE(player_id, club_id, start_date)
        )
    """)

    # Sessions table (for tracking guessing sessions)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS sessions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # Guessed players per session
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS guessed_players (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id INTEGER NOT NULL,
            player_id INTEGER NOT NULL,
            guessed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (session_id) REFERENCES sessions(id),
            FOREIGN KEY (player_id) REFERENCES players(id),
            UNIQUE(session_id, player_id)
        )
    """)

    # Create indexes for fast lookups
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_players_normalized_name ON players(normalized_name)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_players_name ON players(name)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_clubs_name ON clubs(name)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_player_clubs_player ON player_clubs(player_id)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_player_clubs_club ON player_clubs(club_id)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_guessed_players_session ON guessed_players(session_id)")

    conn.commit()
    conn.close()
    print(f"Database initialized at {DATABASE_PATH}")


if __name__ == "__main__":
    init_database()
