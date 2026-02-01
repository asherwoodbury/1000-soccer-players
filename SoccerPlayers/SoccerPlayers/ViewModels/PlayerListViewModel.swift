import Foundation

/// View model for the player list with filtering capabilities
@MainActor
final class PlayerListViewModel: ObservableObject {
    @Published var searchText: String = ""
    @Published var selectedPosition: String?
    @Published var selectedNationality: String?
    @Published var sortOrder: SortOrder = .recent

    enum SortOrder: String, CaseIterable {
        case recent = "Most Recent"
        case alphabetical = "A-Z"
        case nationality = "Nationality"
        case position = "Position"
    }

    /// Filter and sort players based on current criteria
    func filter(players: [PlayerDisplay]) -> [PlayerDisplay] {
        var filtered = players

        // Text search
        if !searchText.isEmpty {
            let normalized = NameNormalizer.normalize(searchText)
            filtered = filtered.filter { player in
                let nameMatch = NameNormalizer.normalize(player.name).contains(normalized)
                let clubMatch = player.topClubs.contains { club in
                    NameNormalizer.normalize(club).contains(normalized)
                }
                return nameMatch || clubMatch
            }
        }

        // Position filter
        if let position = selectedPosition {
            filtered = filtered.filter { $0.position == position }
        }

        // Nationality filter
        if let nationality = selectedNationality {
            filtered = filtered.filter { $0.nationality == nationality }
        }

        // Sort
        switch sortOrder {
        case .recent:
            break // Already in order
        case .alphabetical:
            filtered.sort { $0.name.localizedCaseInsensitiveCompare($1.name) == .orderedAscending }
        case .nationality:
            filtered.sort {
                ($0.nationality ?? "").localizedCaseInsensitiveCompare($1.nationality ?? "") == .orderedAscending
            }
        case .position:
            filtered.sort {
                ($0.position ?? "").localizedCaseInsensitiveCompare($1.position ?? "") == .orderedAscending
            }
        }

        return filtered
    }

    /// Clear all filters
    func clearFilters() {
        searchText = ""
        selectedPosition = nil
        selectedNationality = nil
        sortOrder = .recent
    }

    /// Check if any filters are active
    var hasActiveFilters: Bool {
        !searchText.isEmpty || selectedPosition != nil || selectedNationality != nil || sortOrder != .recent
    }
}
