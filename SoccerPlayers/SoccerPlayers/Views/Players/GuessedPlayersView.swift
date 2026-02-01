import SwiftUI

/// View displaying all guessed players with filtering
struct GuessedPlayersView: View {
    @EnvironmentObject var gameViewModel: GameViewModel
    @StateObject private var listViewModel = PlayerListViewModel()
    @State private var selectedPlayer: PlayerDisplay?
    @State private var showPlayerDetail = false

    var body: some View {
        NavigationStack {
            VStack(spacing: 0) {
                // Filter bar
                FilterBar(viewModel: listViewModel, gameViewModel: gameViewModel)
                    .padding(.horizontal)
                    .padding(.vertical, 8)
                    .background(Color(.systemBackground))

                Divider()

                // Player list
                let filteredPlayers = listViewModel.filter(players: gameViewModel.guessedPlayers)

                if filteredPlayers.isEmpty {
                    emptyState
                } else {
                    playerList(filteredPlayers)
                }
            }
            .navigationTitle("Guessed Players")
            .navigationBarTitleDisplayMode(.inline)
            .toolbar {
                ToolbarItem(placement: .navigationBarTrailing) {
                    Text("\(gameViewModel.guessedCount) players")
                        .font(.caption)
                        .foregroundColor(.secondary)
                }
            }
            .sheet(isPresented: $showPlayerDetail) {
                if let player = selectedPlayer {
                    PlayerDetailSheet(player: player)
                }
            }
        }
    }

    // MARK: - Empty State

    private var emptyState: some View {
        VStack(spacing: 16) {
            Spacer()

            Image(systemName: listViewModel.hasActiveFilters ? "magnifyingglass" : "person.3")
                .font(.system(size: 60))
                .foregroundColor(.secondary)

            if listViewModel.hasActiveFilters {
                Text("No players match your filters")
                    .font(.headline)
                    .foregroundColor(.secondary)

                Button("Clear Filters") {
                    listViewModel.clearFilters()
                }
                .buttonStyle(.bordered)
            } else {
                Text("No players guessed yet")
                    .font(.headline)
                    .foregroundColor(.secondary)

                Text("Go to the Play tab to start guessing!")
                    .font(.subheadline)
                    .foregroundColor(.secondary)
            }

            Spacer()
        }
    }

    // MARK: - Player List

    private func playerList(_ players: [PlayerDisplay]) -> some View {
        ScrollView {
            LazyVStack(spacing: 12) {
                ForEach(players) { player in
                    PlayerCardView(player: player, isCompact: true)
                        .onTapGesture {
                            selectedPlayer = player
                            showPlayerDetail = true
                        }
                        .contentShape(Rectangle())
                }
            }
            .padding()
        }
    }
}

#Preview {
    GuessedPlayersView()
        .environmentObject(GameViewModel(databaseManager: DatabaseManager.shared))
}
