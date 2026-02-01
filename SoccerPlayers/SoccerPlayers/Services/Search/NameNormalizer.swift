import Foundation

/// Normalizes player names for matching
enum NameNormalizer {
    /// Normalize a name by removing diacritics, lowercasing, and collapsing whitespace
    ///
    /// Example: "Lionél Messi" -> "lionel messi"
    static func normalize(_ name: String) -> String {
        // Unicode NFKD decomposition separates base characters from combining marks
        let decomposed = name.decomposedStringWithCompatibilityMapping

        // Remove combining diacritical marks (accents, umlauts, etc.)
        let withoutDiacritics = decomposed.unicodeScalars.filter { scalar in
            !CharacterSet.nonBaseCharacters.contains(scalar)
        }

        // Convert back to String and normalize
        let result = String(String.UnicodeScalarView(withoutDiacritics))
            .lowercased()
            .trimmingCharacters(in: .whitespaces)

        // Collapse multiple whitespace into single spaces
        let components = result.components(separatedBy: .whitespaces)
            .filter { !$0.isEmpty }
        return components.joined(separator: " ")
    }
}

extension CharacterSet {
    /// Characters that modify other characters (combining diacritical marks)
    static let nonBaseCharacters: CharacterSet = {
        var set = CharacterSet()
        // Combining Diacritical Marks: U+0300 to U+036F
        set.insert(charactersIn: Unicode.Scalar(0x0300)!...Unicode.Scalar(0x036F)!)
        // Combining Diacritical Marks Extended: U+1AB0 to U+1AFF
        set.insert(charactersIn: Unicode.Scalar(0x1AB0)!...Unicode.Scalar(0x1AFF)!)
        // Combining Diacritical Marks Supplement: U+1DC0 to U+1DFF
        set.insert(charactersIn: Unicode.Scalar(0x1DC0)!...Unicode.Scalar(0x1DFF)!)
        // Combining Diacritical Marks for Symbols: U+20D0 to U+20FF
        set.insert(charactersIn: Unicode.Scalar(0x20D0)!...Unicode.Scalar(0x20FF)!)
        // Combining Half Marks: U+FE20 to U+FE2F
        set.insert(charactersIn: Unicode.Scalar(0xFE20)!...Unicode.Scalar(0xFE2F)!)
        return set
    }()
}
