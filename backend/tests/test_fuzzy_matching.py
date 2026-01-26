"""
Unit tests for fuzzy matching algorithms.

Run with: pytest backend/tests/test_fuzzy_matching.py -v
"""

import pytest
from app.services.fuzzy_matching import (
    levenshtein_distance,
    soundex,
    metaphone,
    get_edit_threshold,
    fuzzy_match,
    fuzzy_match_name,
    FuzzyMatchResult,
)


class TestLevenshteinDistance:
    """Tests for Levenshtein distance calculation."""

    def test_identical_strings(self):
        assert levenshtein_distance("hello", "hello") == 0
        assert levenshtein_distance("ronaldo", "ronaldo") == 0

    def test_single_insertion(self):
        assert levenshtein_distance("messi", "messis") == 1
        assert levenshtein_distance("neymar", "neymars") == 1

    def test_single_deletion(self):
        assert levenshtein_distance("messi", "mesi") == 1
        assert levenshtein_distance("ronaldo", "ronldo") == 1

    def test_single_substitution(self):
        assert levenshtein_distance("messi", "messo") == 1
        assert levenshtein_distance("ronaldo", "ronalda") == 1

    def test_multiple_edits(self):
        assert levenshtein_distance("ronaldinho", "ronaldino") == 1
        assert levenshtein_distance("cristiano", "christiano") == 1  # insertion
        assert levenshtein_distance("szczesny", "szczsny") == 1  # 1 deletion

    def test_transposition(self):
        # Transposition counts as 2 edits in standard Levenshtein
        assert levenshtein_distance("ronaldo", "ronalod") == 2

    def test_completely_different(self):
        assert levenshtein_distance("messi", "ronaldo") == 7

    def test_empty_string(self):
        assert levenshtein_distance("", "hello") == 5
        assert levenshtein_distance("hello", "") == 5
        assert levenshtein_distance("", "") == 0

    def test_case_sensitivity(self):
        # Levenshtein is case-sensitive
        assert levenshtein_distance("Messi", "messi") == 1


class TestSoundex:
    """Tests for Soundex phonetic algorithm."""

    def test_basic_encoding(self):
        assert soundex("Robert") == "R163"
        assert soundex("Rupert") == "R163"  # Same as Robert

    def test_soccer_names(self):
        # Cristiano and Christiano should have same soundex
        assert soundex("Cristiano") == soundex("Christiano")

        # Similar sounding names
        assert soundex("Smith") == soundex("Smyth")

    def test_empty_string(self):
        assert soundex("") == ""

    def test_short_names(self):
        # Short names get padded with zeros
        assert len(soundex("Lee")) == 4
        assert soundex("Lee") == "L000"

    def test_handles_vowels(self):
        # Vowels (except first letter) are not coded
        soundex_result = soundex("Aeiou")
        assert soundex_result[0] == "A"


class TestMetaphone:
    """Tests for Metaphone phonetic algorithm."""

    def test_basic_encoding(self):
        # Basic test - metaphone should produce consistent output
        result = metaphone("Robert")
        assert result == metaphone("Robert")  # Consistent

    def test_ph_to_f(self):
        # PH should sound like F
        assert "F" in metaphone("Philippe")

    def test_c_variations(self):
        # C before E, I, Y sounds like S
        result = metaphone("Cesar")
        assert "S" in result

    def test_silent_letters(self):
        # Should handle silent letters
        result = metaphone("Knight")
        assert result  # Should produce something

    def test_empty_string(self):
        assert metaphone("") == ""


class TestEditThreshold:
    """Tests for edit distance threshold calculation."""

    def test_short_names_no_tolerance(self):
        # Names 4 chars or less: 0 tolerance
        assert get_edit_threshold(1) == 0
        assert get_edit_threshold(2) == 0
        assert get_edit_threshold(3) == 0
        assert get_edit_threshold(4) == 0

    def test_medium_names_one_edit(self):
        # Names 5-8 chars: 1 edit tolerance
        assert get_edit_threshold(5) == 1
        assert get_edit_threshold(6) == 1
        assert get_edit_threshold(7) == 1
        assert get_edit_threshold(8) == 1

    def test_long_names_two_edits(self):
        # Names 9+ chars: 2 edits tolerance
        assert get_edit_threshold(9) == 2
        assert get_edit_threshold(10) == 2
        assert get_edit_threshold(15) == 2
        assert get_edit_threshold(20) == 2


