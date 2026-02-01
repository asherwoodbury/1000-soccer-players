import SwiftUI

/// Card view displaying a player's information
struct PlayerCardView: View {
    let player: PlayerDisplay
    let isCompact: Bool

    @AppStorage("showNationality") private var showNationality = true
    @AppStorage("showPosition") private var showPosition = true
    @AppStorage("showClubs") private var showClubs = true
    @AppStorage("showCareerSpan") private var showCareerSpan = false

    var body: some View {
        VStack(alignment: .leading, spacing: isCompact ? 6 : 10) {
            // Header: Name and metadata
            HStack {
                Text(player.name)
                    .font(isCompact ? .headline : .title3)
                    .fontWeight(.semibold)
                    .lineLimit(1)

                Spacer()

                if showCareerSpan, let span = player.careerSpan {
                    Text(span)
                        .font(.caption)
                        .foregroundColor(.secondary)
                }
            }

            // Metadata row
            HStack(spacing: 12) {
                if showNationality, let nationality = player.nationality {
                    Label(nationality, systemImage: "flag.fill")
                        .font(.caption)
                        .foregroundColor(.secondary)
                }

                if showPosition, let position = player.position {
                    Label(position, systemImage: "sportscourt.fill")
                        .font(.caption)
                        .foregroundColor(.secondary)
                }
            }

            // Top clubs
            if showClubs && !player.topClubs.isEmpty {
                HStack(spacing: 8) {
                    ForEach(player.topClubs, id: \.self) { club in
                        Text(club)
                            .font(.caption2)
                            .padding(.horizontal, 8)
                            .padding(.vertical, 4)
                            .background(Color(.systemGray5))
                            .cornerRadius(6)
                    }
                }
            }
        }
        .padding(isCompact ? 12 : 16)
        .frame(maxWidth: .infinity, alignment: .leading)
        .background(Color(.secondarySystemBackground))
        .cornerRadius(12)
    }
}

#Preview {
    VStack {
        PlayerCardView(
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
                clubs: [],
                topClubs: ["Barcelona", "Paris Saint-Germain", "Inter Miami"],
                careerSpan: "2004-present"
            ),
            isCompact: false
        )

        PlayerCardView(
            player: PlayerDisplay(
                player: Player(
                    id: 2,
                    wikidataId: "Q2",
                    name: "Cristiano Ronaldo",
                    normalizedName: "cristiano ronaldo",
                    firstName: "Cristiano",
                    lastName: "Ronaldo",
                    nationality: "Portugal",
                    nationalityCode: "PT",
                    position: "Forward",
                    birthDate: "1985-02-05",
                    gender: "male",
                    createdAt: nil
                ),
                clubs: [],
                topClubs: ["Real Madrid", "Manchester United", "Juventus"],
                careerSpan: "2002-present"
            ),
            isCompact: true
        )
    }
    .padding()
}
