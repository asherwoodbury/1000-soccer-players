import Foundation
import GRDB

/// Represents a game session
struct Session: Codable, FetchableRecord, PersistableRecord, Identifiable {
    var id: Int64?
    let createdAt: Date?
    var updatedAt: Date?

    static let databaseTableName = "sessions"

    enum Columns {
        static let id = Column(CodingKeys.id)
        static let createdAt = Column(CodingKeys.createdAt)
        static let updatedAt = Column(CodingKeys.updatedAt)
    }

    enum CodingKeys: String, CodingKey {
        case id
        case createdAt = "created_at"
        case updatedAt = "updated_at"
    }

    init(id: Int64? = nil, createdAt: Date? = nil, updatedAt: Date? = nil) {
        self.id = id
        self.createdAt = createdAt
        self.updatedAt = updatedAt
    }

    /// Columns to persist - excludes timestamps to use database defaults
    func encode(to container: inout PersistenceContainer) throws {
        // Encode id (nil triggers auto-increment on insert)
        container[CodingKeys.id.stringValue] = id
        // Don't encode created_at and updated_at - let database defaults handle them
    }

    /// Called after insert to receive the auto-generated row ID
    mutating func didInsert(_ inserted: InsertionSuccess) {
        id = inserted.rowID
    }
}
