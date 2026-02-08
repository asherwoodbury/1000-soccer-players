#!/usr/bin/env python3
"""
Merge football-data.org data into players.db.

Updates player-club associations with accurate recent squad data from
football-data.org. Marks stale club links and adds missing ones.

Usage:
    python3 backend/scripts/merge_footballdata.py
"""

import json
import re
import sqlite3
import unicodedata
from pathlib import Path

GAME_DB_PATH = Path(__file__).parent.parent / "data" / "players.db"
FD_DB_PATH = Path(__file__).parent.parent / "data" / "footballdata.db"

# Bootstrap mapping: FD team name -> Wikidata club name (for names that
# don't match after normalization + suffix stripping). Only needed for
# clubs where the names genuinely differ, not just punctuation.
BOOTSTRAP_ALIASES = {
    "FC Bayern München": "FC Bayern Munich",
    "FC Internazionale Milano": "Inter Milan",
    "Club Atlético de Madrid": "Atlético de Madrid",
    "SSC Napoli": "SSC Napoli",
    "Juventus FC": "Juventus FC",
    "SS Lazio": "S.S. Lazio",
    "Torino FC": "Torino F.C.",
    "Genoa CFC": "Genoa CFC",
    "Hellas Verona FC": "Hellas Verona F.C.",
    "Bologna FC 1909": "Bologna F.C. 1909",
    "US Lecce": "U.S. Lecce",
    "US Salernitana 1919": "U.S. Salernitana 1919",
    "US Sassuolo Calcio": "U.S. Sassuolo Calcio",
    "US Cremonese": "U.S. Cremonese",
    "Empoli FC": "Empoli F.C.",
    "Udinese Calcio": "Udinese Calcio",
    "ACF Fiorentina": "ACF Fiorentina",
    "AC Monza": "A.C. Monza",
    "Frosinone Calcio": "Frosinone Calcio",
    "Cagliari Calcio": "Cagliari Calcio",
    "Parma Calcio 1913": "Parma Calcio 1913",
    "Venezia FC": "Venezia F.C.",
    "Como 1907": "Como 1907",
    # Spain
    "Real Madrid CF": "Real Madrid CF",
    "FC Barcelona": "Futbol Club Barcelona",
    "Real Sociedad de Fútbol": "Real Sociedad",
    "Real Betis Balompié": "Real Betis",
    "Athletic Club": "Athletic Bilbao",
    "Sevilla FC": "Sevilla FC",
    "Villarreal CF": "Villarreal CF",
    "Valencia CF": "Valencia CF",
    "Cádiz CF": "Cádiz Club de Fútbol",
    "RCD Mallorca": "RCD Mallorca",
    "Real Valladolid CF": "Real Valladolid CF",
    "Rayo Vallecano de Madrid": "Rayo Vallecano",
    "CA Osasuna": "Club Atlético Osasuna",
    "RC Celta de Vigo": "RC Celta de Vigo",
    "RCD Espanyol de Barcelona": "RCD Espanyol",
    "Getafe CF": "Getafe CF",
    "Deportivo Alavés": "Deportivo Alavés",
    "Granada CF": "Granada CF",
    "Girona FC": "Girona FC",
    "UD Almería": "Unión Deportiva Almería",
    "UD Las Palmas": "UD Las Palmas",
    "CD Leganés": "CD Leganés",
    "Levante UD": "Levante UD",
    # Germany
    "Borussia Dortmund": "Borussia Dortmund",
    "Bayer 04 Leverkusen": "Bayer 04 Leverkusen",
    "RB Leipzig": "RB Leipzig",
    "Borussia Mönchengladbach": "Borussia Mönchengladbach",
    "Eintracht Frankfurt": "Eintracht Frankfurt",
    "VfL Wolfsburg": "VfL Wolfsburg",
    "VfB Stuttgart": "VfB Stuttgart",
    "SC Freiburg": "SC Freiburg",
    "TSG 1899 Hoffenheim": "TSG 1899 Hoffenheim",
    "1. FC Köln": "1. FC Köln",
    "1. FC Union Berlin": "1. FC Union Berlin",
    "1. FSV Mainz 05": "1. FSV Mainz 05",
    "FC Augsburg": "FC Augsburg",
    "SV Werder Bremen": "Werder Bremen",
    "VfL Bochum 1848": "VfL Bochum",
    "SV Darmstadt 98": "SV Darmstadt 98",
    "FC St. Pauli 1910": "FC St. Pauli",
    "1. FC Heidenheim 1846": "1. FC Heidenheim",
    "Holstein Kiel": "Holstein Kiel",
    # France
    "Paris Saint-Germain FC": "Paris Saint-Germain FC",
    "Olympique de Marseille": "Olympique de Marseille",
    "Olympique Lyonnais": "Olympique Lyonnais",
    "AS Monaco FC": "AS Monaco FC",
    "Lille OSC": "Lille OSC",
    "Stade Rennais FC 1901": "Stade Rennais F.C.",
    "OGC Nice": "OGC Nice",
    "RC Strasbourg Alsace": "RC Strasbourg Alsace",
    "FC Nantes": "FC Nantes",
    "Montpellier HSC": "Montpellier HSC",
    "Stade Brestois 29": "Stade Brestois 29",
    "Toulouse FC": "Toulouse FC",
    "Stade de Reims": "Stade de Reims",
    "FC Lorient": "FC Lorient",
    "Clermont Foot 63": "Clermont Foot",
    "FC Metz": "FC Metz",
    "Racing Club de Lens": "RC Lens",
    "Le Havre AC": "Le Havre AC",
    "AJ Auxerre": "AJ Auxerre",
    "AS Saint-Étienne": "AS Saint-Étienne",
    "Angers SCO": "Angers SCO",
    # Netherlands
    "AFC Ajax": "AFC Ajax",
    "PSV": "PSV Eindhoven",
    "Feyenoord Rotterdam": "Feyenoord",
    "AZ": "AZ Alkmaar",
    "FC Twente '65": "FC Twente",
    "FC Utrecht": "FC Utrecht",
    "SC Heerenveen": "SC Heerenveen",
    "FC Groningen": "FC Groningen",
    "SBV Vitesse": "SBV Vitesse",
    "Willem II Tilburg": "Willem II (football club)",
    "Sparta Rotterdam": "Sparta Rotterdam",
    "Go Ahead Eagles": "Go Ahead Eagles",
    "NAC Breda": "NAC Breda",
    "NEC": "N.E.C.",
    "RKC Waalwijk": "RKC Waalwijk",
    "PEC Zwolle": "PEC Zwolle",
    "Almere City FC": "Almere City FC",
    "Heracles Almelo": "Heracles Almelo",
    "SBV Excelsior": "Excelsior Rotterdam",
    "FC Volendam": "FC Volendam",
    "Fortuna Sittard": "Fortuna Sittard",
    # England
    "Arsenal FC": "Arsenal F.C.",
    "Chelsea FC": "Chelsea F.C.",
    "Liverpool FC": "Liverpool F.C.",
    "Manchester City FC": "Manchester City F.C.",
    "Manchester United FC": "Manchester United F.C.",
    "Tottenham Hotspur FC": "Tottenham Hotspur F.C.",
    "Newcastle United FC": "Newcastle United F.C.",
    "West Ham United FC": "West Ham United F.C.",
    "Aston Villa FC": "Aston Villa F.C.",
    "AFC Bournemouth": "AFC Bournemouth",
    "Brighton & Hove Albion FC": "Brighton & Hove Albion F.C.",
    "Crystal Palace FC": "Crystal Palace F.C.",
    "Brentford FC": "Brentford F.C.",
    "Fulham FC": "Fulham F.C.",
    "Wolverhampton Wanderers FC": "Wolverhampton Wanderers F.C.",
    "Everton FC": "Everton F.C.",
    "Nottingham Forest FC": "Nottingham Forest F.C.",
    "Burnley FC": "Burnley F.C.",
    "Sheffield United FC": "Sheffield United F.C.",
    "Luton Town FC": "Luton Town F.C.",
    "Leicester City FC": "Leicester City F.C.",
    "Ipswich Town FC": "Ipswich Town F.C.",
    "Southampton FC": "Southampton F.C.",
    # Championship
    "Leeds United FC": "Leeds United F.C.",
    "Norwich City FC": "Norwich City F.C.",
    "Sunderland AFC": "Sunderland A.F.C.",
    "Middlesbrough FC": "Middlesbrough F.C.",
    "Coventry City FC": "Coventry City F.C.",
    "Hull City AFC": "Hull City A.F.C.",
    "Stoke City FC": "Stoke City F.C.",
    "Swansea City AFC": "Swansea City A.F.C.",
    "Millwall FC": "Millwall F.C.",
    "Cardiff City FC": "Cardiff City F.C.",
    "Watford FC": "Watford F.C.",
    "Blackburn Rovers FC": "Blackburn Rovers F.C.",
    "Birmingham City FC": "Birmingham City F.C.",
    "Queens Park Rangers FC": "Queens Park Rangers",
    "Huddersfield Town AFC": "Huddersfield Town A.F.C.",
    "Rotherham United FC": "Rotherham United F.C.",
    "Plymouth Argyle FC": "Plymouth Argyle F.C.",
    "Preston North End FC": "Preston North End F.C.",
    "Bristol City FC": "Bristol City F.C.",
    "Sheffield Wednesday FC": "Sheffield Wednesday F.C.",
    "Derby County FC": "Derby County F.C.",
    "West Bromwich Albion FC": "West Bromwich Albion F.C.",
    "Oxford United FC": "Oxford United F.C.",
    "Wrexham AFC": "Wrexham A.F.C.",
    "Charlton Athletic FC": "Charlton Athletic F.C.",
    "Portsmouth FC": "Portsmouth F.C.",
    # Portugal
    "FC Porto": "FC Porto",
    "Sporting Clube de Portugal": "Sporting CP",
    "Sport Lisboa e Benfica": "S.L. Benfica",
    "Sporting Clube de Braga": "S.C. Braga",
    "Moreirense FC": "Moreirense F.C.",
    "Boavista FC": "Boavista F.C.",
    "FC Arouca": "F.C. Arouca",
    "Rio Ave FC": "Rio Ave F.C.",
    "Vitória SC": "Vitória de Guimarães",
    "Gil Vicente FC": "Gil Vicente F.C.",
    "GD Estoril Praia": "G.D. Estoril Praia",
    "FC Famalicão": "F.C. Famalicão",
    "GD Chaves": "G.D. Chaves",
    "SC Farense": "S.C. Farense",
    "Casa Pia AC": "Casa Pia A.C.",
    "CD Nacional": "C.D. Nacional",
    "CD Santa Clara": "C.D. Santa Clara",
    "Portimonense SC": "Portimonense S.C.",
    "CF Estrela da Amadora": "C.F. Estrela da Amadora",
    "FC Vizela": "F.C. Vizela",
    # Brazil
    "CR Flamengo": "Clube de Regatas do Flamengo",
    "SE Palmeiras": "Sociedade Esportiva Palmeiras",
    "São Paulo FC": "São Paulo FC",
    "SC Corinthians Paulista": "S.C. Corinthians Paulista",
    "Fluminense FC": "Fluminense FC",
    "Grêmio FBPA": "Grêmio",
    "SC Recife": "Sport Club do Recife",
    "SC Internacional": "S.C. Internacional",
    "Cruzeiro EC": "Cruzeiro E.C.",
    "CA Mineiro": "Clube Atlético Mineiro",
    "Santos FC": "Santos FC",
    "Botafogo FR": "Botafogo de Futebol e Regatas",
    "Fortaleza EC": "Fortaleza E.C.",
    "EC Bahia": "Esporte Clube Bahia",
    "CA Paranaense": "Club Athletico Paranaense",
    "CR Vasco da Gama": "CR Vasco da Gama",
    "RB Bragantino": "Red Bull Bragantino",
    "Goiás EC": "Goiás Esporte Clube",
    "Cuiabá EC": "Cuiabá Esporte Clube",
    "Coritiba FBC": "Coritiba F.C.",
    "América FC": "América Futebol Clube",
    "Ceará SC": "Ceará Sporting Club",
    "AC Goianiense": "Atlético Clube Goianiense",
    "EC Juventude": "Esporte Clube Juventude",
    # Additional matches found during testing
    "Telstar 1963": "SC Telstar",
    "FC Alverca": "F.C. Alverca",
    "EC Vitória": "E.C. Vitória",
    "Criciúma EC": "Criciúma Esporte Clube",
    "Mirassol FC": "Mirassol Futebol Clube",
    # UCL / other European
    "BSC Young Boys": "BSC Young Boys",
    "Celtic FC": "Celtic F.C.",
    "Galatasaray SK": "Galatasaray S.K. (football)",
    "GNK Dinamo Zagreb": "GNK Dinamo Zagreb",
    "FK Shakhtar Donetsk": "FC Shakhtar Donetsk",
    "FK Crvena Zvezda": "FK Crvena Zvezda",
    "FC København": "F.C. Copenhagen",
    "FC Red Bull Salzburg": "FC Red Bull Salzburg",
    "PAE Olympiakos SFP": "Olympiacos F.C.",
    "AC Sparta Praha": "AC Sparta Prague",
    "SK Slavia Praha": "SK Slavia Prague",
    "SK Sturm Graz": "SK Sturm Graz",
    "FK Bodø/Glimt": "FK Bodø/Glimt",
    "Royal Antwerp FC": "Royal Antwerp F.C.",
    "Club Brugge KV": "Club Brugge K.V.",
    "Royale Union Saint-Gilloise": "Royale Union Saint-Gilloise",
    "ŠK Slovan Bratislava": "ŠK Slovan Bratislava",
    "Qarabağ Ağdam FK": "Qarabağ FK",
    "Real Oviedo": "Real Oviedo",
    "AC Pisa 1909": "Pisa S.C.",
    "Hamburger SV": "Hamburger SV",

}

