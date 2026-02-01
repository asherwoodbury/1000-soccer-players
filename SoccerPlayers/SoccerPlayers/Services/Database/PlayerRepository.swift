import Foundation
import GRDB

/// Repository for player database operations
final class PlayerRepository {
    private let dbPool: DatabasePool

    init(dbPool: DatabasePool) {
        self.dbPool = dbPool
    }

    /// Look up a player by name with exact, prefix, FTS, and fuzzy matching
    func lookupPlayer(name: String) async throws -> PlayerLookupResult {
        let normalized = NameNormalizer.normalize(name)
        let words = normalized.split(separator: " ").map(String.init)

        // Require both first and last name, unless it's a known mononym
        if words.count < 2 && !Constants.knownMononyms.contains(normalized) {
            return .needsFullName
        }

        // Try exact normalized match first
        var players = try await exactMatch(normalized: normalized)

        // Try prefix match
        if players.isEmpty {
            players = try await prefixMatch(normalized: normalized)
        }

        // Try FTS5 search
        if players.isEmpty {
            players = try await ftsSearch(query: normalized)
        }

        // Track if we used fuzzy search
        var usedFuzzySearch = false

        // Try fuzzy search
        if players.isEmpty {
            players = try await fuzzySearch(query: normalized)
            usedFuzzySearch = !players.isEmpty
        }

        if players.isEmpty {
            return .notFound
        }

        // Check for ambiguous matches
        if players.count > 1 {
            let uniquePlayers = Set(players.map { "\($0.name)|\($0.nationality ?? "")" })
            if uniquePlayers.count > 1 {
                // For fuzzy search, prefer the top result
                if usedFuzzySearch {
                    players = [players[0]]
                } else {
                    return .ambiguous(count: uniquePlayers.count)
                }
            }
        }

        // Found a player - get their club history
        let player = players[0]
        guard let playerId = player.id else {
            return .notFound
        }

        let clubs = try await getClubHistory(playerId: playerId)
        let topClubs = calculateTopClubs(clubs: clubs)
        let careerSpan = calculateCareerSpan(clubs: clubs)

        let playerDisplay = PlayerDisplay(
            player: player,
            clubs: clubs,
            topClubs: topClubs,
            careerSpan: careerSpan
        )

        return .found(playerDisplay)
    }

    /// Exact match on normalized name
    private func exactMatch(normalized: String) async throws -> [Player] {
        try await dbPool.read { db in
            try Player.filter(Player.Columns.normalizedName == normalized).fetchAll(db)
        }
    }

    /// Prefix match on normalized name
    private func prefixMatch(normalized: String, limit: Int = 10) async throws -> [Player] {
        try await dbPool.read { db in
            try Player.filter(Player.Columns.normalizedName.like("\(normalized)%"))
                .limit(limit)
                .fetchAll(db)
        }
    }

    /// FTS5 full-text search with prefix matching
    private func ftsSearch(query: String, limit: Int = 10) async throws -> [Player] {
        try await dbPool.read { db in
            let words = query.split(separator: " ").map(String.init)
            guard !words.isEmpty else { return [] }

            // Add prefix wildcard to last word
            var ftsQuery = words
            ftsQuery[ftsQuery.count - 1] = words.last! + "*"
            let ftsQueryString = ftsQuery.joined(separator: " ")

            let sql = """
                SELECT p.*
                FROM players_fts fts
                JOIN players p ON fts.rowid = p.id
                WHERE players_fts MATCH ?
                ORDER BY rank
                LIMIT ?
            """

            return try Player.fetchAll(db, sql: sql, arguments: [ftsQueryString, limit])
        }
    }

    /// Fuzzy search using FTS5 prefix variations + Levenshtein distance
    private func fuzzySearch(query: String, limit: Int = 10, maxDistance: Int = 2) async throws -> [Player] {
        try await dbPool.read { db in
            let words = query.split(separator: " ").map(String.init)
            guard !words.isEmpty else { return [] }

            var candidates: [(player: Player, score: Double)] = []
            var seenIds = Set<Int64>()

            for word in words where word.count >= 2 {
                let prefixes = FuzzyMatcher.generatePrefixVariations(word: word, maxLen: 5)

                for prefix in prefixes where prefix.count >= 2 {
                    let sql = """
                        SELECT DISTINCT p.*
                        FROM players_fts fts
                        JOIN players p ON fts.rowid = p.id
                        WHERE players_fts MATCH ?
                        LIMIT 50
                    """

                    let players = try Player.fetchAll(db, sql: sql, arguments: ["\(prefix)*"])

                    for player in players {
                        guard let playerId = player.id, !seenIds.contains(playerId) else { continue }
                        seenIds.insert(playerId)

                        // Score by Levenshtein distance
                        let candidateNormalized = player.normalizedName
                        let distance = FuzzyMatcher.levenshteinDistance(query, candidateNormalized)

                        // Check distance for individual words too
                        let candidateWords = candidateNormalized.split(separator: " ").map(String.init)
                        let wordDistances = candidateWords.map {
                            FuzzyMatcher.levenshteinDistance(query, $0)
                        }
                        let minWordDistance = wordDistances.min() ?? distance
                        let closestWordIndex = wordDistances.firstIndex(of: minWordDistance) ?? 0
                        let closestWord = candidateWords.indices.contains(closestWordIndex) ?
                            candidateWords[closestWordIndex] : ""

                        let bestDistance = min(distance, minWordDistance)

                        // Length-based threshold
                        let queryLen = query.count
                        let threshold: Int
                        if queryLen <= 4 {
                            threshold = 1
                        } else if queryLen <= 8 {
                            threshold = 2
                        } else {
                            threshold = 3
                        }

                        if bestDistance <= threshold {
                            var score = Double(bestDistance) * 10.0

                            // Bonus for first word match
                            if !closestWord.isEmpty && !candidateWords.isEmpty &&
                               closestWord == candidateWords[0] {
                                score -= 2.0
                            }

                            // Penalty for length difference
                            let lengthDiff = abs(query.count - closestWord.count)
                            score += Double(lengthDiff) * 0.5

                            // Bonus for matching ending
                            if closestWord.count >= 3 && query.count >= 3 {
                                if query.suffix(3) == closestWord.suffix(3) {
                                    score -= 1.0
                                } else if query.suffix(2) == closestWord.suffix(2) {
                                    score -= 0.5
                                }
                            }

                            // Tiebreaker: prefer shorter names
                            score += Double(candidateNormalized.count) * 0.01

                            candidates.append((player: player, score: score))
                        }
                    }
                }
            }

            // Sort by score and return top results
            candidates.sort { $0.score < $1.score }
            return Array(candidates.prefix(limit).map { $0.player })
        }
    }

