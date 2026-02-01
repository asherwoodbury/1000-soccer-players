import Foundation

/// Formats national team names for display
enum NationalTeamFormatter {
    /// Convert long national team names to short display format
    ///
    /// Examples:
    /// - "Argentina men's national association football team" -> "Argentina (M)"
    /// - "Germany women's national football team" -> "Germany (W)"
    /// - "Brazil national under-20 football team" -> "Brazil U20"
    /// - "France national under-23 football team" -> "France U23 (M)"
    static func format(_ name: String) -> String {
        let lowercased = name.lowercased()

        // Check if this looks like a national team name
        guard lowercased.contains("national") else {
            return name
        }

        // Determine gender
        let isWomen = lowercased.contains("women")
        let genderSuffix = isWomen ? " (W)" : " (M)"

        // Check for youth age groups
        var youthSuffix = ""
        if let match = lowercased.range(of: "under-(\\d+)", options: .regularExpression) {
            let ageRange = lowercased[match]
            if let dashIndex = ageRange.firstIndex(of: "-") {
                let age = String(ageRange[ageRange.index(after: dashIndex)...])
                youthSuffix = " U\(age)"
            }
        }

        // Extract country name
        var country: String?

        // Pattern: "Country men's national..." or "Country women's national..."
        if let menRange = lowercased.range(of: "\\s+men's\\s+national", options: .regularExpression) {
            country = String(name[..<menRange.lowerBound]).trimmingCharacters(in: .whitespaces)
        } else if let womenRange = lowercased.range(of: "\\s+women's\\s+national", options: .regularExpression) {
            country = String(name[..<womenRange.lowerBound]).trimmingCharacters(in: .whitespaces)
        } else if let nationalRange = lowercased.range(of: "\\s+national", options: .regularExpression) {
            // Pattern: "Country national under-XX..." or "Country national..."
            country = String(name[..<nationalRange.lowerBound]).trimmingCharacters(in: .whitespaces)
        }

        guard let countryName = country, !countryName.isEmpty else {
            return name
        }

        // Build short name
        if !youthSuffix.isEmpty {
            return "\(countryName)\(youthSuffix)\(genderSuffix)"
        } else {
            return "\(countryName)\(genderSuffix)"
        }
    }

    /// Return a priority score for sorting national teams
    /// Lower score = higher priority (appears first)
    ///
    /// Priority order:
    /// 1. Senior men's teams (score 0)
    /// 2. Senior women's teams (score 1)
    /// 3. Youth teams by age descending (U23 before U21 before U20, etc.)
    static func priority(for name: String) -> Int {
        let lowercased = name.lowercased()

        // Check if this is a national team
        guard lowercased.contains("national") else {
            return 100 // Non-national teams go last
        }

        // Check for youth age group
        if let match = lowercased.range(of: "under-(\\d+)", options: .regularExpression) {
            let ageRange = lowercased[match]
            if let dashIndex = ageRange.firstIndex(of: "-"),
               let age = Int(ageRange[ageRange.index(after: dashIndex)...]) {
                // Youth teams get score 10-29 based on age
                var baseScore = 10 + (30 - age)
                // Women's youth teams slightly lower priority
                if lowercased.contains("women") {
                    baseScore += 1
                }
                return baseScore
            }
        }

        // Senior teams
        if lowercased.contains("women") {
            return 1 // Senior women's
        }
        return 0 // Senior men's
    }
}
