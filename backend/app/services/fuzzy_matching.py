"""
Fuzzy matching algorithms for player name matching.

This module provides algorithms for matching player names with tolerance for:
- Typos (via Levenshtein distance)
- Phonetic variations (via Soundex/Metaphone)
- Diacritics and transliteration differences

Key principle: Accept close matches silently without revealing answers.
"""

from dataclasses import dataclass
from typing import Optional


@dataclass
class FuzzyMatchResult:
    """Result of a fuzzy match comparison."""
    is_match: bool
    confidence: float  # 0.0 to 1.0
    edit_distance: int
    phonetic_match: bool
    reason: str


def levenshtein_distance(s1: str, s2: str) -> int:
    """
    Calculate the Levenshtein (edit) distance between two strings.

    This is the minimum number of single-character edits (insertions,
    deletions, or substitutions) required to change one string into the other.

    Examples:
        levenshtein_distance("ronaldo", "ronalod") -> 2 (transposition = 2 edits)
        levenshtein_distance("messi", "mesi") -> 1 (deletion)
        levenshtein_distance("neymar", "neymar") -> 0 (identical)
    """
    if len(s1) < len(s2):
        s1, s2 = s2, s1

    if len(s2) == 0:
        return len(s1)

    previous_row = range(len(s2) + 1)

    for i, c1 in enumerate(s1):
        current_row = [i + 1]
        for j, c2 in enumerate(s2):
            # Cost is 0 if characters match, 1 otherwise
            insertions = previous_row[j + 1] + 1
            deletions = current_row[j] + 1
            substitutions = previous_row[j] + (c1 != c2)
            current_row.append(min(insertions, deletions, substitutions))
        previous_row = current_row

    return previous_row[-1]


def soundex(name: str) -> str:
    """
    Generate the Soundex code for a name.

    Soundex is a phonetic algorithm that indexes names by sound as pronounced
    in English. Names that sound similar will have the same Soundex code.

    Examples:
        soundex("Robert") -> "R163"
        soundex("Rupert") -> "R163"
        soundex("Cristiano") -> "C623"
        soundex("Christiano") -> "C623"
    """
    if not name:
        return ""

    # Convert to uppercase
    name = name.upper()

    # Keep first letter
    first_letter = name[0]

    # Soundex coding
    codes = {
        'B': '1', 'F': '1', 'P': '1', 'V': '1',
        'C': '2', 'G': '2', 'J': '2', 'K': '2', 'Q': '2', 'S': '2', 'X': '2', 'Z': '2',
        'D': '3', 'T': '3',
        'L': '4',
        'M': '5', 'N': '5',
        'R': '6',
    }

    # Encode the rest
    encoded = first_letter
    prev_code = codes.get(first_letter, '0')

    for char in name[1:]:
        code = codes.get(char, '0')
        if code != '0' and code != prev_code:
            encoded += code
        prev_code = code if code != '0' else prev_code

    # Pad with zeros or truncate to 4 characters
    encoded = (encoded + '000')[:4]

    return encoded


def metaphone(name: str) -> str:
    """
    Generate the Metaphone code for a name.

    Metaphone is a more sophisticated phonetic algorithm than Soundex,
    better handling various English language inconsistencies.

    This is a simplified implementation covering common cases.
    """
    if not name:
        return ""

    name = name.upper()

    # Common substitutions for phonetic similarity
    result = []
    i = 0

    while i < len(name):
        char = name[i]
        next_char = name[i + 1] if i + 1 < len(name) else ''

        # Skip duplicate adjacent letters
        if char == next_char and char not in 'CC':
            i += 1
            continue

        # Handle special cases
        if char == 'C':
            if next_char in 'EIY':
                result.append('S')
            elif next_char == 'H':
                result.append('X')
                i += 1
            else:
                result.append('K')
        elif char == 'G':
            if next_char in 'EIY':
                result.append('J')
            else:
                result.append('K')
        elif char == 'P' and next_char == 'H':
            result.append('F')
            i += 1
        elif char == 'Q':
            result.append('K')
        elif char == 'S' and next_char == 'H':
            result.append('X')
            i += 1
        elif char == 'X':
            result.append('KS')
        elif char == 'Z':
            result.append('S')
        elif char == 'W':
            if next_char in 'AEIOU':
                result.append('W')
        elif char == 'Y':
            if next_char in 'AEIOU':
                result.append('Y')
        elif char in 'AEIOU':
            if i == 0:
                result.append(char)
        elif char.isalpha():
            result.append(char)

        i += 1

    return ''.join(result)


