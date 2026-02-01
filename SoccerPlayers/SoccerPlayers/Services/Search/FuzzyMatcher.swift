import Foundation

/// Fuzzy matching algorithms for player name matching
enum FuzzyMatcher {
    /// Calculate the Levenshtein (edit) distance between two strings
    ///
    /// This is the minimum number of single-character edits (insertions,
    /// deletions, or substitutions) required to change one string into the other.
    static func levenshteinDistance(_ s1: String, _ s2: String) -> Int {
        let str1 = Array(s1)
        let str2 = Array(s2)

        if str1.count < str2.count {
            return levenshteinDistance(s2, s1)
        }

        if str2.isEmpty {
            return str1.count
        }

        var previousRow = Array(0...str2.count)

        for (i, c1) in str1.enumerated() {
            var currentRow = [i + 1]

            for (j, c2) in str2.enumerated() {
                let insertions = previousRow[j + 1] + 1
                let deletions = currentRow[j] + 1
                let substitutions = previousRow[j] + (c1 != c2 ? 1 : 0)
                currentRow.append(min(insertions, deletions, substitutions))
            }

            previousRow = currentRow
        }

        return previousRow.last!
    }

    /// Generate the Soundex code for a name
    ///
    /// Soundex is a phonetic algorithm that indexes names by sound.
    /// Names that sound similar will have the same Soundex code.
    static func soundex(_ name: String) -> String {
        guard !name.isEmpty else { return "" }

        let uppercased = name.uppercased()
        guard let firstLetter = uppercased.first else { return "" }

        let codes: [Character: Character] = [
            "B": "1", "F": "1", "P": "1", "V": "1",
            "C": "2", "G": "2", "J": "2", "K": "2", "Q": "2", "S": "2", "X": "2", "Z": "2",
            "D": "3", "T": "3",
            "L": "4",
            "M": "5", "N": "5",
            "R": "6"
        ]

        var encoded = String(firstLetter)
        var prevCode = codes[firstLetter] ?? "0"

        for char in uppercased.dropFirst() {
            let code = codes[char] ?? "0"
            if code != "0" && code != prevCode {
                encoded.append(code)
            }
            if code != "0" {
                prevCode = code
            }
        }

        // Pad with zeros or truncate to 4 characters
        while encoded.count < 4 {
            encoded.append("0")
        }
        return String(encoded.prefix(4))
    }

    /// Get the allowed edit distance threshold based on name length
    static func getEditThreshold(nameLength: Int) -> Int {
        if nameLength <= 4 {
            return 0
        } else if nameLength <= 8 {
            return 1
        } else {
            return 2
        }
    }

    /// Generate prefix variations to catch common typos
    ///
    /// Generates shorter prefixes, character deletions, adjacent swaps,
    /// and vowel substitutions for fuzzy matching.
    static func generatePrefixVariations(word: String, maxLen: Int = 5) -> Set<String> {
        var variations = Set<String>()
        let prefix = word.count >= maxLen ? String(word.prefix(maxLen)) : word
        let chars = Array(prefix)

        // Original prefix and shorter versions
        for i in 2...chars.count {
            variations.insert(String(word.prefix(i)))
        }

        // Try removing each character (catches insertions like "chr" -> "cr")
        for i in 0..<chars.count {
            var variant = chars
            variant.remove(at: i)
            if variant.count >= 2 {
                variations.insert(String(variant))
            }
        }

        // Try swapping adjacent characters (catches transpositions like "salha" -> "salah")
        for i in 0..<(chars.count - 1) {
            var variant = chars
            variant.swapAt(i, i + 1)
            if variant.count >= 2 {
                variations.insert(String(variant.prefix(maxLen)))
            }
        }

        // Try common vowel substitutions
        let vowelSwaps: [Character: Character] = [
            "a": "e", "e": "a", "i": "e", "o": "u", "u": "o", "y": "i"
        ]
        for (i, char) in chars.enumerated() {
            if let swapped = vowelSwaps[char] {
                var variant = chars
                variant[i] = swapped
                if variant.count >= 2 {
                    variations.insert(String(variant))
                }
            }
        }

        return variations
    }

    /// Result of a fuzzy match comparison
    struct MatchResult {
        let isMatch: Bool
        let confidence: Double
        let editDistance: Int
        let phoneticMatch: Bool
        let reason: String
    }

    /// Determine if a query string is a fuzzy match for a target string
    static func fuzzyMatch(query: String, target: String, usePhonetics: Bool = true) -> MatchResult {
        // Exact match
        if query == target {
            return MatchResult(
                isMatch: true,
                confidence: 1.0,
                editDistance: 0,
                phoneticMatch: true,
                reason: "exact_match"
            )
        }

        // Calculate edit distance
        let editDist = levenshteinDistance(query, target)

        // Use the shorter string's length for threshold
        let minLength = min(query.count, target.count)
        let threshold = getEditThreshold(nameLength: minLength)

        // Check phonetic similarity
        var phoneticMatch = false
        if usePhonetics {
            let querySoundex = soundex(query)
            let targetSoundex = soundex(target)
            phoneticMatch = !querySoundex.isEmpty && querySoundex == targetSoundex
        }

        // Determine if it's a match
        let isEditMatch = editDist <= threshold && editDist > 0

        // Calculate confidence
        let confidence: Double
        if editDist == 0 {
            confidence = 1.0
        } else {
            let maxLength = max(query.count, target.count)
            confidence = max(0.0, 1.0 - (Double(editDist) / Double(maxLength)))
        }

        // Check length ratio for phonetic matching reliability
        let lengthRatio = Double(minLength) / Double(max(query.count, target.count))
        let phoneticsReliable = lengthRatio >= 0.8

        let isMatch = isEditMatch || (
            phoneticMatch &&
            phoneticsReliable &&
            editDist <= threshold + 1
        )

        var reason = "no_match"
        if isMatch {
            if isEditMatch && phoneticMatch {
                reason = "edit_and_phonetic"
            } else if isEditMatch {
                reason = "edit_distance"
            } else if phoneticMatch {
                reason = "phonetic"
            }
        }

        return MatchResult(
            isMatch: isMatch,
            confidence: confidence,
            editDistance: editDist,
            phoneticMatch: phoneticMatch,
            reason: reason
        )
    }
}
