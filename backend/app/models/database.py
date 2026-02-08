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
            is_stale BOOLEAN DEFAULT 0,
            FOREIGN KEY (player_id) REFERENCES players(id),
            FOREIGN KEY (club_id) REFERENCES clubs(id),
            UNIQUE(player_id, club_id, start_date)
        )
    """)

    # Add is_stale column if table already exists without it
    try:
        cursor.execute("ALTER TABLE player_clubs ADD COLUMN is_stale BOOLEAN DEFAULT 0")
    except sqlite3.OperationalError:
        pass  # Column already exists

    # Club aliases for matching names across data sources
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS club_aliases (
            id INTEGER PRIMARY KEY,
            club_id INTEGER NOT NULL REFERENCES clubs(id),
            name TEXT NOT NULL,
            normalized_name TEXT NOT NULL,
            source TEXT NOT NULL,
            external_id TEXT,
            UNIQUE(normalized_name, source)
        )
    """)
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_club_aliases_normalized ON club_aliases(normalized_name)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_club_aliases_club ON club_aliases(club_id)")

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

    # FTS5 virtual table for full-text search on player names
    # Uses unicode61 tokenizer with diacritics removal for consistent matching
    cursor.execute("""
        CREATE VIRTUAL TABLE IF NOT EXISTS players_fts USING fts5(
            name,
            normalized_name,
            content='players',
            content_rowid='id',
            tokenize='unicode61 remove_diacritics 2'
        )
    """)

    # Triggers to keep FTS index in sync with players table
    cursor.execute("""
        CREATE TRIGGER IF NOT EXISTS players_ai AFTER INSERT ON players BEGIN
            INSERT INTO players_fts(rowid, name, normalized_name)
            VALUES (new.id, new.name, new.normalized_name);
        END
    """)

    cursor.execute("""
        CREATE TRIGGER IF NOT EXISTS players_ad AFTER DELETE ON players BEGIN
            INSERT INTO players_fts(players_fts, rowid, name, normalized_name)
            VALUES ('delete', old.id, old.name, old.normalized_name);
        END
    """)

    cursor.execute("""
        CREATE TRIGGER IF NOT EXISTS players_au AFTER UPDATE ON players BEGIN
            INSERT INTO players_fts(players_fts, rowid, name, normalized_name)
            VALUES ('delete', old.id, old.name, old.normalized_name);
            INSERT INTO players_fts(rowid, name, normalized_name)
            VALUES (new.id, new.name, new.normalized_name);
        END
    """)

    conn.commit()
    conn.close()
    print(f"Database initialized at {DATABASE_PATH}")


def rebuild_fts_index():
    """
    Rebuild the FTS5 index from scratch.
    Run this after bulk data imports or if the index gets out of sync.
    """
    conn = get_db_connection()
    cursor = conn.cursor()

    print("Rebuilding FTS5 index...")

    # Clear and rebuild the FTS index
    cursor.execute("DELETE FROM players_fts")
    cursor.execute("""
        INSERT INTO players_fts(rowid, name, normalized_name)
        SELECT id, name, normalized_name FROM players
    """)

    conn.commit()

    # Get count to verify
    cursor.execute("SELECT COUNT(*) FROM players_fts")
    count = cursor.fetchone()[0]

    conn.close()
    print(f"FTS5 index rebuilt with {count} players")
    return count


def fts_search(query: str, limit: int = 20, use_prefix: bool = True) -> list[dict]:
    """
    Search for players using FTS5 full-text search.

    Uses unicode61 tokenizer with prefix matching for fast candidate retrieval.
    Returns list of player dicts with id, name, nationality, position.

    Args:
        query: Search query (player name)
        limit: Maximum results to return
        use_prefix: If True, adds wildcard for prefix matching (e.g., "crist*")
    """
    conn = get_db_connection()
    cursor = conn.cursor()

    import unicodedata
    import re

    # Normalize the query the same way we normalize player names
    normalized_query = unicodedata.normalize('NFKD', query)
    normalized_query = ''.join(c for c in normalized_query if not unicodedata.combining(c))
    normalized_query = normalized_query.lower().strip()
    normalized_query = re.sub(r'\s+', ' ', normalized_query)

    # Build FTS5 query - handle multiple words
    words = normalized_query.split()
    if use_prefix and words:
        # Add prefix wildcard to last word for partial matching
        # e.g., "lionel mes" -> "lionel mes*"
        fts_query = ' '.join(words[:-1] + [words[-1] + '*']) if len(words) > 0 else normalized_query + '*'
    else:
        fts_query = normalized_query

    try:
        cursor.execute("""
            SELECT p.id, p.name, p.nationality, p.position, p.wikidata_id
            FROM players_fts fts
            JOIN players p ON fts.rowid = p.id
            WHERE players_fts MATCH ?
            ORDER BY rank
            LIMIT ?
        """, (fts_query, limit))

        rows = cursor.fetchall()
        conn.close()

        return [dict(row) for row in rows]

    except Exception as e:
        conn.close()
        print(f"FTS search error: {e}")
        return []


