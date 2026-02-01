import SwiftUI

/// Tab for browsing club rosters
struct RosterTabView: View {
    @EnvironmentObject var viewModel: RosterViewModel

    var body: some View {
        NavigationStack {
            VStack(spacing: 0) {
                if viewModel.selectedClub == nil {
                    clubSearchView
                } else {
                    rosterView
                }
            }
            .navigationTitle("Club Rosters")
            .navigationBarTitleDisplayMode(.inline)
            .toolbar {
                if viewModel.selectedClub != nil {
                    ToolbarItem(placement: .navigationBarLeading) {
                        Button {
                            viewModel.clearSelection()
                        } label: {
                            HStack(spacing: 4) {
                                Image(systemName: "chevron.left")
                                Text("Search")
                            }
                        }
                    }
                }
            }
        }
    }

    // MARK: - Club Search View

    private var clubSearchView: some View {
        VStack(spacing: 0) {
            // Search bar
            ClubSearchView(viewModel: viewModel)
                .padding()
                .background(Color(.systemBackground))

            Divider()

            // Recent clubs
            if !viewModel.recentClubs.isEmpty && viewModel.searchText.isEmpty {
                RecentClubsChips(viewModel: viewModel)
                    .padding(.horizontal)
                    .padding(.vertical, 12)
                    .background(Color(.systemBackground))

                Divider()
            }

            // Search results
            if !viewModel.searchResults.isEmpty {
                searchResultsList
            } else if viewModel.searchText.count >= 2 && !viewModel.isSearching {
                noResultsView
            } else {
                emptySearchState
            }
        }
    }

    private var searchResultsList: some View {
        List(viewModel.searchResults) { club in
            Button {
                Task {
                    await viewModel.selectClub(club)
                }
            } label: {
                HStack {
                    Image(systemName: club.isNationalTeam ? "flag.fill" : "building.2.fill")
                        .foregroundColor(club.isNationalTeam ? .yellow : .blue)
                        .frame(width: 24)

                    Text(club.displayName)
                        .foregroundColor(.primary)

                    Spacer()

                    Image(systemName: "chevron.right")
                        .foregroundColor(.secondary)
                        .font(.caption)
                }
            }
        }
        .listStyle(.plain)
    }

    private var noResultsView: some View {
        VStack(spacing: 16) {
            Spacer()

            Image(systemName: "magnifyingglass")
                .font(.system(size: 60))
                .foregroundColor(.secondary)

            Text("No clubs found")
                .font(.headline)
                .foregroundColor(.secondary)

            Text("Try a different search term")
                .font(.subheadline)
                .foregroundColor(.secondary)

            Spacer()
        }
    }

    private var emptySearchState: some View {
        VStack(spacing: 16) {
            Spacer()

            Image(systemName: "building.2.crop.circle")
                .font(.system(size: 60))
                .foregroundColor(.secondary)

            Text("Search for a club")
                .font(.headline)
                .foregroundColor(.secondary)

            Text("Enter a club name to view their roster")
                .font(.subheadline)
                .foregroundColor(.secondary)
                .multilineTextAlignment(.center)
                .padding(.horizontal)

            Spacer()
        }
    }

    // MARK: - Roster View

    private var rosterView: some View {
        VStack(spacing: 0) {
            if let club = viewModel.selectedClub {
                // Club header
                VStack(spacing: 8) {
                    Text(club.displayName)
                        .font(.title2)
                        .fontWeight(.bold)

                    // Season selector
                    seasonSelector
                }
                .padding()
                .background(Color(.systemBackground))

                Divider()

                // Roster grid
                if viewModel.isLoadingRoster {
                    VStack {
                        Spacer()
                        ProgressView("Loading roster...")
                        Spacer()
                    }
                } else if let roster = viewModel.roster {
                    RosterGridView(roster: roster, guessedPlayerIds: viewModel.guessedPlayerIds)
                } else {
                    VStack {
                        Spacer()
                        Text("Unable to load roster")
                            .foregroundColor(.secondary)
                        Spacer()
                    }
                }
            }
        }
    }

    private var seasonSelector: some View {
        HStack {
            Button {
                if viewModel.selectedSeason > viewModel.minYear {
                    Task {
                        await viewModel.changeSeason(to: viewModel.selectedSeason - 1)
                    }
                }
            } label: {
                Image(systemName: "chevron.left")
                    .padding(8)
            }
            .disabled(viewModel.selectedSeason <= viewModel.minYear)

            Spacer()

            Text("\(viewModel.selectedSeason)/\(String(viewModel.selectedSeason + 1).suffix(2))")
                .font(.headline)

            Spacer()

            Button {
                if viewModel.selectedSeason < viewModel.maxYear {
                    Task {
                        await viewModel.changeSeason(to: viewModel.selectedSeason + 1)
                    }
                }
            } label: {
                Image(systemName: "chevron.right")
                    .padding(8)
            }
            .disabled(viewModel.selectedSeason >= viewModel.maxYear)
        }
        .padding(.horizontal)
    }
}

#Preview {
    RosterTabView()
        .environmentObject(RosterViewModel(databaseManager: DatabaseManager.shared))
}
