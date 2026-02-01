import SwiftUI

/// Settings and preferences view
struct SettingsView: View {
    @EnvironmentObject var gameViewModel: GameViewModel
    @StateObject private var viewModel = SettingsViewModel()
    @EnvironmentObject var databaseManager: DatabaseManager
    @State private var showResetConfirmation = false

    var body: some View {
        NavigationStack {
            List {
                // Display settings
                displaySettingsSection

                // Game section
                gameSection

                // Database info
                databaseSection

                // About
                aboutSection
            }
            .navigationTitle("Settings")
            .navigationBarTitleDisplayMode(.inline)
            .onAppear {
                viewModel.loadDatabaseInfo(manager: databaseManager)
            }
            .alert("Reset Progress?", isPresented: $showResetConfirmation) {
                Button("Cancel", role: .cancel) { }
                Button("Reset", role: .destructive) {
                    Task {
                        await gameViewModel.resetSession()
                    }
                }
            } message: {
                Text("This will delete all your guessed players and start fresh. This action cannot be undone.")
            }
        }
    }

    // MARK: - Display Settings Section

    private var displaySettingsSection: some View {
        Section("Display") {
            Toggle("Show Nationality", isOn: $viewModel.showNationality)
            Toggle("Show Position", isOn: $viewModel.showPosition)
            Toggle("Show Top Clubs", isOn: $viewModel.showClubs)
            Toggle("Show Career Span", isOn: $viewModel.showCareerSpan)
            Toggle("Compact Mode", isOn: $viewModel.compactMode)
        }
    }

    // MARK: - Game Section

    private var gameSection: some View {
        Section("Game") {
            HStack {
                Text("Players Guessed")
                Spacer()
                Text("\(gameViewModel.guessedCount)")
                    .foregroundColor(.secondary)
            }

            HStack {
                Text("Progress")
                Spacer()
                Text(String(format: "%.1f%%", gameViewModel.progressPercentage))
                    .foregroundColor(.secondary)
            }

            Button(role: .destructive) {
                showResetConfirmation = true
            } label: {
                HStack {
                    Image(systemName: "arrow.counterclockwise")
                    Text("Reset Progress")
                }
            }
        }
    }

    // MARK: - Database Section

    private var databaseSection: some View {
        Section("Database") {
            HStack {
                Text("Total Players")
                Spacer()
                Text("\(viewModel.totalPlayers)")
                    .foregroundColor(.secondary)
            }

            HStack {
                Text("Database Size")
                Spacer()
                Text(viewModel.databaseSize)
                    .foregroundColor(.secondary)
            }
        }
    }

    // MARK: - About Section

    private var aboutSection: some View {
        Section("About") {
            HStack {
                Text("Version")
                Spacer()
                Text("1.0.0")
                    .foregroundColor(.secondary)
            }

            Link(destination: URL(string: "https://github.com")!) {
                HStack {
                    Text("Source Code")
                    Spacer()
                    Image(systemName: "arrow.up.right.square")
                        .foregroundColor(.secondary)
                }
            }

            Text("Data sourced from Wikidata. Player information may not be complete or fully accurate.")
                .font(.caption)
                .foregroundColor(.secondary)
        }
    }
}

#Preview {
    SettingsView()
        .environmentObject(GameViewModel(databaseManager: DatabaseManager.shared))
        .environmentObject(DatabaseManager.shared)
}