    /// Get club history for a player
    func getClubHistory(playerId: Int64) async throws -> [ClubHistory] {
        try await dbPool.read { db in
            let sql = """
                SELECT c.name, pc.start_date, pc.end_date, pc.is_national_team
                FROM player_clubs pc
                JOIN clubs c ON pc.club_id = c.id
                WHERE pc.player_id = ?
                ORDER BY pc.start_date
            """

            let rows = try Row.fetchAll(db, sql: sql, arguments: [playerId])

            return rows.map { row in
                let name: String = row["name"]
                let isNational: Bool = row["is_national_team"]
                let displayName = isNational ? NationalTeamFormatter.format(name) : name

                return ClubHistory(
                    name: name,
                    displayName: displayName,
                    startDate: row["start_date"],
                    endDate: row["end_date"],
                    isNationalTeam: isNational
                )
            }
        }
    }

    /// Calculate top 3 clubs by duration (non-national teams only)
    private func calculateTopClubs(clubs: [ClubHistory]) -> [String] {
        let nonNationalClubs = clubs.filter { !$0.isNationalTeam }

        let durations: [(String, Double)] = nonNationalClubs.map { club in
            let duration = calculateDuration(startDate: club.startDate, endDate: club.endDate)
            return (club.displayName, duration)
        }

        var seenClubs = Set<String>()
        var topClubs: [String] = []

        for (clubName, _) in durations.sorted(by: { $0.1 > $1.1 }) {
            if !seenClubs.contains(clubName) {
                seenClubs.insert(clubName)
                topClubs.append(clubName)
                if topClubs.count >= 3 { break }
            }
        }

        return topClubs
    }

    /// Calculate duration in years
    private func calculateDuration(startDate: String?, endDate: String?) -> Double {
        guard let startDate = startDate else { return 0.0 }

        let dateFormatter = DateFormatter()
        dateFormatter.dateFormat = "yyyy-MM-dd"

        var start: Date?
        if startDate.count >= 10 {
            start = dateFormatter.date(from: String(startDate.prefix(10)))
        }
        if start == nil && startDate.count >= 4 {
            dateFormatter.dateFormat = "yyyy"
            start = dateFormatter.date(from: String(startDate.prefix(4)))
        }
        guard let startParsed = start else { return 0.0 }

        var end: Date?
        if let endDate = endDate {
            dateFormatter.dateFormat = "yyyy-MM-dd"
            if endDate.count >= 10 {
                end = dateFormatter.date(from: String(endDate.prefix(10)))
            }
            if end == nil && endDate.count >= 4 {
                dateFormatter.dateFormat = "yyyy"
                end = dateFormatter.date(from: String(endDate.prefix(4)))
            }
        }

        let endDate = end ?? Date()
        let days = Calendar.current.dateComponents([.day], from: startParsed, to: endDate).day ?? 0
        return max(0.0, Double(days) / 365.25)
    }

    /// Calculate career span string
    private func calculateCareerSpan(clubs: [ClubHistory]) -> String? {
        guard !clubs.isEmpty else { return nil }

        var startYears: [Int] = []
        var endYears: [Int] = []

        for club in clubs {
            if let startDate = club.startDate, startDate.count >= 4,
               let year = Int(startDate.prefix(4)) {
                startYears.append(year)
            }
            if let endDate = club.endDate, endDate.count >= 4,
               let year = Int(endDate.prefix(4)) {
                endYears.append(year)
            }
        }

        guard let earliest = startYears.min() else { return nil }

        let hasActiveClub = clubs.contains { $0.endDate == nil }

        if hasActiveClub {
            return "\(earliest)-present"
        } else if let latest = endYears.max() {
            return "\(earliest)-\(latest)"
        } else {
            return "\(earliest)-present"
        }
    }

    /// Get player by ID
    func getPlayer(id: Int64) async throws -> Player? {
        try await dbPool.read { db in
            try Player.fetchOne(db, key: id)
        }
    }

    /// Get total player count
    func getTotalPlayers() async throws -> Int {
        try await dbPool.read { db in
            try Int.fetchOne(db, sql: "SELECT COUNT(*) FROM players") ?? 0
        }
    }
}

/// Result of a player lookup
enum PlayerLookupResult {
    case found(PlayerDisplay)
    case notFound
    case ambiguous(count: Int)
    case needsFullName
}
