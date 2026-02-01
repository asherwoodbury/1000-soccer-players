import SwiftUI

/// Search field for finding clubs
struct ClubSearchView: View {
    @ObservedObject var viewModel: RosterViewModel

    var body: some View {
        HStack {
            Image(systemName: "magnifyingglass")
                .foregroundColor(.secondary)

            TextField("Search clubs...", text: $viewModel.searchText)
                .textFieldStyle(.plain)
                .autocorrectionDisabled()
                .textInputAutocapitalization(.words)
                .onChange(of: viewModel.searchText) { _, _ in
                    Task {
                        try? await Task.sleep(nanoseconds: 300_000_000) // 300ms debounce
                        await viewModel.searchClubs()
                    }
                }

            if viewModel.isSearching {
                ProgressView()
                    .scaleEffect(0.8)
            } else if !viewModel.searchText.isEmpty {
                Button {
                    viewModel.searchText = ""
                    viewModel.searchResults = []
                } label: {
                    Image(systemName: "xmark.circle.fill")
                        .foregroundColor(.secondary)
                }
            }
        }
        .padding(12)
        .background(Color(.systemGray6))
        .cornerRadius(10)
    }
}

#Preview {
    VStack {
        ClubSearchView(viewModel: RosterViewModel(databaseManager: DatabaseManager.shared))
        Spacer()
    }
    .padding()
}
