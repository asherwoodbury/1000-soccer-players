import SwiftUI

/// Sheet displaying full player details including career history
struct PlayerDetailSheet: View {
    let player: PlayerDisplay
    @Environment(\.dismiss) private var dismiss

    var body: some View {
        NavigationStack {
            ScrollView {
                VStack(alignment: .leading, spacing: 20) {
                    // Header
                    headerSection

                    Divider()

                    // Career timeline
                    if !player.clubs.isEmpty {
                        careerSection
                    }
                }
                .padding()
            }
            .navigationTitle(player.name)
            .navigationBarTitleDisplayMode(.inline)
            .toolbar {
                ToolbarItem(placement: .navigationBarTrailing) {
                    Button("Done") {
                        dismiss()
                    }
                }
            }
        }
    }

    // MARK: - Header Section

    private var headerSection: some View {
        VStack(alignment: .leading, spacing: 12) {
            HStack(spacing: 16) {
                // Player icon placeholder
                Circle()
                    .fill(Color(.systemGray4))
                    .frame(width: 80, height: 80)
                    .overlay {
                        Text(player.name.prefix(1))
                            .font(.largeTitle)
                            .fontWeight(.bold)
                            .foregroundColor(.secondary)
                    }

                VStack(alignment: .leading, spacing: 6) {
                    if let nationality = player.nationality {
                        Label(nationality, systemImage: "flag.fill")
                            .font(.subheadline)
                    }

                    if let position = player.position {
                        Label(position, systemImage: "sportscourt.fill")
                            .font(.subheadline)
                    }

                    if let careerSpan = player.careerSpan {
                        Label(careerSpan, systemImage: "calendar")
                            .font(.subheadline)
                    }
                }
            }

            // Top clubs
            if !player.topClubs.isEmpty {
                VStack(alignment: .leading, spacing: 6) {
                    Text("Top Clubs")
                        .font(.caption)
                        .foregroundColor(.secondary)

                    HStack(spacing: 8) {
                        ForEach(player.topClubs, id: \.self) { club in
                            Text(club)
                                .font(.caption)
                                .padding(.horizontal, 10)
                                .padding(.vertical, 6)
                                .background(Color.blue.opacity(0.1))
                                .foregroundColor(.blue)
                                .cornerRadius(8)
                        }
                    }
                }
            }
        }
    }

    // MARK: - Career Section

    private var careerSection: some View {
        VStack(alignment: .leading, spacing: 12) {
            Text("Career History")
                .font(.headline)

            // Separate clubs and national teams
            let clubs = player.clubs.filter { !$0.isNationalTeam }
            let nationalTeams = player.clubs.filter { $0.isNationalTeam }

            if !clubs.isEmpty {
                Text("Clubs")
                    .font(.subheadline)
                    .foregroundColor(.secondary)
                    .padding(.top, 4)

                ForEach(clubs) { club in
                    clubRow(club)
                }
            }

            if !nationalTeams.isEmpty {
                Text("National Teams")
                    .font(.subheadline)
                    .foregroundColor(.secondary)
                    .padding(.top, 8)

                ForEach(nationalTeams) { team in
                    clubRow(team)
                }
            }
        }
    }

    private func clubRow(_ club: ClubHistory) -> some View {
        HStack {
            Circle()
                .fill(club.isNationalTeam ? Color.yellow.opacity(0.3) : Color.blue.opacity(0.3))
                .frame(width: 8, height: 8)

            Text(club.displayName)
                .font(.subheadline)

            Spacer()

            Text(formatDateRange(start: club.startDate, end: club.endDate))
                .font(.caption)
                .foregroundColor(.secondary)
        }
        .padding(.vertical, 4)
    }

    private func formatDateRange(start: String?, end: String?) -> String {
        let startYear = start.map { String($0.prefix(4)) } ?? "?"
        let endYear = end.map { String($0.prefix(4)) } ?? "present"
        return "\(startYear)-\(endYear)"
    }
}

#Preview {
    PlayerDetailSheet(
        player: PlayerDisplay(
            player: Player(
                id: 1,
                wikidataId: "Q1",
                name: "Lionel Messi",
                normalizedName: "lionel messi",
                firstName: "Lionel",
                lastName: "Messi",
                nationality: "Argentina",
                nationalityCode: "AR",
                position: "Forward",
                birthDate: "1987-06-24",
                gender: "male",
                createdAt: nil
            ),
            clubs: [
                ClubHistory(name: "FC Barcelona", displayName: "FC Barcelona",
                           startDate: "2004-10-16", endDate: "2021-08-10", isNationalTeam: false),
                ClubHistory(name: "Paris Saint-Germain", displayName: "Paris Saint-Germain",
                           startDate: "2021-08-10", endDate: "2023-07-15", isNationalTeam: false),
                ClubHistory(name: "Inter Miami", displayName: "Inter Miami",
                           startDate: "2023-07-15", endDate: nil, isNationalTeam: false),
                ClubHistory(name: "Argentina men's national football team", displayName: "Argentina (M)",
                           startDate: "2005-08-17", endDate: nil, isNationalTeam: true)
            ],
            topClubs: ["FC Barcelona", "Paris Saint-Germain", "Inter Miami"],
            careerSpan: "2004-present"
        )
    )
}
