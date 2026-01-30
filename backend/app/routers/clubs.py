"""
Club search and roster endpoints.
"""

from fastapi import APIRouter, Query
from pydantic import BaseModel
from typing import Optional
import unicodedata
import re

from app.models.database import get_db_connection

router = APIRouter()


def normalize_name(name: str) -> str:
    """Normalize a name for matching."""
    normalized = unicodedata.normalize('NFKD', name)
    normalized = ''.join(c for c in normalized if not unicodedata.combining(c))
    normalized = normalized.lower().strip()
    normalized = re.sub(r'\s+', ' ', normalized)
    return normalized


def format_national_team_name(name: str) -> str:
    """
    Convert long national team names to short display format.

    Examples:
    - "Argentina men's national association football team" → "Argentina (M)"
    - "Germany women's national football team" → "Germany (W)"
    - "Brazil national under-20 football team" → "Brazil U20"
    - "France national under-23 football team" → "France U23 (M)"
    - "Spain women's national under-19 football team" → "Spain U19 (W)"
    """
    # Check if this looks like a national team name
    if 'national' not in name.lower():
        return name

    # Determine gender
    is_women = "women" in name.lower()
    gender_suffix = " (W)" if is_women else " (M)"

    # Check for youth age groups
    youth_match = re.search(r'under-(\d+)', name.lower())
    youth_suffix = ""
    if youth_match:
        youth_suffix = f" U{youth_match.group(1)}"

    # Extract country name (everything before "men's", "women's", or "national")
    # Try different patterns
    country = None

    # Pattern: "Country men's national..." or "Country women's national..."
    match = re.match(r"^(.+?)\s+(?:men's|women's)\s+national", name, re.IGNORECASE)
    if match:
        country = match.group(1)
    else:
        # Pattern: "Country national under-XX..." or "Country national..."
        match = re.match(r"^(.+?)\s+national", name, re.IGNORECASE)
        if match:
            country = match.group(1)

    if not country:
        return name

    # Clean up country name
    country = country.strip()

    # Build short name
    if youth_suffix:
        return f"{country}{youth_suffix}{gender_suffix}"
    else:
        return f"{country}{gender_suffix}"


def get_national_team_priority(name: str) -> int:
    """
    Return a priority score for sorting national teams.
    Lower score = higher priority (appears first).

    Priority order:
    1. Senior men's teams (score 0)
    2. Senior women's teams (score 1)
    3. Youth teams by age descending (U23 before U21 before U20, etc.)
    """
    name_lower = name.lower()

    # Check if this is a national team
    if 'national' not in name_lower:
        return 100  # Non-national teams go last

    # Check for youth age group
    youth_match = re.search(r'under-(\d+)', name_lower)
    if youth_match:
        age = int(youth_match.group(1))
        # Youth teams get score 10-29 based on age (higher age = lower score = higher priority)
        # U23 = 10+7 = 17, U21 = 10+9 = 19, U20 = 10+10 = 20, U19 = 10+11 = 21, U17 = 10+13 = 23
        base_score = 10 + (30 - age)
        # Women's youth teams slightly lower priority than men's
        if "women" in name_lower:
            base_score += 1
        return base_score

    # Senior teams
    if "women" in name_lower:
        return 1  # Senior women's
    return 0  # Senior men's


class ClubSearchResult(BaseModel):
    id: int
    name: str
    display_name: str  # Short display name for national teams
    is_national_team: bool


class RosterPlayer(BaseModel):
    id: int
    name: str
    position: Optional[str]
    start_year: Optional[int]
    end_year: Optional[int]  # None means still at club


class RosterResponse(BaseModel):
    club_id: int
    club_name: str  # Full name
    display_name: str  # Short display name for national teams
    season: str
    players: list[RosterPlayer]
    total_count: int


@router.get("/search", response_model=list[ClubSearchResult])
async def search_clubs(
    query: str = Query(..., min_length=2, description="Search term for club name"),
    limit: int = Query(20, ge=1, le=50, description="Maximum results to return")
):
    """
    Search for clubs by name.
    Returns clubs matching the search term. National teams are sorted with
    senior teams first (men's, then women's), followed by youth teams by age.
    Non-national clubs are sorted by player count (popularity).
    """
    conn = get_db_connection()
    cursor = conn.cursor()

    normalized = normalize_name(query)

    # Search for clubs with players - fetch more than limit to allow for re-sorting
    cursor.execute("""
        SELECT c.id, c.name,
               EXISTS(SELECT 1 FROM player_clubs pc
                      WHERE pc.club_id = c.id AND pc.is_national_team = 1) as is_national_team,
               COUNT(DISTINCT pc.player_id) as player_count
        FROM clubs c
        LEFT JOIN player_clubs pc ON c.id = pc.club_id
        WHERE c.normalized_name LIKE ?
        GROUP BY c.id
        ORDER BY player_count DESC
        LIMIT ?
    """, (f"%{normalized}%", limit * 2))  # Fetch extra for re-sorting

    results = cursor.fetchall()
    conn.close()

    # Convert to result objects with display names
    club_results = []
    for row in results:
        name = row['name']
        is_national = bool(row['is_national_team'])
        display_name = format_national_team_name(name) if is_national else name

        club_results.append({
            'id': row['id'],
            'name': name,
            'display_name': display_name,
            'is_national_team': is_national,
            'player_count': row['player_count'],
            'priority': get_national_team_priority(name) if is_national else 50
        })

    # Sort: national teams by priority first, then non-national by player count
    # This puts senior national teams at top when searching for country names
    club_results.sort(key=lambda x: (x['priority'], -x['player_count']))

    # Return limited results
    return [
        ClubSearchResult(
            id=r['id'],
            name=r['name'],
            display_name=r['display_name'],
            is_national_team=r['is_national_team']
        )
        for r in club_results[:limit]
    ]


