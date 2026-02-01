import Foundation
import GRDB

/// Repository for session database operations
final class SessionRepository {
    private let dbPool: DatabasePool

    init(dbPool: DatabasePool) {
        self.dbPool = dbPool
    }

    /// Create a new session
    func createSession() async throws -> Session {
        try await dbPool.write { db in
            let session = try Session().inserted(db)
            return session
        }
    }

    /// Get a session by ID
    func getSession(id: Int64) async throws -> Session? {
        try await dbPool.read { db in
            try Session.fetchOne(db, key: id)
        }
    }

    /// Update session's updated_at timestamp
    func touchSession(id: Int64) async throws {
        try await dbPool.write { db in
            try db.execute(
                sql: "UPDATE sessions SET updated_at = CURRENT_TIMESTAMP WHERE id = ?",
                arguments: [id]
            )
        }
    }

    /// Add a guessed player to a session
    func addGuessedPlayer(sessionId: Int64, playerId: Int64) async throws {
        try await dbPool.write { db in
            let guessed = GuessedPlayer(sessionId: sessionId, playerId: playerId)
            try guessed.insert(db)

            // Update session timestamp
            try db.execute(
                sql: "UPDATE sessions SET updated_at = CURRENT_TIMESTAMP WHERE id = ?",
                arguments: [sessionId]
            )
        }
    }

    /// Check if a player has already been guessed in a session
    func hasGuessedPlayer(sessionId: Int64, playerId: Int64) async throws -> Bool {
        try await dbPool.read { db in
            let count = try Int.fetchOne(db, sql: """
                SELECT COUNT(*) FROM guessed_players
                WHERE session_id = ? AND player_id = ?
            """, arguments: [sessionId, playerId])
            return (count ?? 0) > 0
        }
    }

    /// Get count of guessed players in a session
    func getGuessedCount(sessionId: Int64) async throws -> Int {
        try await dbPool.read { db in
            try Int.fetchOne(db, sql: """
                SELECT COUNT(*) FROM guessed_players WHERE session_id = ?
            """, arguments: [sessionId]) ?? 0
        }
    }

    /// Get all guessed players for a session with their details
    func getGuessedPlayers(sessionId: Int64) async throws -> [PlayerDisplay] {
        try await dbPool.read { db in
            let sql = """
                SELECT p.*
                FROM guessed_players gp
                JOIN players p ON gp.player_id = p.id
                WHERE gp.session_id = ?
                ORDER BY gp.guessed_at DESC
            """

            let players = try Player.fetchAll(db, sql: sql, arguments: [sessionId])
            return players.map { player in
                PlayerDisplay(
                    player: player,
                    clubs: [], // Clubs loaded on demand
                    topClubs: [],
                    careerSpan: nil
                )
            }
        }
    }

    /// Get guessed players with full details (including clubs)
    func getGuessedPlayersWithDetails(sessionId: Int64, playerRepository: PlayerRepository) async throws -> [PlayerDisplay] {
        let basicPlayers = try await getGuessedPlayers(sessionId: sessionId)

        var detailedPlayers: [PlayerDisplay] = []
        for player in basicPlayers {
            if let playerId = player.player.id {
                let clubs = try await playerRepository.getClubHistory(playerId: playerId)
                let topClubs = calculateTopClubs(clubs: clubs)
                let careerSpan = calculateCareerSpan(clubs: clubs)

                detailedPlayers.append(PlayerDisplay(
                    player: player.player,
                    clubs: clubs,
                    topClubs: topClubs,
                    careerSpan: careerSpan
                ))
            }
        }

        return detailedPlayers
    }

    /// Calculate top 3 clubs by duration
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

    /// Delete a session and all its guessed players
    func deleteSession(id: Int64) async throws {
        try await dbPool.write { db in
            try db.execute(sql: "DELETE FROM guessed_players WHERE session_id = ?", arguments: [id])
            try db.execute(sql: "DELETE FROM sessions WHERE id = ?", arguments: [id])
        }
    }
}