# National teams in footballdata.db - these are teams with country names
# We skip national teams since our game DB handles them differently
NATIONAL_TEAMS = {
    "Albania", "Austria", "Belgium", "Croatia", "Czechia", "Denmark",
    "England", "France", "Georgia", "Germany", "Hungary", "Italy",
    "Netherlands", "Poland", "Portugal", "Romania", "Scotland",
    "Serbia", "Slovakia", "Slovenia", "Spain", "Switzerland",
    "Turkey", "Ukraine",
}


def normalize_name(name: str) -> str:
    """Normalize a name for matching (lowercase, no diacritics)."""
    normalized = unicodedata.normalize('NFKD', name)
    normalized = ''.join(c for c in normalized if not unicodedata.combining(c))
    normalized = normalized.lower().strip()
    normalized = re.sub(r'\s+', ' ', normalized)
    return normalized


def strip_club_suffixes(name: str) -> str:
    """Strip common club suffixes for fuzzy matching."""
    # Remove trailing suffixes like FC, AFC, F.C., A.F.C., SC, etc.
    suffixes = [
        r'\s+f\.?c\.?$', r'\s+a\.?f\.?c\.?$', r'\s+s\.?c\.?$',
        r'\s+cf$', r'\s+ac$', r'\s+fk$', r'\s+sk$',
        r'\s+\(football club\)$', r'\s+\(football\)$',
    ]
    result = name
    for suffix in suffixes:
        result = re.sub(suffix, '', result, flags=re.IGNORECASE)
    return result.strip()