@router.get("/{club_id}/roster", response_model=RosterResponse)
async def get_club_roster(
    club_id: int,
    season: str = Query(..., description="Season year, e.g., '2023' for 2023/24 season")
):
    """
    Get the roster for a club in a specific season.

    A player is considered part of the roster if they were at the club
    during the specified season (start_date <= season end AND end_date >= season start OR end_date is NULL).

    For a season like "2023" (meaning 2023/24), we check:
    - Player joined before or during 2024 (start_year <= 2024)
    - Player left after or during 2023 OR is still at club (end_year >= 2023 OR end_year IS NULL)
    """
    conn = get_db_connection()
    cursor = conn.cursor()

    # Get club info
    cursor.execute("SELECT id, name FROM clubs WHERE id = ?", (club_id,))
    club_row = cursor.fetchone()

    if not club_row:
        conn.close()
        return RosterResponse(
            club_id=club_id,
            club_name="Unknown Club",
            display_name="Unknown Club",
            season=season,
            players=[],
            total_count=0
        )

    # Parse season year
    try:
        season_start = int(season)
        season_end = season_start + 1
    except ValueError:
        season_start = 2024
        season_end = 2025

    # Get players who were at this club during the season
    # A player was at the club if:
    # - They have a valid start_date (not NULL, not corrupted)
    # - Their start_date year <= season_end (they joined before or during the season)
    # - Their end_date year >= season_start OR end_date is NULL (they left after the season started or are still there)
    #
    # Data quality heuristic: For players with NULL end_date, only include them if:
    # - They started within the last 10 years (reasonable tenure assumption)
    # - This prevents showing players from decades ago with missing departure data
    #
    # We use a subquery to get unique players and their most relevant stint dates.
    max_tenure_years = 10  # Players without end_date must have started within this many years
    oldest_valid_start = season_start - max_tenure_years

    cursor.execute("""
        WITH valid_stints AS (
            SELECT
                pc.player_id,
                CAST(SUBSTR(pc.start_date, 1, 4) AS INTEGER) as start_year,
                CASE
                    WHEN pc.end_date IS NULL THEN NULL
                    WHEN pc.end_date LIKE '%http%' THEN NULL
                    WHEN LENGTH(pc.end_date) < 4 THEN NULL
                    ELSE CAST(SUBSTR(pc.end_date, 1, 4) AS INTEGER)
                END as end_year
            FROM player_clubs pc
            WHERE pc.club_id = ?
              AND pc.start_date IS NOT NULL
              AND pc.start_date NOT LIKE '%http%'
              AND LENGTH(pc.start_date) >= 4
              AND CAST(SUBSTR(pc.start_date, 1, 4) AS INTEGER) <= ?
              AND (
                  -- Has a valid end_date that's >= season_start
                  (pc.end_date IS NOT NULL
                   AND pc.end_date NOT LIKE '%http%'
                   AND LENGTH(pc.end_date) >= 4
                   AND CAST(SUBSTR(pc.end_date, 1, 4) AS INTEGER) >= ?)
                  OR
                  -- Has NULL/invalid end_date AND started within max_tenure_years
                  ((pc.end_date IS NULL OR pc.end_date LIKE '%http%' OR LENGTH(pc.end_date) < 4)
                   AND CAST(SUBSTR(pc.start_date, 1, 4) AS INTEGER) >= ?)
              )
        ),
        best_stint AS (
            SELECT
                player_id,
                MAX(start_year) as start_year,
                -- For end_year, prefer NULL (still at club) over a date
                MIN(COALESCE(end_year, 9999)) as end_year_raw
            FROM valid_stints
            GROUP BY player_id
        )
        SELECT
            p.id, p.name, p.position,
            bs.start_year,
            CASE WHEN bs.end_year_raw = 9999 THEN NULL ELSE bs.end_year_raw END as end_year
        FROM best_stint bs
        JOIN players p ON bs.player_id = p.id
        ORDER BY p.name
    """, (club_id, season_end, season_start, oldest_valid_start))

    player_rows = cursor.fetchall()
    conn.close()

    players = [
        RosterPlayer(
            id=row['id'],
            name=row['name'],
            position=row['position'],
            start_year=row['start_year'],
            end_year=row['end_year']
        )
        for row in player_rows
    ]

    # Format display name (short version for national teams)
    club_name = club_row['name']
    display_name = format_national_team_name(club_name)

    return RosterResponse(
        club_id=club_row['id'],
        club_name=club_name,
        display_name=display_name,
        season=f"{season_start}/{str(season_end)[-2:]}",
        players=players,
        total_count=len(players)
    )


@router.get("/{club_id}/years")
async def get_club_years(club_id: int):
    """
    Get the range of years a club has player data for.
    Useful for populating the season selector.
    """
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            MIN(CAST(SUBSTR(pc.start_date, 1, 4) AS INTEGER)) as min_year,
            MAX(CASE
                WHEN pc.end_date IS NULL THEN CAST(strftime('%Y', 'now') AS INTEGER)
                ELSE CAST(SUBSTR(pc.end_date, 1, 4) AS INTEGER)
            END) as max_year
        FROM player_clubs pc
        WHERE pc.club_id = ?
          AND pc.start_date IS NOT NULL
    """, (club_id,))

    row = cursor.fetchone()
    conn.close()

    if row and row['min_year']:
        return {
            "club_id": club_id,
            "min_year": row['min_year'],
            "max_year": row['max_year'] or 2025
        }

    return {
        "club_id": club_id,
        "min_year": 2000,
        "max_year": 2025
    }
