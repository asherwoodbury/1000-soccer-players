"""
Player matching service.

This module provides a clean interface for matching player name queries
against the database, with support for:
- Fuzzy matching (typo tolerance)
- Name validation (first + last name requirements)
- Mononym detection (single-name players like Ronaldinho)
- Ambiguity resolution (multiple players with similar names)

Key principle: Reward knowing the player (typo tolerance) without
giving away answers (no autocomplete suggestions).
"""

import unicodedata
import re
from dataclasses import dataclass
from enum import Enum
from typing import Optional
import sqlite3

from app.services.fuzzy_matching import fuzzy_match_name, FuzzyMatchResult


class MatchStatus(Enum):
    """Status of a player match attempt."""
    EXACT_MATCH = "exact_match"
    FUZZY_MATCH = "fuzzy_match"
    AMBIGUOUS = "ambiguous"
    NOT_FOUND = "not_found"
    NEED_FULL_NAME = "need_full_name"


@dataclass
class PlayerData:
    """Basic player data from the database."""
    id: int
    wikidata_id: str
    name: str
    normalized_name: str
    first_name: Optional[str]
    last_name: Optional[str]
    nationality: Optional[str]
    position: Optional[str]
    is_mononym: bool = False  # Will be used once DB schema is updated


@dataclass
class MatchCandidate:
    """A potential match for a player query."""
    player: PlayerData
    match_result: FuzzyMatchResult
    score: float  # Combined score for ranking


@dataclass
class PlayerMatchResult:
    """Result of a player matching operation."""
    status: MatchStatus
    player: Optional[PlayerData]
    candidates: list[MatchCandidate]  # For disambiguation
    message: str