def build_person_team_seasons(fd_conn: sqlite3.Connection) -> dict[int, list[tuple[int, int]]]:
    """
    Build person -> [(team_id, season), ...] mapping from cached API responses.

    The footballdata.db stores squad data embedded in team API responses.
    We re-parse these to extract person-team-season links.
    """
    person_teams: dict[int, list[tuple[int, int]]] = {}

    rows = fd_conn.execute(
        "SELECT response_json FROM api_responses "
        "WHERE endpoint LIKE '%/teams' AND http_status = 200"
    ).fetchall()

    for (raw_json,) in rows:
        data = json.loads(raw_json)
        season_info = data.get("season", {})
        season_start = season_info.get("startDate", "")[:4]
        if not season_start:
            continue
        season = int(season_start)

        for team in data.get("teams", []):
            team_id = team.get("id")
            if not team_id:
                continue
            for player in team.get("squad", []):
                pid = player.get("id")
                if not pid:
                    continue
                person_teams.setdefault(pid, []).append((team_id, season))

    return person_teams


def step1_schema_migration(game_conn: sqlite3.Connection):
    """Add is_stale column and club_aliases table if not present."""
    cursor = game_conn.cursor()

    # Add is_stale column
    try:
        cursor.execute("ALTER TABLE player_clubs ADD COLUMN is_stale BOOLEAN DEFAULT 0")
        print("  Added is_stale column to player_clubs")
    except sqlite3.OperationalError:
        print("  is_stale column already exists")

    # Create club_aliases table
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

    # Populate initial aliases from existing clubs (source='wikidata')
    existing = cursor.execute("SELECT COUNT(*) FROM club_aliases WHERE source = 'wikidata'").fetchone()[0]
    if existing == 0:
        cursor.execute("""
            INSERT OR IGNORE INTO club_aliases (club_id, name, normalized_name, source, external_id)
            SELECT id, name, normalized_name, 'wikidata', wikidata_id FROM clubs
        """)
        inserted = cursor.rowcount
        print(f"  Populated {inserted} wikidata aliases from clubs table")
    else:
        print(f"  Wikidata aliases already populated ({existing} entries)")

    game_conn.commit()


