import SwiftUI

/// Filter bar for the player list
struct FilterBar: View {
    @ObservedObject var viewModel: PlayerListViewModel
    @ObservedObject var gameViewModel: GameViewModel

    var body: some View {
        VStack(spacing: 10) {
            // Search field
            HStack {
                Image(systemName: "magnifyingglass")
                    .foregroundColor(.secondary)

                TextField("Search players or clubs...", text: $viewModel.searchText)
                    .textFieldStyle(.plain)
                    .autocorrectionDisabled()

                if !viewModel.searchText.isEmpty {
                    Button {
                        viewModel.searchText = ""
                    } label: {
                        Image(systemName: "xmark.circle.fill")
                            .foregroundColor(.secondary)
                    }
                }
            }
            .padding(10)
            .background(Color(.systemGray6))
            .cornerRadius(10)

            // Filter chips
            ScrollView(.horizontal, showsIndicators: false) {
                HStack(spacing: 8) {
                    // Sort order
                    Menu {
                        ForEach(PlayerListViewModel.SortOrder.allCases, id: \.self) { order in
                            Button {
                                viewModel.sortOrder = order
                            } label: {
                                HStack {
                                    Text(order.rawValue)
                                    if viewModel.sortOrder == order {
                                        Image(systemName: "checkmark")
                                    }
                                }
                            }
                        }
                    } label: {
                        filterChip(
                            icon: "arrow.up.arrow.down",
                            text: viewModel.sortOrder.rawValue,
                            isActive: viewModel.sortOrder != .recent
                        )
                    }

                    // Position filter
                    if !gameViewModel.uniquePositions.isEmpty {
                        Menu {
                            Button {
                                viewModel.selectedPosition = nil
                            } label: {
                                HStack {
                                    Text("All Positions")
                                    if viewModel.selectedPosition == nil {
                                        Image(systemName: "checkmark")
                                    }
                                }
                            }

                            Divider()

                            ForEach(gameViewModel.uniquePositions, id: \.self) { position in
                                Button {
                                    viewModel.selectedPosition = position
                                } label: {
                                    HStack {
                                        Text(position)
                                        if viewModel.selectedPosition == position {
                                            Image(systemName: "checkmark")
                                        }
                                    }
                                }
                            }
                        } label: {
                            filterChip(
                                icon: "sportscourt.fill",
                                text: viewModel.selectedPosition ?? "Position",
                                isActive: viewModel.selectedPosition != nil
                            )
                        }
                    }

                    // Nationality filter
                    if !gameViewModel.uniqueNationalities.isEmpty {
                        Menu {
                            Button {
                                viewModel.selectedNationality = nil
                            } label: {
                                HStack {
                                    Text("All Nationalities")
                                    if viewModel.selectedNationality == nil {
                                        Image(systemName: "checkmark")
                                    }
                                }
                            }

                            Divider()

                            ForEach(gameViewModel.uniqueNationalities, id: \.self) { nationality in
                                Button {
                                    viewModel.selectedNationality = nationality
                                } label: {
                                    HStack {
                                        Text(nationality)
                                        if viewModel.selectedNationality == nationality {
                                            Image(systemName: "checkmark")
                                        }
                                    }
                                }
                            }
                        } label: {
                            filterChip(
                                icon: "flag.fill",
                                text: viewModel.selectedNationality ?? "Nationality",
                                isActive: viewModel.selectedNationality != nil
                            )
                        }
                    }

                    // Clear all button
                    if viewModel.hasActiveFilters {
                        Button {
                            viewModel.clearFilters()
                        } label: {
                            filterChip(
                                icon: "xmark",
                                text: "Clear",
                                isActive: false,
                                color: .red
                            )
                        }
                    }
                }
            }
        }
    }

    private func filterChip(
        icon: String,
        text: String,
        isActive: Bool,
        color: Color = .blue
    ) -> some View {
        HStack(spacing: 4) {
            Image(systemName: icon)
                .font(.caption2)
            Text(text)
                .font(.caption)
        }
        .padding(.horizontal, 10)
        .padding(.vertical, 6)
        .background(isActive ? color.opacity(0.2) : Color(.systemGray6))
        .foregroundColor(isActive ? color : .primary)
        .cornerRadius(16)
    }
}

#Preview {
    VStack {
        FilterBar(
            viewModel: PlayerListViewModel(),
            gameViewModel: GameViewModel(databaseManager: DatabaseManager.shared)
        )
        Spacer()
    }
    .padding()
}
