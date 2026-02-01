import Foundation
import SwiftUI

/// Main game view model handling guessing logic and session management
@MainActor
final class GameViewModel: ObservableObject {
    // MARK: - Published Properties

    @Published var guessText: String = ""
    @Published var message: String = ""
    @Published var messageType: MessageType = .info
    @Published var guessedPlayers: [PlayerDisplay] = []
    @Published var guessedCount: Int = 0
    @Published var isLoading: Bool = false
    @Published var isSessionReady: Bool = false
    @Published var lastGuessedPlayer: PlayerDisplay?
    @Published var showPlayerDetail: Bool = false
    @Published var selectedPlayer: PlayerDisplay?

    // MARK: - Private Properties

    private var sessionId: Int64?
    private var playerRepository: PlayerRepository?
    private var sessionRepository: SessionRepository?
    private let databaseManager: DatabaseManager

    // MARK: - UserDefaults Keys

    private let sessionIdKey = "currentSessionId"

    // MARK: - Initialization

    init(databaseManager: DatabaseManager) {
        self.databaseManager = databaseManager
    }

    // MARK: - Setup

    func setup() async {
        guard databaseManager.isReady, let dbPool = databaseManager.dbPool else {
            message = "Database not ready"
            messageType = .error
            return
        }

        playerRepository = PlayerRepository(dbPool: dbPool)
        sessionRepository = SessionRepository(dbPool: dbPool)

        // Load or create session
        await loadOrCreateSession()
    }

    private func loadOrCreateSession() async {
        guard let sessionRepository = sessionRepository else { return }

        // Try to load existing session from UserDefaults
        // Note: UserDefaults stores Int64 as NSNumber, need to handle both Int and Int64 casts
        let savedValue = UserDefaults.standard.object(forKey: sessionIdKey)
        let savedId: Int64? = (savedValue as? Int64) ?? (savedValue as? Int).map { Int64($0) }

        if let savedId = savedId {
            do {
                if let existingSession = try await sessionRepository.getSession(id: savedId),
                   let existingId = existingSession.id {
                    sessionId = existingId
                    await loadGuessedPlayers()
                    isSessionReady = true
                    return
                }
            } catch {
                print("Failed to load session: \(error)")
            }
        }

        // Create new session
        do {
            let newSession = try await sessionRepository.createSession()
            guard let newId = newSession.id else {
                message = "Failed to create session: no ID returned"
                messageType = .error
                print("Session created but ID is nil")
                return
            }
            sessionId = newId
            UserDefaults.standard.set(newId, forKey: sessionIdKey)
            isSessionReady = true
        } catch {
            message = "Failed to create session"
            messageType = .error
            print("Failed to create session: \(error)")
        }
    }

    private func loadGuessedPlayers() async {
        guard let sessionRepository = sessionRepository,
              let playerRepository = playerRepository,
              let sessionId = sessionId else { return }

        do {
            guessedPlayers = try await sessionRepository.getGuessedPlayersWithDetails(
                sessionId: sessionId,
                playerRepository: playerRepository
            )
            guessedCount = guessedPlayers.count
        } catch {
            print("Failed to load guessed players: \(error)")
        }
    }

    // MARK: - Guess Submission

    func submitGuess() async {
        let input = guessText.trimmingCharacters(in: .whitespacesAndNewlines)
        guard !input.isEmpty else { return }

        guard let playerRepository = playerRepository,
              let sessionRepository = sessionRepository,
              let sessionId = sessionId else {
            message = "Session not ready"
            messageType = .error
            return
        }

        isLoading = true
        defer { isLoading = false }

        do {
            let result = try await playerRepository.lookupPlayer(name: input)

            switch result {
            case .found(let player):
                guard let playerId = player.player.id else {
                    message = "Invalid player data"
                    messageType = .error
                    return
                }

                // Check if already guessed
                let alreadyGuessed = try await sessionRepository.hasGuessedPlayer(
                    sessionId: sessionId,
                    playerId: playerId
                )

                if alreadyGuessed {
                    message = "\(player.name) has already been guessed!"
                    messageType = .warning
                } else {
                    // Add to guessed players
                    try await sessionRepository.addGuessedPlayer(
                        sessionId: sessionId,
                        playerId: playerId
                    )

                    guessedPlayers.insert(player, at: 0)
                    guessedCount = guessedPlayers.count
                    lastGuessedPlayer = player

                    message = "\(player.name) - Correct!"
                    messageType = .success
                    guessText = ""
                }

            case .notFound:
                message = "Player not found. Check the spelling and try again."
                messageType = .error

            case .ambiguous(let count):
                message = "Found \(count) players with that name. Please enter the full name to narrow it down."
                messageType = .warning

            case .needsFullName:
                message = "Please enter the player's full name (first and last name)."
                messageType = .info
            }
        } catch {
            message = "An error occurred. Please try again."
            messageType = .error
            print("Guess submission error: \(error)")
        }
    }

    // MARK: - Player Selection

    func selectPlayer(_ player: PlayerDisplay) {
        selectedPlayer = player
        showPlayerDetail = true
    }

    // MARK: - Session Management

    func resetSession() async {
        guard let sessionRepository = sessionRepository,
              let sessionId = sessionId else { return }

        do {
            try await sessionRepository.deleteSession(id: sessionId)
            self.sessionId = nil
            UserDefaults.standard.removeObject(forKey: sessionIdKey)
            guessedPlayers = []
            guessedCount = 0
            lastGuessedPlayer = nil
            message = ""

            await loadOrCreateSession()
        } catch {
            message = "Failed to reset session"
            messageType = .error
            print("Reset session error: \(error)")
        }
    }

    // MARK: - Filtering

    func filteredPlayers(
        searchText: String,
        positionFilter: String?,
        nationalityFilter: String?
    ) -> [PlayerDisplay] {
        var filtered = guessedPlayers

        // Text search
        if !searchText.isEmpty {
            let normalized = NameNormalizer.normalize(searchText)
            filtered = filtered.filter { player in
                NameNormalizer.normalize(player.name).contains(normalized)
            }
        }

        // Position filter
        if let position = positionFilter {
            filtered = filtered.filter { $0.position == position }
        }

        // Nationality filter
        if let nationality = nationalityFilter {
            filtered = filtered.filter { $0.nationality == nationality }
        }

        return filtered
    }

    // MARK: - Computed Properties

    var totalPlayers: Int {
        databaseManager.totalPlayers
    }

    var progressPercentage: Double {
        guard totalPlayers > 0 else { return 0 }
        return Double(guessedCount) / Double(min(totalPlayers, Constants.targetPlayerCount)) * 100
    }

    var uniqueNationalities: [String] {
        let nationalities = guessedPlayers.compactMap { $0.nationality }
        return Array(Set(nationalities)).sorted()
    }

    var uniquePositions: [String] {
        let positions = guessedPlayers.compactMap { $0.position }
        return Array(Set(positions)).sorted()
    }
}

// MARK: - Message Type

enum MessageType {
    case success
    case error
    case warning
    case info

    var color: Color {
        switch self {
        case .success: return .green
        case .error: return .red
        case .warning: return .orange
        case .info: return .blue
        }
    }
}