def step2_match_clubs(game_conn: sqlite3.Connection, fd_conn: sqlite3.Connection) -> dict[int, int]:
    """
    Match FD teams to game DB clubs. Returns fd_team_id -> game_club_id mapping.
    """
    print("\n=== Step 2: Match clubs ===")

    game_cursor = game_conn.cursor()

    # Build lookup: normalized_name -> club_id from club_aliases
    alias_rows = game_cursor.execute(
        "SELECT club_id, normalized_name FROM club_aliases"
    ).fetchall()
    alias_lookup: dict[str, int] = {}
    for club_id, norm_name in alias_rows:
        alias_lookup[norm_name] = club_id

    # Also build stripped-name lookup
    stripped_lookup: dict[str, int] = {}
    for norm_name, club_id in alias_lookup.items():
        stripped = strip_club_suffixes(norm_name)
        if stripped not in stripped_lookup:
            stripped_lookup[stripped] = club_id

    # Load FD teams
    fd_teams = fd_conn.execute("SELECT id, name FROM teams").fetchall()

    fd_to_game: dict[int, int] = {}
    matched = 0
    unmatched = []
    skipped_national = 0

    for fd_id, fd_name in fd_teams:
        # Skip national teams
        if fd_name in NATIONAL_TEAMS:
            skipped_national += 1
            continue

        fd_normalized = normalize_name(fd_name)

        # Try 1: exact normalized match in aliases
        if fd_normalized in alias_lookup:
            fd_to_game[fd_id] = alias_lookup[fd_normalized]
            matched += 1
            _insert_fd_alias(game_cursor, alias_lookup[fd_normalized], fd_name, fd_normalized, fd_id)
            continue

        # Try 2: stripped suffix match
        fd_stripped = strip_club_suffixes(fd_normalized)
        if fd_stripped in stripped_lookup:
            fd_to_game[fd_id] = stripped_lookup[fd_stripped]
            matched += 1
            _insert_fd_alias(game_cursor, stripped_lookup[fd_stripped], fd_name, fd_normalized, fd_id)
            continue

        # Try 3: bootstrap alias mapping
        if fd_name in BOOTSTRAP_ALIASES:
            target_name = BOOTSTRAP_ALIASES[fd_name]
            target_normalized = normalize_name(target_name)
            if target_normalized in alias_lookup:
                fd_to_game[fd_id] = alias_lookup[target_normalized]
                matched += 1
                _insert_fd_alias(game_cursor, alias_lookup[target_normalized], fd_name, fd_normalized, fd_id)
                continue
            # Also try stripped
            target_stripped = strip_club_suffixes(target_normalized)
            if target_stripped in stripped_lookup:
                fd_to_game[fd_id] = stripped_lookup[target_stripped]
                matched += 1
                _insert_fd_alias(game_cursor, stripped_lookup[target_stripped], fd_name, fd_normalized, fd_id)
                continue

        unmatched.append((fd_id, fd_name))

    game_conn.commit()

    print(f"  Matched: {matched} clubs")
    print(f"  Skipped national teams: {skipped_national}")
    print(f"  Unmatched: {len(unmatched)} clubs")
    if unmatched:
        for fd_id, fd_name in unmatched[:20]:
            print(f"    - [{fd_id}] {fd_name}")
        if len(unmatched) > 20:
            print(f"    ... and {len(unmatched) - 20} more")

    return fd_to_game