class PlayerMatcher:
    """
    Service for matching player name queries against the database.

    This class encapsulates all the logic for:
    - Normalizing input names
    - Validating name format (first + last requirement)
    - Detecting mononyms
    - Finding exact and fuzzy matches
    - Handling ambiguous results

    Usage:
        matcher = PlayerMatcher(db_connection)
        result = matcher.match("Cristano Ronaldo")  # typo in Cristiano

        if result.status == MatchStatus.EXACT_MATCH:
            # Found the player
            print(result.player.name)
        elif result.status == MatchStatus.AMBIGUOUS:
            # Multiple players match - show disambiguation UI
            for candidate in result.candidates:
                print(f"{candidate.player.name} ({candidate.player.nationality})")
    """

    def __init__(self, conn: sqlite3.Connection):
        """
        Initialize the PlayerMatcher with a database connection.

        Args:
            conn: SQLite connection with row_factory set to sqlite3.Row
        """
        self.conn = conn

    @staticmethod
    def normalize_name(name: str) -> str:
        """
        Normalize a name for matching.

        - Convert to lowercase
        - Remove diacritics/accents
        - Collapse multiple spaces
        """
        normalized = unicodedata.normalize('NFKD', name)
        normalized = ''.join(c for c in normalized if not unicodedata.combining(c))
        normalized = normalized.lower().strip()
        normalized = re.sub(r'\s+', ' ', normalized)
        return normalized

    @staticmethod
    def validate_name_format(name: str) -> tuple[bool, str]:
        """
        Validate that a name meets the format requirements.

        Returns:
            Tuple of (is_valid, message)
        """
        parts = name.strip().split()

        if len(parts) == 0:
            return False, "Please enter a player name."

        if len(parts) == 1:
            # Single name - might be valid for mononyms, but we check that later
            return True, "single_name"

        return True, "full_name"

    @staticmethod
    def is_single_name_query(name: str) -> bool:
        """Check if the query is a single name (no spaces)."""
        return len(name.strip().split()) == 1

    def _fetch_exact_matches(self, normalized: str) -> list[PlayerData]:
        """Fetch players with exact normalized name match."""
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT id, wikidata_id, name, normalized_name, first_name, last_name,
                   nationality, position
            FROM players
            WHERE normalized_name = ?
        """, (normalized,))

        return [self._row_to_player(row) for row in cursor.fetchall()]

    def _fetch_prefix_matches(self, normalized: str, limit: int = 20) -> list[PlayerData]:
        """Fetch players whose normalized name starts with the query."""
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT id, wikidata_id, name, normalized_name, first_name, last_name,
                   nationality, position
            FROM players
            WHERE normalized_name LIKE ?
            LIMIT ?
        """, (normalized + "%", limit))

        return [self._row_to_player(row) for row in cursor.fetchall()]

    def _fetch_fuzzy_candidates(self, normalized: str, limit: int = 100) -> list[PlayerData]:
        """
        Fetch potential fuzzy match candidates.

        This uses a prefix-based approach to limit candidates, then applies
        fuzzy matching. For better performance in production, consider using
        SQLite FTS5 or a dedicated search index.
        """
        cursor = self.conn.cursor()

        # Get candidates that share the first few characters
        # This is a heuristic to limit the search space
        prefix_len = min(3, len(normalized))
        prefix = normalized[:prefix_len]

        cursor.execute("""
            SELECT id, wikidata_id, name, normalized_name, first_name, last_name,
                   nationality, position
            FROM players
            WHERE normalized_name LIKE ?
            LIMIT ?
        """, (prefix + "%", limit))

        return [self._row_to_player(row) for row in cursor.fetchall()]

    def _row_to_player(self, row: sqlite3.Row) -> PlayerData:
        """Convert a database row to a PlayerData object."""
        # Determine if this is a mononym based on first_name being NULL
        # This is a heuristic until we add the is_mononym column
        is_mononym = row['first_name'] is None and row['last_name'] is not None

        return PlayerData(
            id=row['id'],
            wikidata_id=row['wikidata_id'],
            name=row['name'],
            normalized_name=row['normalized_name'],
            first_name=row['first_name'],
            last_name=row['last_name'],
            nationality=row['nationality'],
            position=row['position'],
            is_mononym=is_mononym
        )

    def _deduplicate_players(self, players: list[PlayerData]) -> list[PlayerData]:
        """
        Deduplicate players, keeping unique (name, nationality) combinations.

        Some players may appear multiple times due to data issues.
        """
        seen = set()
        unique = []
        for player in players:
            key = (player.name, player.nationality)
            if key not in seen:
                seen.add(key)
                unique.append(player)
        return unique

    def _find_best_fuzzy_match(
        self,
        normalized: str,
        candidates: list[PlayerData]
    ) -> list[MatchCandidate]:
        """
        Find the best fuzzy matches from a list of candidates.

        Returns candidates sorted by match score (best first).
        """
        matches = []

        for player in candidates:
            result = fuzzy_match_name(normalized, player.normalized_name)

            if result.is_match:
                # Calculate combined score (confidence + exact bonus)
                score = result.confidence
                if result.edit_distance == 0:
                    score += 0.5  # Bonus for exact match

                matches.append(MatchCandidate(
                    player=player,
                    match_result=result,
                    score=score
                ))

        # Sort by score (highest first)
        matches.sort(key=lambda m: m.score, reverse=True)

        return matches

    def match(self, query: str) -> PlayerMatchResult:
        """
        Match a player name query against the database.

        This is the main entry point for player matching.

        Args:
            query: The player name to search for

        Returns:
            PlayerMatchResult with status, matched player (if any), and message
        """
        # Validate input
        is_valid, format_type = self.validate_name_format(query)
        if not is_valid:
            return PlayerMatchResult(
                status=MatchStatus.NOT_FOUND,
                player=None,
                candidates=[],
                message=format_type  # Error message
            )

        normalized = self.normalize_name(query)
        is_single_name = self.is_single_name_query(query)

        # Step 1: Try exact match
        exact_matches = self._fetch_exact_matches(normalized)
        exact_matches = self._deduplicate_players(exact_matches)

        if len(exact_matches) == 1:
            player = exact_matches[0]

            # Check if single-name query is valid for this player
            if is_single_name and not player.is_mononym:
                return PlayerMatchResult(
                    status=MatchStatus.NEED_FULL_NAME,
                    player=None,
                    candidates=[],
                    message="Please enter the player's first and last name."
                )

            return PlayerMatchResult(
                status=MatchStatus.EXACT_MATCH,
                player=player,
                candidates=[],
                message="Player found!"
            )

        if len(exact_matches) > 1:
            # Multiple exact matches - ambiguous
            candidates = [
                MatchCandidate(
                    player=p,
                    match_result=FuzzyMatchResult(
                        is_match=True,
                        confidence=1.0,
                        edit_distance=0,
                        phonetic_match=True,
                        reason="exact_match"
                    ),
                    score=1.0
                )
                for p in exact_matches
            ]

            return PlayerMatchResult(
                status=MatchStatus.AMBIGUOUS,
                player=None,
                candidates=candidates,
                message=f"Found {len(exact_matches)} players with this name. Please be more specific."
            )

        # Step 2: Try prefix match
        prefix_matches = self._fetch_prefix_matches(normalized)
        prefix_matches = self._deduplicate_players(prefix_matches)

        if len(prefix_matches) == 1:
            player = prefix_matches[0]

            if is_single_name and not player.is_mononym:
                return PlayerMatchResult(
                    status=MatchStatus.NEED_FULL_NAME,
                    player=None,
                    candidates=[],
                    message="Please enter the player's first and last name."
                )

            return PlayerMatchResult(
                status=MatchStatus.EXACT_MATCH,
                player=player,
                candidates=[],
                message="Player found!"
            )

        if len(prefix_matches) > 1:
            candidates = self._find_best_fuzzy_match(normalized, prefix_matches)
            if candidates:
                return PlayerMatchResult(
                    status=MatchStatus.AMBIGUOUS,
                    player=None,
                    candidates=candidates,
                    message=f"Found {len(candidates)} players with similar names. Please be more specific."
                )

        # Step 3: Try fuzzy matching
        fuzzy_candidates = self._fetch_fuzzy_candidates(normalized)
        fuzzy_candidates = self._deduplicate_players(fuzzy_candidates)
        matches = self._find_best_fuzzy_match(normalized, fuzzy_candidates)

        if len(matches) == 0:
            return PlayerMatchResult(
                status=MatchStatus.NOT_FOUND,
                player=None,
                candidates=[],
                message="Player not found. Check the spelling and try again."
            )

        if len(matches) == 1:
            candidate = matches[0]
            player = candidate.player

            if is_single_name and not player.is_mononym:
                return PlayerMatchResult(
                    status=MatchStatus.NEED_FULL_NAME,
                    player=None,
                    candidates=[],
                    message="Please enter the player's first and last name."
                )

            return PlayerMatchResult(
                status=MatchStatus.FUZZY_MATCH,
                player=player,
                candidates=[],
                message="Player found!"
            )

        # Multiple fuzzy matches - ambiguous
        return PlayerMatchResult(
            status=MatchStatus.AMBIGUOUS,
            player=None,
            candidates=matches,
            message=f"Found {len(matches)} players with similar names. Please be more specific."
        )

    def match_with_disambiguation(
        self,
        query: str,
        nationality: Optional[str] = None,
        position: Optional[str] = None
    ) -> PlayerMatchResult:
        """
        Match a player with optional disambiguation hints.

        Use this when the user has provided additional context to narrow
        down an ambiguous match.

        Args:
            query: The player name to search for
            nationality: Optional nationality to filter by
            position: Optional position to filter by

        Returns:
            PlayerMatchResult with status, matched player (if any), and message
        """
        result = self.match(query)

        if result.status != MatchStatus.AMBIGUOUS:
            return result

        # Filter candidates by provided hints
        filtered = result.candidates

        if nationality:
            norm_nat = self.normalize_name(nationality)
            filtered = [
                c for c in filtered
                if c.player.nationality and norm_nat in self.normalize_name(c.player.nationality)
            ]

        if position:
            norm_pos = self.normalize_name(position)
            filtered = [
                c for c in filtered
                if c.player.position and norm_pos in self.normalize_name(c.player.position)
            ]

        if len(filtered) == 0:
            return PlayerMatchResult(
                status=MatchStatus.NOT_FOUND,
                player=None,
                candidates=[],
                message="No players match those criteria."
            )

        if len(filtered) == 1:
            return PlayerMatchResult(
                status=MatchStatus.FUZZY_MATCH if result.candidates[0].match_result.edit_distance > 0 else MatchStatus.EXACT_MATCH,
                player=filtered[0].player,
                candidates=[],
                message="Player found!"
            )

        return PlayerMatchResult(
            status=MatchStatus.AMBIGUOUS,
            player=None,
            candidates=filtered,
            message=f"Still found {len(filtered)} matching players. Please be more specific."
        )
