import SwiftUI

/// Main container view with tab navigation
struct ContentView: View {
    @EnvironmentObject var databaseManager: DatabaseManager
    @StateObject private var gameViewModel: GameViewModel
    @StateObject private var rosterViewModel: RosterViewModel

    init() {
        let manager = DatabaseManager.shared
        _gameViewModel = StateObject(wrappedValue: GameViewModel(databaseManager: manager))
        _rosterViewModel = StateObject(wrappedValue: RosterViewModel(databaseManager: manager))
    }

    var body: some View {
        Group {
            if databaseManager.isReady {
                TabView {
                    GameTabView()
                        .environmentObject(gameViewModel)
                        .tabItem {
                            Label("Play", systemImage: "gamecontroller.fill")
                        }

                    GuessedPlayersView()
                        .environmentObject(gameViewModel)
                        .tabItem {
                            Label("Players", systemImage: "person.3.fill")
                        }

                    RosterTabView()
                        .environmentObject(rosterViewModel)
                        .tabItem {
                            Label("Rosters", systemImage: "list.bullet.rectangle")
                        }

                    SettingsView()
                        .environmentObject(gameViewModel)
                        .tabItem {
                            Label("Settings", systemImage: "gear")
                        }
                }
                .task {
                    await gameViewModel.setup()
                    await rosterViewModel.setup()
                }
            } else if let error = databaseManager.error {
                VStack(spacing: 16) {
                    Image(systemName: "exclamationmark.triangle.fill")
                        .font(.system(size: 60))
                        .foregroundColor(.orange)

                    Text("Database Error")
                        .font(.title)
                        .fontWeight(.bold)

                    Text(error.localizedDescription)
                        .font(.body)
                        .foregroundColor(.secondary)
                        .multilineTextAlignment(.center)
                        .padding(.horizontal)
                }
            } else {
                VStack(spacing: 16) {
                    ProgressView()
                        .scaleEffect(1.5)

                    Text("Loading players...")
                        .font(.headline)
                        .foregroundColor(.secondary)
                }
            }
        }
    }
}

#Preview {
    ContentView()
        .environmentObject(DatabaseManager.shared)
}