def fts_search_fuzzy(query: str, limit: int = 20, max_distance: int = 2) -> list[dict]:
    """
    Fuzzy search combining FTS5 with Levenshtein distance filtering.

    Strategy:
    1. Generate multiple prefix variations to catch typos (e.g., "chr" -> try "cr", "ch", "chr")
    2. Get candidates from FTS5 using these prefixes
    3. Filter candidates using Levenshtein distance

    This handles typos like "Christiano" -> "Cristiano Ronaldo"
    """
    conn = get_db_connection()
    cursor = conn.cursor()

    import unicodedata
    import re

    # Normalize the query
    normalized_query = unicodedata.normalize('NFKD', query)
    normalized_query = ''.join(c for c in normalized_query if not unicodedata.combining(c))
    normalized_query = normalized_query.lower().strip()
    normalized_query = re.sub(r'\s+', ' ', normalized_query)

    # Strategy: Get candidates using multiple prefix variations
    words = normalized_query.split()

    candidates = []

    def generate_prefix_variations(word: str, max_len: int = 5) -> set:
        """Generate prefix variations to catch common typos."""
        variations = set()
        prefix = word[:max_len] if len(word) >= max_len else word

        # Original prefix and shorter versions
        for i in range(2, len(prefix) + 1):
            variations.add(word[:i])

        # Try removing each character (catches insertions like "chr" -> "cr")
        for i in range(len(prefix)):
            var = prefix[:i] + prefix[i+1:]
            if len(var) >= 2:
                variations.add(var)

        # Try swapping adjacent characters (catches transpositions like "salha" -> "salah")
        for i in range(len(prefix) - 1):
            var = prefix[:i] + prefix[i+1] + prefix[i] + prefix[i+2:]
            if len(var) >= 2:
                variations.add(var[:max_len])

        # Try common vowel substitutions (a<->e, e<->i, o<->u)
        vowel_swaps = {'a': 'e', 'e': 'a', 'i': 'e', 'o': 'u', 'u': 'o', 'y': 'i'}
        for i, char in enumerate(prefix):
            if char in vowel_swaps:
                var = prefix[:i] + vowel_swaps[char] + prefix[i+1:]
                if len(var) >= 2:
                    variations.add(var)

        return variations

    try:
        for word in words:
            if len(word) >= 2:
                # Generate prefix variations to catch typos
                prefixes = generate_prefix_variations(word, max_len=5)

                for prefix in prefixes:
                    if len(prefix) >= 2:
                        cursor.execute("""
                            SELECT DISTINCT p.id, p.name, p.nationality, p.position, p.wikidata_id,
                                   p.normalized_name
                            FROM players_fts fts
                            JOIN players p ON fts.rowid = p.id
                            WHERE players_fts MATCH ?
                            LIMIT 50
                        """, (f'{prefix}*',))
                        candidates.extend(cursor.fetchall())

        conn.close()

        if not candidates:
            return []

        # Remove duplicates
        seen = set()
        unique_candidates = []
        for c in candidates:
            if c['id'] not in seen:
                seen.add(c['id'])
                unique_candidates.append(c)

        # Import Levenshtein - try both paths for different execution contexts
        try:
            from app.services.fuzzy_matching import levenshtein_distance
        except ImportError:
            from backend.app.services.fuzzy_matching import levenshtein_distance

        # Score candidates by Levenshtein distance to query
        scored = []
        for candidate in unique_candidates:
            candidate_normalized = candidate['normalized_name']

            # Check distance for the full name
            distance = levenshtein_distance(normalized_query, candidate_normalized)

            # Also check if query matches any word in the name
            candidate_words = candidate_normalized.split()
            word_distances = [(levenshtein_distance(normalized_query, w), w) for w in candidate_words]
            min_word_distance, closest_word = min(word_distances, key=lambda x: x[0]) if word_distances else (distance, '')

            # Use the better (lower) distance
            best_distance = min(distance, min_word_distance)

            # Apply length-based threshold
            query_len = len(normalized_query)
            if query_len <= 4:
                threshold = 1
            elif query_len <= 8:
                threshold = 2
            else:
                threshold = 3

            if best_distance <= threshold:
                # Score adjustments for better ranking:
                # - Prefer when the matching word is the first word (likely first name/main name)
                # - Prefer when query length is similar to matching word length
                score = best_distance * 10  # Base score from distance

                # Bonus for first word match
                if closest_word and candidate_words and closest_word == candidate_words[0]:
                    score -= 2

                # Bonus for similar length (penalize if lengths differ significantly)
                length_diff = abs(len(normalized_query) - len(closest_word)) if closest_word else 0
                score += length_diff * 0.5

                # Tiebreaker: prefer when ending matches (helps "christiano" -> "cristiano" over "christian")
                # because the typo is usually at the beginning, not the end
                if closest_word and len(closest_word) >= 3 and len(normalized_query) >= 3:
                    # Compare last 3 characters
                    if normalized_query[-3:] == closest_word[-3:]:
                        score -= 1
                    elif normalized_query[-2:] == closest_word[-2:]:
                        score -= 0.5

                # Secondary tiebreaker: prefer shorter overall names (more likely to be famous single-name players)
                score += len(candidate_normalized) * 0.01

                scored.append((score, dict(candidate)))

        # Sort by distance and return top results
        scored.sort(key=lambda x: x[0])
        return [item[1] for item in scored[:limit]]

    except Exception as e:
        conn.close()
        print(f"FTS fuzzy search error: {e}")
        return []


if __name__ == "__main__":
    init_database()
