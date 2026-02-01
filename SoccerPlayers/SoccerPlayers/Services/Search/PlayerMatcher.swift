import Foundation

/// Orchestrates player search across multiple strategies
final class PlayerMatcher {
    private let playerRepository: PlayerRepository

    init(playerRepository: PlayerRepository) {
        self.playerRepository = playerRepository
    }

    /// Search for a player by name, using multiple matching strategies
    func search(name: String) async throws -> PlayerLookupResult {
        try await playerRepository.lookupPlayer(name: name)
    }
}