def _insert_fd_alias(cursor, club_id: int, fd_name: str, fd_normalized: str, fd_id: int):
    """Insert a footballdata alias for a club."""
    try:
        cursor.execute(
            "INSERT OR IGNORE INTO club_aliases (club_id, name, normalized_name, source, external_id) "
            "VALUES (?, ?, ?, 'footballdata', ?)",
            (club_id, fd_name, fd_normalized, str(fd_id))
        )
    except sqlite3.IntegrityError:
        pass


def step3_match_players(
    game_conn: sqlite3.Connection, fd_conn: sqlite3.Connection
) -> dict[int, int]:
    """
    Match FD persons to game DB players. Returns fd_person_id -> game_player_id mapping.
    """
    print("\n=== Step 3: Match players ===")

    # Build game DB lookup: normalized_name -> [(player_id, birth_date), ...]
    game_cursor = game_conn.cursor()
    game_rows = game_cursor.execute(
        "SELECT id, normalized_name, birth_date FROM players"
    ).fetchall()

    game_name_lookup: dict[str, list[tuple[int, str | None]]] = {}
    for pid, norm_name, birth_date in game_rows:
        game_name_lookup.setdefault(norm_name, []).append((pid, birth_date))

    # Load FD persons
    fd_persons = fd_conn.execute(
        "SELECT id, name, date_of_birth FROM persons"
    ).fetchall()

    fd_to_game: dict[int, int] = {}
    matched_unique = 0
    matched_dob = 0
    ambiguous = 0
    unmatched = 0

    for fd_id, fd_name, fd_dob in fd_persons:
        if not fd_name:
            unmatched += 1
            continue

        fd_normalized = normalize_name(fd_name)
        candidates = game_name_lookup.get(fd_normalized, [])

        if len(candidates) == 1:
            fd_to_game[fd_id] = candidates[0][0]
            matched_unique += 1
        elif len(candidates) > 1:
            # Try to disambiguate by DOB
            if fd_dob:
                dob_matches = [
                    (pid, bd) for pid, bd in candidates
                    if bd and bd == fd_dob
                ]
                if len(dob_matches) == 1:
                    fd_to_game[fd_id] = dob_matches[0][0]
                    matched_dob += 1
                else:
                    ambiguous += 1
            else:
                ambiguous += 1
        else:
            unmatched += 1

    print(f"  FD persons: {len(fd_persons)}")
    print(f"  Matched (unique name): {matched_unique}")
    print(f"  Matched (DOB disambig): {matched_dob}")
    print(f"  Ambiguous (skipped): {ambiguous}")
    print(f"  Unmatched (skipped): {unmatched}")

    return fd_to_game


