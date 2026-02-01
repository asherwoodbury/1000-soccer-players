import SwiftUI

/// Grid view displaying a club's roster
struct RosterGridView: View {
    let roster: RosterResponse
    let guessedPlayerIds: Set<Int64>

    var body: some View {
        ScrollView {
            VStack(alignment: .leading, spacing: 16) {
                // Player count
                HStack {
                    Text("\(roster.totalCount) players")
                        .font(.subheadline)
                        .foregroundColor(.secondary)

                    Spacer()
                }
                .padding(.horizontal)
                .padding(.top, 8)

                // Group by position
                let groupedPlayers = Dictionary(grouping: roster.players) { $0.position ?? "Unknown" }
                let sortedPositions = groupedPlayers.keys.sorted { p1, p2 in
                    positionOrder(p1) < positionOrder(p2)
                }

                ForEach(sortedPositions, id: \.self) { position in
                    if let players = groupedPlayers[position] {
                        positionSection(position: position, players: players)
                    }
                }
            }
            .padding(.bottom, 20)
        }
    }

    private func positionSection(position: String, players: [RosterPlayer]) -> some View {
        VStack(alignment: .leading, spacing: 8) {
            Text(position)
                .font(.headline)
                .padding(.horizontal)

            LazyVGrid(columns: [
                GridItem(.flexible(), spacing: 8),
                GridItem(.flexible(), spacing: 8)
            ], spacing: 8) {
                ForEach(players) { player in
                    playerCell(player)
                }
            }
            .padding(.horizontal)
        }
    }

    private func playerCell(_ player: RosterPlayer) -> some View {
        let isGuessed = guessedPlayerIds.contains(player.id)

        return VStack(alignment: .leading, spacing: 4) {
            Text(isGuessed ? player.name : "?????")
                .font(.subheadline)
                .fontWeight(.medium)
                .lineLimit(1)
                .foregroundColor(isGuessed ? .primary : .secondary)

            if let startYear = player.startYear {
                let endYear = player.endYear.map { String($0) } ?? "present"
                Text("\(startYear)-\(endYear)")
                    .font(.caption2)
                    .foregroundColor(.secondary)
            }
        }
        .padding(10)
        .frame(maxWidth: .infinity, alignment: .leading)
        .background(isGuessed ? Color.green.opacity(0.15) : Color(.secondarySystemBackground))
        .cornerRadius(8)
        .overlay(
            RoundedRectangle(cornerRadius: 8)
                .stroke(isGuessed ? Color.green.opacity(0.5) : Color.clear, lineWidth: 1)
        )
    }

    /// Returns a sort order for positions (Goalkeeper first, then defenders, midfielders, forwards)
    private func positionOrder(_ position: String) -> Int {
        let lowercased = position.lowercased()
        if lowercased.contains("goalkeeper") || lowercased.contains("keeper") {
            return 0
        } else if lowercased.contains("defender") || lowercased.contains("back") {
            return 1
        } else if lowercased.contains("midfielder") || lowercased.contains("mid") {
            return 2
        } else if lowercased.contains("forward") || lowercased.contains("striker") || lowercased.contains("winger") {
            return 3
        }
        return 4 // Unknown positions last
    }
}

#Preview {
    RosterGridView(
        roster: RosterResponse(
            clubId: 1,
            clubName: "FC Barcelona",
            displayName: "FC Barcelona",
            season: "2023/24",
            players: [
                RosterPlayer(id: 1, name: "Marc-Andre ter Stegen", position: "Goalkeeper", startYear: 2014, endYear: nil),
                RosterPlayer(id: 2, name: "Ronald Araujo", position: "Defender", startYear: 2020, endYear: nil),
                RosterPlayer(id: 3, name: "Jules Kounde", position: "Defender", startYear: 2022, endYear: nil),
                RosterPlayer(id: 4, name: "Pedri", position: "Midfielder", startYear: 2020, endYear: nil),
                RosterPlayer(id: 5, name: "Gavi", position: "Midfielder", startYear: 2021, endYear: nil),
                RosterPlayer(id: 6, name: "Lamine Yamal", position: "Forward", startYear: 2023, endYear: nil),
                RosterPlayer(id: 7, name: "Robert Lewandowski", position: "Forward", startYear: 2022, endYear: nil)
            ],
            totalCount: 7
        ),
        guessedPlayerIds: [1, 4, 7] // Sample: ter Stegen, Pedri, and Lewandowski guessed
    )
}
