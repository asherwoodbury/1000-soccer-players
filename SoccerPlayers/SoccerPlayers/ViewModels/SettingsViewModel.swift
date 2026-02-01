import Foundation
import SwiftUI

/// View model for settings
@MainActor
final class SettingsViewModel: ObservableObject {
    // MARK: - Display Settings

    @AppStorage("showNationality") var showNationality: Bool = true
    @AppStorage("showPosition") var showPosition: Bool = true
    @AppStorage("showClubs") var showClubs: Bool = true
    @AppStorage("showCareerSpan") var showCareerSpan: Bool = false
    @AppStorage("compactMode") var compactMode: Bool = false

    // MARK: - Game Settings

    @Published var showResetConfirmation: Bool = false

    // MARK: - Database Info

    var totalPlayers: Int = 0
    var databaseSize: String = "Unknown"

    // MARK: - Methods

    func loadDatabaseInfo(manager: DatabaseManager) {
        totalPlayers = manager.totalPlayers

        // Calculate database size
        let fileManager = FileManager.default
        if let documentsURL = try? fileManager.url(
            for: .documentDirectory,
            in: .userDomainMask,
            appropriateFor: nil,
            create: false
        ) {
            let dbURL = documentsURL.appendingPathComponent("players.db")
            if let attributes = try? fileManager.attributesOfItem(atPath: dbURL.path),
               let size = attributes[.size] as? UInt64 {
                databaseSize = ByteCountFormatter.string(fromByteCount: Int64(size), countStyle: .file)
            }
        }
    }

    func confirmReset() {
        showResetConfirmation = true
    }
}