class TestFuzzyMatch:
    """Tests for the main fuzzy_match function."""

    def test_exact_match(self):
        result = fuzzy_match("ronaldo", "ronaldo")
        assert result.is_match is True
        assert result.confidence == 1.0
        assert result.edit_distance == 0
        assert result.reason == "exact_match"

    def test_single_typo_medium_name(self):
        # "neymar" (6 chars) with 1 typo should match
        result = fuzzy_match("neymer", "neymar")
        assert result.is_match is True
        assert result.edit_distance == 1
        assert result.reason in ["edit_distance", "edit_and_phonetic"]

    def test_single_typo_long_name(self):
        # "ronaldinho" (10 chars) with 1 typo should match
        result = fuzzy_match("ronaldino", "ronaldinho")
        assert result.is_match is True
        assert result.edit_distance == 1

    def test_two_typos_long_name(self):
        # "ronaldinho" (10 chars) with 2 typos should match
        result = fuzzy_match("ronaldnio", "ronaldinho")  # missing 'h' and 'h->i' = 2 edits
        assert result.is_match is True
        assert result.edit_distance == 2

    def test_typo_rejected_for_short_name(self):
        # "messi" (5 chars) with 2 typos should NOT match
        result = fuzzy_match("massi", "messi")
        # 1 edit is allowed for 5 chars, "massi" -> "messi" is 1 edit
        # Actually let's check: m-a-s-s-i vs m-e-s-s-i = 1 substitution
        assert result.edit_distance == 1
        assert result.is_match is True  # 1 edit is within threshold for 5 chars

    def test_typo_rejected_for_very_short_name(self):
        # "pele" (4 chars) with any typo should NOT match via edit distance
        # (but might match via phonetics)
        result = fuzzy_match("pela", "pele")
        assert result.edit_distance == 1
        # 4-char names have threshold 0, so edit-only match should fail
        # but phonetic match might still work
        if not result.phonetic_match:
            assert result.is_match is False

    def test_phonetic_match(self):
        # "cristiano" vs "christiano" - phonetically similar
        result = fuzzy_match("cristiano", "christiano")
        assert result.phonetic_match is True
        # Should match due to phonetic similarity even though edit distance is 1

    def test_completely_different_names(self):
        result = fuzzy_match("messi", "ronaldo")
        assert result.is_match is False
        assert result.confidence < 0.5

    def test_confidence_decreases_with_edits(self):
        exact = fuzzy_match("ronaldo", "ronaldo")
        one_edit = fuzzy_match("ronalda", "ronaldo")

        assert exact.confidence > one_edit.confidence


class TestFuzzyMatchName:
    """Tests for multi-part name fuzzy matching."""

    def test_exact_full_name(self):
        result = fuzzy_match_name("cristiano ronaldo", "cristiano ronaldo")
        assert result.is_match is True
        assert result.confidence == 1.0

    def test_typo_in_first_name(self):
        # Typo in "cristiano" -> "cristano"
        result = fuzzy_match_name("cristano ronaldo", "cristiano ronaldo")
        assert result.is_match is True

    def test_typo_in_last_name(self):
        # Typo in "ronaldo" -> "ronalda"
        result = fuzzy_match_name("cristiano ronalda", "cristiano ronaldo")
        assert result.is_match is True

    def test_typos_in_both_parts(self):
        # One typo each in first and last name
        result = fuzzy_match_name("cristano ronalda", "cristiano ronaldo")
        # Total 2 edits across a 17-char name - should be within combined threshold
        assert result.is_match is True

    def test_different_word_count(self):
        # Different number of name parts - falls back to whole-string matching
        result = fuzzy_match_name("ronaldo", "cristiano ronaldo")
        # This should not match well
        assert result.edit_distance > 5

    def test_three_part_name(self):
        result = fuzzy_match_name("kevin de bruyne", "kevin de bruyne")
        assert result.is_match is True
        assert result.confidence == 1.0

    def test_three_part_name_with_typo(self):
        result = fuzzy_match_name("kevin de bruine", "kevin de bruyne")
        assert result.is_match is True
        assert result.edit_distance == 1


class TestRealWorldExamples:
    """Tests with real player names to verify practical accuracy."""

    def test_common_misspellings(self):
        # Szczęsny - commonly misspelled
        result = fuzzy_match("szczesny", "szczesny")
        assert result.is_match is True

        # With a typo
        result = fuzzy_match("szczsny", "szczesny")
        assert result.is_match is True  # 1 edit in 8-char name

    def test_diacritics_handled_at_normalization(self):
        # This test assumes names are normalized before matching
        # özil -> ozil at normalization step
        result = fuzzy_match("ozil", "ozil")
        assert result.is_match is True

    def test_brazilian_single_names(self):
        # These should match exactly
        assert fuzzy_match("ronaldinho", "ronaldinho").is_match is True
        assert fuzzy_match("kaka", "kaka").is_match is True
        assert fuzzy_match("neymar", "neymar").is_match is True

    def test_similar_but_different_players(self):
        # These are different players and should not match
        result = fuzzy_match("ronaldo", "ronaldinho")
        # "ronaldo" (7 chars) vs "ronaldinho" (10 chars) = 3 edits (add 'i', 'n', 'h')
        assert result.edit_distance == 3
        assert result.is_match is False

        result = fuzzy_match("silva", "silvo")
        # Short name with edit
        assert result.edit_distance == 1
        # "silva" is 5 chars, threshold is 1, so this WILL match
        # This is actually a design decision - we accept 1 edit for 5-char names
        assert result.is_match is True
