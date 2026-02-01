# 1000 Soccer Players - iOS App

A native SwiftUI iOS app for the soccer player guessing game. Features full offline capability with a bundled 47k+ player SQLite database.

## Requirements

- iOS 17.0+
- Xcode 15.0+
- Swift 5.9+

## Setup

1. Open `SoccerPlayers.xcodeproj` in Xcode
2. Wait for Swift Package Manager to resolve dependencies (GRDB.swift)
3. Ensure the `players.db` file is in the Resources folder
4. Build and run on a simulator or device

## Architecture

The app follows MVVM architecture with SwiftUI:

```
SoccerPlayers/
├── SoccerPlayersApp.swift          # App entry point
├── Models/                          # GRDB data models
│   ├── Player.swift
│   ├── Club.swift
│   ├── PlayerClub.swift
│   ├── Session.swift
│   └── GuessedPlayer.swift
├── Services/
│   ├── Database/                    # Database layer
│   │   ├── DatabaseManager.swift    # Connection & setup
│   │   ├── PlayerRepository.swift   # Player queries & search
│   │   ├── ClubRepository.swift     # Club/roster queries
│   │   └── SessionRepository.swift  # Session management
│   └── Search/                      # Search algorithms
│       ├── NameNormalizer.swift     # Unicode normalization
│       ├── FuzzyMatcher.swift       # Levenshtein distance
│       └── PlayerMatcher.swift      # Search orchestration
├── ViewModels/                      # UI logic
│   ├── GameViewModel.swift          # Guessing logic
│   ├── PlayerListViewModel.swift    # Filtering
│   ├── RosterViewModel.swift        # Club rosters
│   └── SettingsViewModel.swift      # Preferences
├── Views/                           # SwiftUI views
│   ├── Main/
│   │   ├── ContentView.swift        # Tab container
│   │   └── GameTabView.swift        # Guess input
│   ├── Players/
│   │   ├── GuessedPlayersView.swift # Player list
│   │   ├── PlayerCardView.swift     # Player card
│   │   ├── PlayerDetailSheet.swift  # Full career
│   │   └── FilterBar.swift          # Filters
│   ├── Roster/
│   │   ├── RosterTabView.swift      # Club rosters
│   │   ├── ClubSearchView.swift
│   │   ├── RecentClubsChips.swift
│   │   └── RosterGridView.swift
│   └── Settings/
│       └── SettingsView.swift
└── Utilities/
    ├── Constants.swift              # Mononyms list
    └── NationalTeamFormatter.swift  # Team name formatting
```

## Features

### Game Tab
- Enter player names to guess
- Full name required (first + last), except for known mononyms (Pele, Neymar, etc.)
- Fuzzy matching handles typos (e.g., "Christiano" → "Cristiano Ronaldo")
- Progress tracking with visual feedback

### Players Tab
- View all guessed players
- Filter by position, nationality
- Search by name or club
- Sort by recent, alphabetical, position, or nationality
- Tap to view full career history

### Rosters Tab
- Search for any club or national team
- Browse roster by season
- National teams sorted with senior teams first
- Recent clubs for quick access

### Settings
- Toggle display options (nationality, position, clubs, career span)
- Compact mode
- Reset progress
- Database info

## Dependencies

- [GRDB.swift](https://github.com/groue/GRDB.swift) v6.24+ - SQLite toolkit

## Database

The app bundles a ~48MB SQLite database containing:
- 47,000+ players from Wikidata
- Club histories with dates
- FTS5 full-text search index

On first launch, the database is copied from the app bundle to the Documents directory.

## Key Algorithms

### Name Normalization
- Unicode NFKD decomposition
- Diacritics removal (accents, umlauts)
- Lowercase conversion
- Whitespace normalization

### Fuzzy Matching
- FTS5 prefix search for candidates
- Levenshtein distance scoring
- Prefix variations for typo tolerance
- Phonetic matching (Soundex)

### Search Strategy
1. Exact match on normalized name
2. Prefix match
3. FTS5 full-text search
4. Fuzzy search with distance thresholds

## Building for Release

1. Archive the project in Xcode
2. The bundled database compresses to ~20MB in the App Store
3. Ensure code signing is configured for your team

## License

MIT License
