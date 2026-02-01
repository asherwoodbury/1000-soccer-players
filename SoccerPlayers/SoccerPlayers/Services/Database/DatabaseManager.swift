import Foundation
import GRDB

/// Manages the SQLite database connection and setup
final class DatabaseManager: ObservableObject {
    static let shared = DatabaseManager()

    private(set) var dbPool: DatabasePool?
    @Published private(set) var isReady = false
    @Published private(set) var error: Error?
    @Published private(set) var totalPlayers: Int = 0

    private init() {
        Task {
            await setup()
        }
    }

    /// Copy bundled database to Documents on first launch, then open connection
    @MainActor
    func setup() async {
        do {
            let fileManager = FileManager.default
            let documentsURL = try fileManager.url(
                for: .documentDirectory,
                in: .userDomainMask,
                appropriateFor: nil,
                create: true
            )
            let destinationURL = documentsURL.appendingPathComponent("players.db")

            // Copy bundled database if not already in Documents
            if !fileManager.fileExists(atPath: destinationURL.path) {
                guard let bundledURL = Bundle.main.url(forResource: "players", withExtension: "db") else {
                    throw DatabaseError.bundledDatabaseNotFound
                }
                try fileManager.copyItem(at: bundledURL, to: destinationURL)
            }

            // Open database connection pool
            var config = Configuration()
            config.readonly = false
            config.foreignKeysEnabled = true

            dbPool = try DatabasePool(path: destinationURL.path, configuration: config)

            // Initialize session table if needed (may not exist in bundled DB)
            try await initializeSessionTables()

            // Get total player count
            if let pool = dbPool {
                totalPlayers = try await pool.read { db in
                    try Int.fetchOne(db, sql: "SELECT COUNT(*) FROM players") ?? 0
                }
            }

            isReady = true
        } catch {
            self.error = error
            print("Database setup failed: \(error)")
        }
    }

    /// Create session tables if they don't exist
    private func initializeSessionTables() async throws {
        guard let pool = dbPool else { return }

        try await pool.write { db in
            // Sessions table
            try db.execute(sql: """
                CREATE TABLE IF NOT EXISTS sessions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

            // Guessed players table
            try db.execute(sql: """
                CREATE TABLE IF NOT EXISTS guessed_players (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id INTEGER NOT NULL,
                    player_id INTEGER NOT NULL,
                    guessed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (session_id) REFERENCES sessions(id),
                    FOREIGN KEY (player_id) REFERENCES players(id),
                    UNIQUE(session_id, player_id)
                )
            """)

            // Index for fast lookup
            try db.execute(sql: """
                CREATE INDEX IF NOT EXISTS idx_guessed_players_session
                ON guessed_players(session_id)
            """)
        }
    }
}

enum DatabaseError: LocalizedError {
    case bundledDatabaseNotFound
    case databaseNotInitialized

    var errorDescription: String? {
        switch self {
        case .bundledDatabaseNotFound:
            return "The bundled player database was not found in the app bundle."
        case .databaseNotInitialized:
            return "The database has not been initialized."
        }
    }
}
