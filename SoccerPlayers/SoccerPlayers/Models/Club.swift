import Foundation
import GRDB

/// Represents a club/team in the database
struct Club: Codable, FetchableRecord, PersistableRecord, Identifiable {
    var id: Int64?
    let wikidataId: String
    let name: String
    let normalizedName: String
    let country: String?
    let league: String?
    let createdAt: Date?

    static let databaseTableName = "clubs"

    enum Columns {
        static let id = Column(CodingKeys.id)
        static let wikidataId = Column(CodingKeys.wikidataId)
        static let name = Column(CodingKeys.name)
        static let normalizedName = Column(CodingKeys.normalizedName)
        static let country = Column(CodingKeys.country)
        static let league = Column(CodingKeys.league)
        static let createdAt = Column(CodingKeys.createdAt)
    }

    enum CodingKeys: String, CodingKey {
        case id
        case wikidataId = "wikidata_id"
        case name
        case normalizedName = "normalized_name"
        case country
        case league
        case createdAt = "created_at"
    }
}

/// Club search result for display
struct ClubSearchResult: Identifiable {
    let id: Int64
    let name: String
    let displayName: String
    let isNationalTeam: Bool
}

/// Roster player for display
struct RosterPlayer: Identifiable {
    let id: Int64
    let name: String
    let position: String?
    let startYear: Int?
    let endYear: Int?
}

/// Roster response for a club's season
struct RosterResponse {
    let clubId: Int64
    let clubName: String
    let displayName: String
    let season: String
    let players: [RosterPlayer]
    let totalCount: Int
}
