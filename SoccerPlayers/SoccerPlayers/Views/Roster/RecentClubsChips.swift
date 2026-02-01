import SwiftUI

/// Horizontal scrolling chips showing recently viewed clubs
struct RecentClubsChips: View {
    @ObservedObject var viewModel: RosterViewModel

    var body: some View {
        VStack(alignment: .leading, spacing: 8) {
            Text("Recent")
                .font(.caption)
                .foregroundColor(.secondary)

            ScrollView(.horizontal, showsIndicators: false) {
                HStack(spacing: 8) {
                    ForEach(viewModel.recentClubs) { club in
                        Button {
                            Task {
                                await viewModel.selectClub(club)
                            }
                        } label: {
                            HStack(spacing: 6) {
                                Image(systemName: club.isNationalTeam ? "flag.fill" : "building.2.fill")
                                    .font(.caption2)
                                    .foregroundColor(club.isNationalTeam ? .yellow : .blue)

                                Text(club.displayName)
                                    .font(.caption)
                                    .lineLimit(1)
                            }
                            .padding(.horizontal, 12)
                            .padding(.vertical, 8)
                            .background(Color(.systemGray6))
                            .cornerRadius(16)
                            .foregroundColor(.primary)
                        }
                    }
                }
            }
        }
    }
}

#Preview {
    VStack {
        RecentClubsChips(viewModel: RosterViewModel(databaseManager: DatabaseManager.shared))
        Spacer()
    }
    .padding()
}