def step4_update_associations(
    game_conn: sqlite3.Connection,
    fd_conn: sqlite3.Connection,
    fd_player_map: dict[int, int],
    fd_club_map: dict[int, int],
):
    """
    Update player-club associations based on FD squad data.

    For each matched player:
    - Add missing club links from FD data
    - Mark stale links (game DB has club with no end date, FD shows different club)
    """
    print("\n=== Step 4: Update player-club associations ===")

    # Build person -> [(team_id, season)] from FD cached responses
    person_team_seasons = build_person_team_seasons(fd_conn)

    game_cursor = game_conn.cursor()

    added = 0
    stale_marked = 0
    end_dates_set = 0
    already_present = 0
    skipped_no_club = 0
    players_processed = 0

    for fd_person_id, game_player_id in fd_player_map.items():
        fd_memberships = person_team_seasons.get(fd_person_id, [])
        if not fd_memberships:
            continue

        players_processed += 1

        # Get the set of game club IDs this player is at according to FD
        fd_game_clubs: dict[int, list[int]] = {}  # game_club_id -> [seasons]
        for fd_team_id, season in fd_memberships:
            game_club_id = fd_club_map.get(fd_team_id)
            if game_club_id:
                fd_game_clubs.setdefault(game_club_id, []).append(season)
            else:
                skipped_no_club += 1

        if not fd_game_clubs:
            continue

        # Get current game DB club history for this player
        existing_rows = game_cursor.execute(
            "SELECT id, club_id, start_date, end_date, is_national_team, is_stale "
            "FROM player_clubs WHERE player_id = ?",
            (game_player_id,)
        ).fetchall()

        existing_club_ids = {row[1] for row in existing_rows}

        # Add missing club links
        for game_club_id, seasons in fd_game_clubs.items():
            if game_club_id in existing_club_ids:
                already_present += 1
                continue

            # Insert one player-club link using the earliest season
            earliest_season = min(set(seasons))
            start_date = f"{earliest_season}-08-01"
            try:
                game_cursor.execute(
                    "INSERT OR IGNORE INTO player_clubs "
                    "(player_id, club_id, start_date, end_date, is_national_team, is_stale) "
                    "VALUES (?, ?, ?, NULL, 0, 0)",
                    (game_player_id, game_club_id, start_date)
                )
                if game_cursor.rowcount > 0:
                    added += 1
            except sqlite3.IntegrityError:
                pass

        # Handle existing clubs not in FD data (player moved on):
        # - If the record has a start_date, we can infer an end_date from when
        #   the earliest FD club started (e.g. Anderlecht 2020-? → 2020-2023)
        # - If the record has no start_date, mark as stale (truly unclear)
        earliest_fd_season = min(s for seasons in fd_game_clubs.values() for s in seasons)
        earliest_fd_date = f"{earliest_fd_season}-08-01"

        for row in existing_rows:
            pc_id, club_id, start_date, end_date, is_national_team, is_stale = row
            if is_national_team or is_stale or end_date is not None:
                continue
            if club_id not in fd_game_clubs:
                if start_date:
                    # Has a start date — set end_date to when the FD era begins
                    game_cursor.execute(
                        "UPDATE player_clubs SET end_date = ? WHERE id = ?",
                        (earliest_fd_date, pc_id)
                    )
                    end_dates_set += 1
                else:
                    # No start date — truly stale/unclear
                    game_cursor.execute(
                        "UPDATE player_clubs SET is_stale = 1 WHERE id = ?",
                        (pc_id,)
                    )
                    stale_marked += 1

        # Infer end dates from sequential transfers within FD data.
        # If a player was at Club A in seasons [2023,2024] and Club B in [2025],
        # Club A's end_date should be set to when Club B started.
        if len(fd_game_clubs) > 1:
            # Build timeline: [(earliest_season, latest_season, club_id)]
            club_timeline = []
            for game_club_id, seasons in fd_game_clubs.items():
                club_timeline.append((min(seasons), max(seasons), game_club_id))
            club_timeline.sort(key=lambda x: x[0])

            for i in range(len(club_timeline) - 1):
                curr_start, curr_end, curr_club_id = club_timeline[i]
                next_start, _, _ = club_timeline[i + 1]

                # Only set end date if the next club started in a later season
                if next_start > curr_end:
                    end_date = f"{next_start}-08-01"
                    game_cursor.execute(
                        "UPDATE player_clubs SET end_date = ? "
                        "WHERE player_id = ? AND club_id = ? AND end_date IS NULL "
                        "AND is_stale = 0",
                        (end_date, game_player_id, curr_club_id)
                    )
                    if game_cursor.rowcount > 0:
                        end_dates_set += 1

    game_conn.commit()

    print(f"  Players processed: {players_processed}")
    print(f"  New club links added: {added}")
    print(f"  Stale links marked: {stale_marked}")
    print(f"  End dates inferred: {end_dates_set}")
    print(f"  Already present: {already_present}")
    print(f"  Skipped (no club match): {skipped_no_club}")