def get_edit_threshold(name_length: int) -> int:
    """
    Get the allowed edit distance threshold based on name length.

    Longer names get more tolerance for typos:
    - 1-4 characters: 0 edits (must be exact - too short for fuzzy)
    - 5-8 characters: 1 edit allowed
    - 9+ characters: 2 edits allowed

    This prevents "Messi" from matching "Maser" while allowing
    "Ronaldinho" to match "Ronaldino".
    """
    if name_length <= 4:
        return 0
    elif name_length <= 8:
        return 1
    else:
        return 2


def fuzzy_match(query: str, target: str, use_phonetics: bool = True) -> FuzzyMatchResult:
    """
    Determine if a query string is a fuzzy match for a target string.

    Uses both edit distance and phonetic matching to determine if the
    query is "close enough" to the target.

    Args:
        query: The user's input (normalized)
        target: The database value to compare against (normalized)
        use_phonetics: Whether to also check phonetic similarity

    Returns:
        FuzzyMatchResult with match status and details
    """
    # Exact match is always a match
    if query == target:
        return FuzzyMatchResult(
            is_match=True,
            confidence=1.0,
            edit_distance=0,
            phonetic_match=True,
            reason="exact_match"
        )

    # Calculate edit distance
    edit_dist = levenshtein_distance(query, target)

    # Use the SHORTER string's length for threshold to be conservative
    # This prevents "ronaldo" from matching "ronaldinho"
    min_length = min(len(query), len(target))
    threshold = get_edit_threshold(min_length)

    # Check phonetic similarity
    phonetic_match = False
    if use_phonetics:
        query_soundex = soundex(query)
        target_soundex = soundex(target)
        query_metaphone = metaphone(query)
        target_metaphone = metaphone(target)

        phonetic_match = (
            (query_soundex == target_soundex and query_soundex != "") or
            (query_metaphone == target_metaphone and query_metaphone != "")
        )

    # Determine if it's a match
    is_edit_match = edit_dist <= threshold and edit_dist > 0

    # Calculate confidence
    if edit_dist == 0:
        confidence = 1.0
    else:
        # Confidence decreases with edit distance relative to length
        max_length = max(len(query), len(target))
        confidence = max(0.0, 1.0 - (edit_dist / max_length))

    # Check length ratio - don't rely on phonetics alone if lengths differ too much
    # This prevents "ronaldo" (7) from matching "ronaldinho" (10)
    length_ratio = min_length / max(len(query), len(target))
    phonetics_reliable = length_ratio >= 0.8  # Lengths must be within 20%

    # Match if either edit distance is within threshold OR phonetic match with:
    # - reasonable edit distance AND similar lengths
    is_match = is_edit_match or (
        phonetic_match and
        phonetics_reliable and
        edit_dist <= threshold + 1
    )

    reason = "no_match"
    if is_match:
        if is_edit_match and phonetic_match:
            reason = "edit_and_phonetic"
        elif is_edit_match:
            reason = "edit_distance"
        elif phonetic_match:
            reason = "phonetic"

    return FuzzyMatchResult(
        is_match=is_match,
        confidence=confidence,
        edit_distance=edit_dist,
        phonetic_match=phonetic_match,
        reason=reason
    )


def fuzzy_match_name(query: str, target: str) -> FuzzyMatchResult:
    """
    Fuzzy match specifically for player names, handling multi-part names.

    For names with multiple parts (e.g., "Cristiano Ronaldo"), we match
    each part and combine the results.
    """
    query_parts = query.split()
    target_parts = target.split()

    # If different number of parts, do whole-string matching
    if len(query_parts) != len(target_parts):
        return fuzzy_match(query, target)

    # Match each part
    total_edit_dist = 0
    all_phonetic = True

    for q_part, t_part in zip(query_parts, target_parts):
        part_result = fuzzy_match(q_part, t_part)
        total_edit_dist += part_result.edit_distance
        all_phonetic = all_phonetic and part_result.phonetic_match

    # Use the sum of thresholds for multi-part names
    total_threshold = sum(get_edit_threshold(len(p)) for p in target_parts)

    is_match = total_edit_dist <= total_threshold or (all_phonetic and total_edit_dist <= total_threshold + 1)

    # Calculate combined confidence
    max_length = max(len(query), len(target))
    confidence = max(0.0, 1.0 - (total_edit_dist / max_length))

    reason = "no_match"
    if is_match:
        if total_edit_dist <= total_threshold and all_phonetic:
            reason = "edit_and_phonetic"
        elif total_edit_dist <= total_threshold:
            reason = "edit_distance"
        elif all_phonetic:
            reason = "phonetic"

    return FuzzyMatchResult(
        is_match=is_match,
        confidence=confidence,
        edit_distance=total_edit_dist,
        phonetic_match=all_phonetic,
        reason=reason
    )
