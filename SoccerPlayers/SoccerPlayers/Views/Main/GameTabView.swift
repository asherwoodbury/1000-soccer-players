import SwiftUI

/// Main game tab for entering guesses
struct GameTabView: View {
    @EnvironmentObject var viewModel: GameViewModel
    @FocusState private var isInputFocused: Bool

    var body: some View {
        NavigationStack {
            VStack(spacing: 0) {
                // Progress section
                progressSection
                    .padding()
                    .background(Color(.systemBackground))

                Divider()

                // Main content
                ScrollView {
                    VStack(spacing: 24) {
                        // Input section
                        inputSection

                        // Message feedback
                        if !viewModel.message.isEmpty {
                            messageView
                                .transition(.opacity.combined(with: .move(edge: .top)))
                        }

                        // Last guessed player
                        if let player = viewModel.lastGuessedPlayer {
                            lastGuessedPlayerCard(player)
                                .transition(.asymmetric(
                                    insertion: .scale.combined(with: .opacity),
                                    removal: .opacity
                                ))
                        }
                    }
                    .padding()
                }
            }
            .navigationTitle("1000 Soccer Players")
            .navigationBarTitleDisplayMode(.inline)
            .animation(.easeInOut(duration: 0.3), value: viewModel.message)
            .animation(.spring(response: 0.4, dampingFraction: 0.8), value: viewModel.lastGuessedPlayer?.id)
        }
    }

    // MARK: - Progress Section

    private var progressSection: some View {
        VStack(spacing: 12) {
            HStack {
                Text("\(viewModel.guessedCount)")
                    .font(.system(size: 48, weight: .bold, design: .rounded))
                    .foregroundColor(.primary)
                    .contentTransition(.numericText())

                Text("/ \(min(viewModel.totalPlayers, Constants.targetPlayerCount))")
                    .font(.title2)
                    .foregroundColor(.secondary)

                Spacer()

                VStack(alignment: .trailing) {
                    Text(String(format: "%.1f%%", viewModel.progressPercentage))
                        .font(.headline)
                        .foregroundColor(.secondary)
                }
            }

            ProgressView(value: viewModel.progressPercentage, total: 100)
                .tint(.green)
                .scaleEffect(y: 2)
        }
    }

    // MARK: - Input Section

    private var inputSection: some View {
        VStack(spacing: 12) {
            if !viewModel.isSessionReady {
                HStack(spacing: 8) {
                    ProgressView()
                        .scaleEffect(0.8)
                    Text("Setting up session...")
                        .font(.subheadline)
                        .foregroundColor(.secondary)
                }
                .padding(.vertical, 8)
            }

            HStack(spacing: 12) {
                TextField("Enter player name...", text: $viewModel.guessText)
                    .textFieldStyle(.roundedBorder)
                    .font(.body)
                    .autocorrectionDisabled()
                    .textInputAutocapitalization(.words)
                    .focused($isInputFocused)
                    .submitLabel(.go)
                    .disabled(!viewModel.isSessionReady)
                    .onSubmit {
                        guard viewModel.isSessionReady else { return }
                        Task {
                            await viewModel.submitGuess()
                        }
                    }

                Button {
                    Task {
                        await viewModel.submitGuess()
                    }
                } label: {
                    if viewModel.isLoading {
                        ProgressView()
                            .tint(.white)
                    } else {
                        Image(systemName: "arrow.right.circle.fill")
                            .font(.title2)
                    }
                }
                .buttonStyle(.borderedProminent)
                .disabled(!viewModel.isSessionReady || viewModel.guessText.trimmingCharacters(in: .whitespaces).isEmpty || viewModel.isLoading)
            }

            Text("Enter first and last name (e.g., Lionel Messi)")
                .font(.caption)
                .foregroundColor(.secondary)
        }
    }

    // MARK: - Message View

    private var messageView: some View {
        HStack {
            Image(systemName: messageIcon)
            Text(viewModel.message)
                .font(.subheadline)
        }
        .foregroundColor(viewModel.messageType.color)
        .padding()
        .frame(maxWidth: .infinity)
        .background(viewModel.messageType.color.opacity(0.1))
        .cornerRadius(10)
    }

    private var messageIcon: String {
        switch viewModel.messageType {
        case .success: return "checkmark.circle.fill"
        case .error: return "xmark.circle.fill"
        case .warning: return "exclamationmark.triangle.fill"
        case .info: return "info.circle.fill"
        }
    }

    // MARK: - Last Guessed Player Card

    private func lastGuessedPlayerCard(_ player: PlayerDisplay) -> some View {
        VStack(alignment: .leading, spacing: 12) {
            HStack {
                Text("Last guessed")
                    .font(.caption)
                    .foregroundColor(.secondary)
                Spacer()
            }

            PlayerCardView(player: player, isCompact: false)
                .onTapGesture {
                    viewModel.selectPlayer(player)
                }
        }
        .sheet(isPresented: $viewModel.showPlayerDetail) {
            if let selected = viewModel.selectedPlayer {
                PlayerDetailSheet(player: selected)
            }
        }
    }
}

#Preview {
    GameTabView()
        .environmentObject(GameViewModel(databaseManager: DatabaseManager.shared))
}
