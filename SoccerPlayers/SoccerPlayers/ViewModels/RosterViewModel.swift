import Foundation

/// View model for the roster tab
@MainActor
final class RosterViewModel: ObservableObject {
    @Published var searchText: String = ""
    @Published var searchResults: [ClubSearchResult] = []
    @Published var selectedClub: ClubSearchResult?
    @Published var roster: RosterResponse?
    @Published var selectedSeason: Int
    @Published var minYear: Int = 2000
    @Published var maxYear: Int
    @Published var isSearching: Bool = false
    @Published var isLoadingRoster: Bool = false
    @Published var recentClubs: [ClubSearchResult] = []
    @Published var errorMessage: String?
    @Published var guessedPlayerIds: Set<Int64> = []

    private var clubRepository: ClubRepository?
    private var sessionRepository: SessionRepository?
    private let databaseManager: DatabaseManager

    private let recentClubsKey = "recentClubs"
    private let maxRecentClubs = 5
    private let sessionIdKey = "currentSessionId"

    init(databaseManager: DatabaseManager) {
        self.databaseManager = databaseManager
        let currentYear = Calendar.current.component(.year, from: Date())
        self.maxYear = currentYear
        self.selectedSeason = Constants.currentSeason
        loadRecentClubs()
    }

    func setup() async {
        guard databaseManager.isReady, let dbPool = databaseManager.dbPool else {
            errorMessage = "Database not ready"
            return
        }

        clubRepository = ClubRepository(dbPool: dbPool)
        sessionRepository = SessionRepository(dbPool: dbPool)

        // Load guessed player IDs
        await loadGuessedPlayerIds()
    }

    /// Load the set of guessed player IDs from the current session
    func loadGuessedPlayerIds() async {
        guard let sessionRepository = sessionRepository else { return }

        // Get session ID from UserDefaults
        guard let sessionId = UserDefaults.standard.object(forKey: sessionIdKey) as? Int64 else {
            return
        }

        do {
            let guessedPlayers = try await sessionRepository.getGuessedPlayers(sessionId: sessionId)
            guessedPlayerIds = Set(guessedPlayers.compactMap { $0.player.id })
        } catch {
            print("Failed to load guessed player IDs: \(error)")
        }
    }

    // MARK: - Club Search

    func searchClubs() async {
        guard let clubRepository = clubRepository else { return }
        guard searchText.count >= 2 else {
            searchResults = []
            return
        }

        isSearching = true
        defer { isSearching = false }

        do {
            searchResults = try await clubRepository.searchClubs(query: searchText)
            errorMessage = nil
        } catch {
            errorMessage = "Search failed"
            print("Club search error: \(error)")
        }
    }

    // MARK: - Club Selection

    func selectClub(_ club: ClubSearchResult) async {
        selectedClub = club
        searchText = ""
        searchResults = []

        // Add to recent clubs
        addToRecentClubs(club)

        // Load years range
        await loadClubYears(clubId: club.id)

        // Load roster
        await loadRoster()
    }

    private func loadClubYears(clubId: Int64) async {
        guard let clubRepository = clubRepository else { return }

        do {
            let years = try await clubRepository.getClubYears(clubId: clubId)
            minYear = years.minYear
            maxYear = years.maxYear

            // Clamp selected season to valid range
            if selectedSeason < minYear {
                selectedSeason = minYear
            } else if selectedSeason > maxYear {
                selectedSeason = maxYear
            }
        } catch {
            print("Failed to load club years: \(error)")
        }
    }

    // MARK: - Roster Loading

    func loadRoster() async {
        guard let clubRepository = clubRepository,
              let club = selectedClub else { return }

        isLoadingRoster = true
        defer { isLoadingRoster = false }

        // Refresh guessed player IDs
        await loadGuessedPlayerIds()

        do {
            roster = try await clubRepository.getRoster(clubId: club.id, season: selectedSeason)
            errorMessage = nil
        } catch {
            errorMessage = "Failed to load roster"
            print("Roster load error: \(error)")
        }
    }

    func changeSeason(to season: Int) async {
        selectedSeason = season
        await loadRoster()
    }

    // MARK: - Recent Clubs

    private func loadRecentClubs() {
        guard let data = UserDefaults.standard.data(forKey: recentClubsKey),
              let clubs = try? JSONDecoder().decode([RecentClubData].self, from: data) else {
            return
        }

        recentClubs = clubs.map { data in
            ClubSearchResult(
                id: data.id,
                name: data.name,
                displayName: data.displayName,
                isNationalTeam: data.isNationalTeam
            )
        }
    }

    private func addToRecentClubs(_ club: ClubSearchResult) {
        // Remove if already exists
        recentClubs.removeAll { $0.id == club.id }

        // Add to front
        recentClubs.insert(club, at: 0)

        // Limit size
        if recentClubs.count > maxRecentClubs {
            recentClubs = Array(recentClubs.prefix(maxRecentClubs))
        }

        // Save to UserDefaults
        let data = recentClubs.map { club in
            RecentClubData(
                id: club.id,
                name: club.name,
                displayName: club.displayName,
                isNationalTeam: club.isNationalTeam
            )
        }

        if let encoded = try? JSONEncoder().encode(data) {
            UserDefaults.standard.set(encoded, forKey: recentClubsKey)
        }
    }

    // MARK: - Clear Selection

    func clearSelection() {
        selectedClub = nil
        roster = nil
    }
}

// MARK: - Recent Club Data (for persistence)

private struct RecentClubData: Codable {
    let id: Int64
    let name: String
    let displayName: String
    let isNationalTeam: Bool
}
