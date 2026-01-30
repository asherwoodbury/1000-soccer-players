"""
Session management for guessing game.
"""

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
from typing import Optional
from datetime import datetime

from app.models.database import get_db_connection
from app.routers.clubs import format_national_team_name

router = APIRouter()


class SessionResponse(BaseModel):
    id: int
    created_at: str
    player_count: int


class ClubHistory(BaseModel):
    name: str
    display_name: str  # Short display name for national teams
    start_date: Optional[str]
    end_date: Optional[str]
    is_national_team: bool


class GuessedPlayerSummary(BaseModel):
    id: int
    name: str
    nationality: Optional[str]
    position: Optional[str]
    top_clubs: list[str]
    clubs: list[ClubHistory]
    career_span: Optional[str]
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
        player_id = row['id']

        # Get full club history
        cursor.execute("""
            SELECT c.name, pc.start_date, pc.end_date, pc.is_national_team
            FROM player_clubs pc
            JOIN clubs c ON pc.club_id = c.id
            WHERE pc.player_id = ?
            ORDER BY pc.start_date
        """, (player_id,))

        clubs = [
            ClubHistory(
                name=r['name'],
                display_name=format_national_team_name(r['name']) if r['is_national_team'] else r['name'],
                start_date=r['start_date'],
                end_date=r['end_date'],
                is_national_team=bool(r['is_national_team'])
            )
            for r in cursor.fetchall()
        ]

        # Calculate top clubs by duration (non-national teams)
        from app.routers.players import calculate_club_duration_years
        non_national_clubs = [c for c in clubs if not c.is_national_team]
        club_durations = []
        for club in non_national_clubs:
            duration = calculate_club_duration_years(club.start_date, club.end_date)
            club_durations.append((club.name, duration))
        club_durations.sort(key=lambda x: x[1], reverse=True)
        seen_clubs = set()
        top_clubs = []
        for club_name, _ in club_durations:
            if club_name not in seen_clubs:
                seen_clubs.add(club_name)
                top_clubs.append(club_name)
                if len(top_clubs) >= 3:
                    break

        # Calculate career span
        career_span = None
        if clubs:
            start_years = []
            end_years = []
            has_active_club = False
            for club in clubs:
                if club.start_date:
                    try:
                        start_years.append(int(club.start_date[:4]))
                    except (ValueError, TypeError):
                        pass
                if club.end_date:
                    try:
                        end_years.append(int(club.end_date[:4]))
                    except (ValueError, TypeError):
                        pass
                else:
                    has_active_club = True

            if start_years:
                earliest = min(start_years)
                if has_active_club:
                    career_span = f"{earliest}-present"
                elif end_years:
                    latest = max(end_years)
                    career_span = f"{earliest}-{latest}"

        players.append(GuessedPlayerSummary(
            id=row['id'],
            name=row['name'],
            nationality=row['nationality'],
            position=row['position'],
            top_clubs=top_clubs,
            clubs=clubs,
            career_span=career_span,
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