def main():
    print("=== Merging football-data.org data into players.db ===\n")

    if not GAME_DB_PATH.exists():
        print(f"Error: Game DB not found at {GAME_DB_PATH}")
        return
    if not FD_DB_PATH.exists():
        print(f"Error: Football-data DB not found at {FD_DB_PATH}")
        return

    game_conn = sqlite3.connect(str(GAME_DB_PATH))
    game_conn.row_factory = sqlite3.Row
    fd_conn = sqlite3.connect(str(FD_DB_PATH))
    fd_conn.row_factory = sqlite3.Row

    print("=== Step 1: Schema migration ===")
    step1_schema_migration(game_conn)

    fd_club_map = step2_match_clubs(game_conn, fd_conn)

    fd_player_map = step3_match_players(game_conn, fd_conn)

    step4_update_associations(game_conn, fd_conn, fd_player_map, fd_club_map)

    # Print summary stats
    cursor = game_conn.cursor()
    alias_count = cursor.execute("SELECT COUNT(*) FROM club_aliases").fetchone()[0]
    fd_alias_count = cursor.execute(
        "SELECT COUNT(*) FROM club_aliases WHERE source = 'footballdata'"
    ).fetchone()[0]
    stale_count = cursor.execute(
        "SELECT COUNT(*) FROM player_clubs WHERE is_stale = 1"
    ).fetchone()[0]

    print(f"\n=== Summary ===")
    print(f"  Total club aliases: {alias_count}")
    print(f"  Football-data aliases: {fd_alias_count}")
    print(f"  Stale player-club records: {stale_count}")

    game_conn.close()
    fd_conn.close()
    print("\nDone.")


if __name__ == "__main__":
    main()
