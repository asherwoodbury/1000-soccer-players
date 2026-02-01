import Foundation
import GRDB

/// Represents a player that has been guessed in a session
struct GuessedPlayer: Codable, FetchableRecord, PersistableRecord, Identifiable {
    var id: Int64?
    let sessionId: Int64
    let playerId: Int64
    let guessedAt: Date?

    static let databaseTableName = "guessed_players"

    enum Columns {
        static let id = Column(CodingKeys.id)
        static let sessionId = Column(CodingKeys.sessionId)
        static let playerId = Column(CodingKeys.playerId)
        static let guessedAt = Column(CodingKeys.guessedAt)
    }

    enum CodingKeys: String, CodingKey {
        case id
        case sessionId = "session_id"
        case playerId = "player_id"
        case guessedAt = "guessed_at"
    }

    init(id: Int64? = nil, sessionId: Int64, playerId: Int64, guessedAt: Date? = Date()) {
        self.id = id
        self.sessionId = sessionId
        self.playerId = playerId
        self.guessedAt = guessedAt
    }
}
