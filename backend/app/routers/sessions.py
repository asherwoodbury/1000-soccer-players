"""
Session management for guessing game.
"""

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
from typing import Optional
from datetime import datetime

from app.models.database import get_db_connection

router = APIRouter()


class SessionResponse(BaseModel):
    id: int
    created_at: str
    player_count: int


class GuessedPlayerSummary(BaseModel):
    id: int
    name: str
    nationality: Optional[str]
    position: Optional[str]
    top_clubs: list[str]
    guessed_at: str


class SessionDetail(BaseModel):
    id: int
    created_at: str
    player_count: int
    players: list[GuessedPlayerSummary]


class GuessResult(BaseModel):
    success: bool
    already_guessed: bool
    player_count: int
    message: str


@router.post("/", response_model=SessionResponse)
async def create_session():
    """Create a new guessing session."""
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("INSERT INTO sessions DEFAULT VALUES")
    session_id = cursor.lastrowid

    conn.commit()
    conn.close()

    return SessionResponse(
        id=session_id,
        created_at=datetime.now().isoformat(),
        player_count=0
    )


@router.get("/{session_id}", response_model=SessionDetail)
async def get_session(session_id: int):
    """Get session details including all guessed players."""
    conn = get_db_connection()
    cursor = conn.cursor()

    # Get session
    cursor.execute("SELECT * FROM sessions WHERE id = ?", (session_id,))
    session = cursor.fetchone()

    if not session:
        conn.close()
        raise HTTPException(status_code=404, detail="Session not found")

    # Get guessed players
    cursor.execute("""
        SELECT p.id, p.name, p.nationality, p.position, gp.guessed_at
        FROM guessed_players gp
        JOIN players p ON gp.player_id = p.id
        WHERE gp.session_id = ?
        ORDER BY gp.guessed_at DESC
    """, (session_id,))

    players = []
    for row in cursor.fetchall():
        # Get top clubs for each player
        cursor.execute("""
            SELECT c.name
            FROM player_clubs pc
            JOIN clubs c ON pc.club_id = c.id
            WHERE pc.player_id = ? AND pc.is_national_team = 0
            LIMIT 3
        """, (row['id'],))
        top_clubs = [r['name'] for r in cursor.fetchall()]

        players.append(GuessedPlayerSummary(
            id=row['id'],
            name=row['name'],
            nationality=row['nationality'],
            position=row['position'],
            top_clubs=top_clubs,
            guessed_at=row['guessed_at']
        ))

    conn.close()

    return SessionDetail(
        id=session['id'],
        created_at=session['created_at'],
        player_count=len(players),
        players=players
    )


@router.post("/{session_id}/guess/{player_id}", response_model=GuessResult)
async def add_guess(session_id: int, player_id: int):
    """Add a guessed player to the session."""
    conn = get_db_connection()
    cursor = conn.cursor()

    # Verify session exists
    cursor.execute("SELECT id FROM sessions WHERE id = ?", (session_id,))
    if not cursor.fetchone():
        conn.close()
        raise HTTPException(status_code=404, detail="Session not found")

    # Verify player exists
    cursor.execute("SELECT name FROM players WHERE id = ?", (player_id,))
    player = cursor.fetchone()
    if not player:
        conn.close()
        raise HTTPException(status_code=404, detail="Player not found")

    # Check if already guessed
    cursor.execute("""
        SELECT id FROM guessed_players
        WHERE session_id = ? AND player_id = ?
    """, (session_id, player_id))

    if cursor.fetchone():
        # Get current count
        cursor.execute("""
            SELECT COUNT(*) as count FROM guessed_players WHERE session_id = ?
        """, (session_id,))
        count = cursor.fetchone()['count']
        conn.close()

        return GuessResult(
            success=False,
            already_guessed=True,
            player_count=count,
            message=f"You already guessed {player['name']}!"
        )

    # Add the guess
    cursor.execute("""
        INSERT INTO guessed_players (session_id, player_id)
        VALUES (?, ?)
    """, (session_id, player_id))

    # Get new count
    cursor.execute("""
        SELECT COUNT(*) as count FROM guessed_players WHERE session_id = ?
    """, (session_id,))
    count = cursor.fetchone()['count']

    # Update session timestamp
    cursor.execute("""
        UPDATE sessions SET updated_at = CURRENT_TIMESTAMP WHERE id = ?
    """, (session_id,))

    conn.commit()
    conn.close()

    return GuessResult(
        success=True,
        already_guessed=False,
        player_count=count,
        message=f"Added {player['name']}! ({count} players guessed)"
    )


@router.get("/{session_id}/players/by-club")
async def get_players_by_club(session_id: int, club_name: str = Query(..., min_length=2)):
    """Get guessed players filtered by club."""
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT DISTINCT p.id, p.name, p.nationality, p.position
        FROM guessed_players gp
        JOIN players p ON gp.player_id = p.id
        JOIN player_clubs pc ON p.id = pc.player_id
        JOIN clubs c ON pc.club_id = c.id
        WHERE gp.session_id = ?
          AND LOWER(c.name) LIKE LOWER(?)
        ORDER BY p.name
    """, (session_id, f"%{club_name}%"))

    players = [
        {
            "id": row['id'],
            "name": row['name'],
            "nationality": row['nationality'],
            "position": row['position']
        }
        for row in cursor.fetchall()
    ]

    conn.close()

    return {
        "club_filter": club_name,
        "count": len(players),
        "players": players
    }


@router.get("/{session_id}/players/by-nationality")
async def get_players_by_nationality(session_id: int, nationality: str = Query(..., min_length=2)):
    """Get guessed players filtered by nationality."""
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT p.id, p.name, p.nationality, p.position
        FROM guessed_players gp
        JOIN players p ON gp.player_id = p.id
        WHERE gp.session_id = ?
          AND LOWER(p.nationality) LIKE LOWER(?)
        ORDER BY p.name
    """, (session_id, f"%{nationality}%"))

    players = [
        {
            "id": row['id'],
            "name": row['name'],
            "nationality": row['nationality'],
            "position": row['position']
        }
        for row in cursor.fetchall()
    ]

    conn.close()

    return {
        "nationality_filter": nationality,
        "count": len(players),
        "players": players
    }
