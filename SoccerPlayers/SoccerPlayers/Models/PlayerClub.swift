import Foundation
import GRDB

/// Represents a player's stint at a club
struct PlayerClub: Codable, FetchableRecord, PersistableRecord, Identifiable {
    var id: Int64?
    let playerId: Int64
    let clubId: Int64
    let startDate: String?
    let endDate: String?
    let isNationalTeam: Bool

    static let databaseTableName = "player_clubs"

    enum Columns {
        static let id = Column(CodingKeys.id)
        static let playerId = Column(CodingKeys.playerId)
        static let clubId = Column(CodingKeys.clubId)
        static let startDate = Column(CodingKeys.startDate)
        static let endDate = Column(CodingKeys.endDate)
        static let isNationalTeam = Column(CodingKeys.isNationalTeam)
    }

    enum CodingKeys: String, CodingKey {
        case id
        case playerId = "player_id"
        case clubId = "club_id"
        case startDate = "start_date"
        case endDate = "end_date"
        case isNationalTeam = "is_national_team"
    }
}
