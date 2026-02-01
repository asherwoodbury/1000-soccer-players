import Foundation
import GRDB

/// Represents a soccer player in the database
struct Player: Codable, FetchableRecord, PersistableRecord, Identifiable {
    var id: Int64?
    let wikidataId: String
    let name: String
    let normalizedName: String
    let firstName: String?
    let lastName: String?
    let nationality: String?
    let nationalityCode: String?
    let position: String?
    let birthDate: String?
    let gender: String
    let createdAt: Date?

    static let databaseTableName = "players"

    enum Columns {
        static let id = Column(CodingKeys.id)
        static let wikidataId = Column(CodingKeys.wikidataId)
        static let name = Column(CodingKeys.name)
        static let normalizedName = Column(CodingKeys.normalizedName)
        static let firstName = Column(CodingKeys.firstName)
        static let lastName = Column(CodingKeys.lastName)
        static let nationality = Column(CodingKeys.nationality)
        static let nationalityCode = Column(CodingKeys.nationalityCode)
        static let position = Column(CodingKeys.position)
        static let birthDate = Column(CodingKeys.birthDate)
        static let gender = Column(CodingKeys.gender)
        static let createdAt = Column(CodingKeys.createdAt)
    }

    enum CodingKeys: String, CodingKey {
        case id
        case wikidataId = "wikidata_id"
        case name
        case normalizedName = "normalized_name"
        case firstName = "first_name"
        case lastName = "last_name"
        case nationality
        case nationalityCode = "nationality_code"
        case position
        case birthDate = "birth_date"
        case gender
        case createdAt = "created_at"
    }
}

/// Player with computed properties for display
struct PlayerDisplay: Identifiable {
    let player: Player
    let clubs: [ClubHistory]
    let topClubs: [String]
    let careerSpan: String?

    var id: Int64 { player.id ?? 0 }
    var name: String { player.name }
    var nationality: String? { player.nationality }
    var position: String? { player.position }
}

/// Club history entry for a player
struct ClubHistory: Identifiable {
    let id = UUID()
    let name: String
    let displayName: String
    let startDate: String?
    let endDate: String?
    let isNationalTeam: Bool
}
