import Foundation
import GRDB

/// Repository for club database operations
final class ClubRepository {
    private let dbPool: DatabasePool

    init(dbPool: DatabasePool) {
        self.dbPool = dbPool
    }

    /// Search for clubs by name
    func searchClubs(query: String, limit: Int = 20) async throws -> [ClubSearchResult] {
        let normalized = NameNormalizer.normalize(query)

        return try await dbPool.read { db in
            let sql = """
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
            """

            let rows = try Row.fetchAll(db, sql: sql, arguments: ["%\(normalized)%", limit * 2])

            var results: [(ClubSearchResult, Int, Int)] = rows.map { row in
                let id: Int64 = row["id"]
                let name: String = row["name"]
                let isNational: Bool = row["is_national_team"]
                let playerCount: Int = row["player_count"]
                let displayName = isNational ? NationalTeamFormatter.format(name) : name
                let priority = isNational ? NationalTeamFormatter.priority(for: name) : 50

                return (ClubSearchResult(
                    id: id,
                    name: name,
                    displayName: displayName,
                    isNationalTeam: isNational
                ), playerCount, priority)
            }

            // Sort: national teams by priority first, then by player count
            results.sort { ($0.2, -$0.1) < ($1.2, -$1.1) }

            return Array(results.prefix(limit).map { $0.0 })
        }
    }

    /// Get roster for a club in a specific season
    func getRoster(clubId: Int64, season: Int) async throws -> RosterResponse {
        try await dbPool.read { db in
            // Get club info
            guard let club = try Club.fetchOne(db, key: clubId) else {
                return RosterResponse(
                    clubId: clubId,
                    clubName: "Unknown Club",
                    displayName: "Unknown Club",
                    season: "\(season)/\(String(season + 1).suffix(2))",
                    players: [],
                    totalCount: 0
                )
            }

            let seasonEnd = season + 1
            let maxTenureYears = 10
            let oldestValidStart = season - maxTenureYears

            let sql = """
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
                          (pc.end_date IS NOT NULL
                           AND pc.end_date NOT LIKE '%http%'
                           AND LENGTH(pc.end_date) >= 4
                           AND CAST(SUBSTR(pc.end_date, 1, 4) AS INTEGER) >= ?)
                          OR
                          ((pc.end_date IS NULL OR pc.end_date LIKE '%http%' OR LENGTH(pc.end_date) < 4)
                           AND CAST(SUBSTR(pc.start_date, 1, 4) AS INTEGER) >= ?)
                      )
                ),
                best_stint AS (
                    SELECT
                        player_id,
                        MAX(start_year) as start_year,
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
            """

            let rows = try Row.fetchAll(db, sql: sql, arguments: [clubId, seasonEnd, season, oldestValidStart])

            let players: [RosterPlayer] = rows.map { row in
                RosterPlayer(
                    id: row["id"],
                    name: row["name"],
                    position: row["position"],
                    startYear: row["start_year"],
                    endYear: row["end_year"]
                )
            }

            let displayName = NationalTeamFormatter.format(club.name)

            return RosterResponse(
                clubId: clubId,
                clubName: club.name,
                displayName: displayName,
                season: "\(season)/\(String(seasonEnd).suffix(2))",
                players: players,
                totalCount: players.count
            )
        }
    }

    /// Get the range of years a club has player data for
    func getClubYears(clubId: Int64) async throws -> (minYear: Int, maxYear: Int) {
        try await dbPool.read { db in
            let sql = """
                SELECT
                    MIN(CAST(SUBSTR(pc.start_date, 1, 4) AS INTEGER)) as min_year,
                    MAX(CASE
                        WHEN pc.end_date IS NULL THEN CAST(strftime('%Y', 'now') AS INTEGER)
                        ELSE CAST(SUBSTR(pc.end_date, 1, 4) AS INTEGER)
                    END) as max_year
                FROM player_clubs pc
                WHERE pc.club_id = ?
                  AND pc.start_date IS NOT NULL
            """

            let minSeason = 2000
            let maxSeason = 2025

            if let row = try Row.fetchOne(db, sql: sql, arguments: [clubId]),
               let minYear: Int = row["min_year"] {
                let maxYear: Int = row["max_year"] ?? maxSeason
                return (max(minYear, minSeason), min(maxYear, maxSeason))
            }

            return (minSeason, maxSeason)
        }
    }
}
