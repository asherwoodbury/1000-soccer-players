# Project Backlog

Last updated: 2026-02-08 16:00

> **Note:** iOS-specific tasks and App Store publishing checklist have been moved to [BACKLOG-IOS.md](BACKLOG-IOS.md)

## Category Index

### Performance (PERF)
| Item | Priority |
|------|----------|
| Database Query Optimization | LOW |
| Frontend Caching Strategy | LOW |
| Full-Text Search (FTS5) | COMPLETED |

### UX Improvements (UX)
| Item | Priority |
|------|----------|
| Smart Name Matching | COMPLETED |
| Recently Viewed Clubs Quick Access | COMPLETED |
| Clickable Team Links in Player Profiles | COMPLETED |
| Shorter National Team Names | COMPLETED |
| Dark Mode | COMPLETED |
| Clean Up Position Categories | HIGH |
| Fix Year Formatting in Roster Display | HIGH |
| Player Photos & Media | MEDIUM |
| Mobile Touch Improvements | MEDIUM |

### Bugs (BUG)
| Item | Priority |
|------|----------|
| Incorrect Team Assignments (Stale Data) | CRITICAL |

### Data (DATA)
| Item | Priority |
|------|----------|
| Football-data.org Extraction Tool | COMPLETED |
| Merge Football-data.org Data into players.db | HIGH |
| Cap Club History at 2025-26 Season | HIGH |
| Infer End Dates for Youth/Age-Restricted Teams | HIGH |
| Periodic Data Refresh Strategy | MEDIUM |
| Cross-Source Player Deduplication | MEDIUM |

### Game Features (GAME)
| Item | Priority |
|------|----------|
| Player Info Display Settings | COMPLETED |
| Team Roster Lookup | COMPLETED |
| Filter Guessed Players | COMPLETED |
| Expanded Leagues & National Teams | MEDIUM |
| Give Up and Reveal All Players | MEDIUM |
| Different Game Modes | LOW |
| Gamification Features | LOW |
| Additional Sports | MEDIUM |

### Meta Features (META)
| Item | Priority |
|------|----------|
| Native iOS App | COMPLETED |
| Multiplayer Mode | MEDIUM |
| Session Persistence Across Tabs | LOW |
| User Accounts & Authentication | LOW |
| Session Management UI | LOW |
| Competitive Mode | LOW |
| Social Sharing | MEDIUM |

### Other (OTHER)
| Item | Priority |
|------|----------|
| API Documentation Improvements | LOW |
| Automated Test Suite | LOW |
| Rate Limiting & Abuse Prevention | MEDIUM |
| Session ID Security | MEDIUM |
| Docker Containerization | MEDIUM |

---

## To Do

### Critical Priority

- **[BUG] Incorrect Team Assignments (Stale Data)**
  > Some players show incorrect current team assignments. Example: Nico Schulz shows as playing for Dortmund but no longer does.
  >
  > **Investigation needed:**
  > 1. Check if this is a Wikidata issue (stale data at source)
  > 2. Review sample of team rosters manually to assess scope
  > 3. Determine if end_date is missing/incorrect in player_clubs table
  > 4. Consider re-running extract_wikidata.py to refresh data
  > 5. May need to implement periodic data refresh strategy
  >
  > **Affected areas:** Player profiles, team rosters, "current team" indicators
  > Added: 2026-01-29

### High Priority

- **[DATA] Merge Football-data.org Data into players.db** - Priority: HIGH
  > Build an export/merge script that reads from `footballdata.db` and updates the game's `players.db` with enriched data. Key steps:
  > 1. Match `persons` in footballdata.db to `players` in players.db (by name + birth date + nationality)
  > 2. Import new players not already in players.db (fills gaps in Wikidata coverage)
  > 3. Update/correct club histories using match lineup data (more accurate than Wikidata's often-stale `member of sports team` property)
  > 4. Add missing clubs from footballdata.db `teams` table
  > 5. Handle conflicts gracefully (prefer football-data.org for recent seasons, Wikidata for older data)
  >
  > This directly addresses the CRITICAL "Incorrect Team Assignments" bug by providing a second, more reliable data source for recent seasons.
  > Added: 2026-02-07

- **[DATA] Cap Club History at 2025-26 Season** - Priority: HIGH
  > Club history and team roster data should not extend beyond the 2025-26 season. Currently, data from future seasons may appear if Wikidata or football-data.org sources contain forward-looking entries (e.g., pre-announced transfers for 2026-27).
  >
  > **Changes needed:**
  > 1. Add a season cap in the roster query logic (`clubs.py`) so that the year/season selector does not go beyond 2025-26
  > 2. Filter out `player_clubs` entries with `start_date` beyond the 2025-26 season during data import (extraction scripts)
  > 3. Ensure the `/clubs/{id}/years` endpoint returns a max year no later than 2025
  > 4. Apply the same cap in the iOS app's roster browsing
  >
  > Prevents confusion from speculative or pre-announced transfer data that has not actually taken effect yet.
  > Added: 2026-02-08

- **[DATA] Infer End Dates for Youth/Age-Restricted Teams** - Priority: HIGH
  > Youth and age-restricted team entries (U16, U17, U18, U19, U20, U21) in a player's club history may show as "active" (no end_date) even when the player has aged out. Fix this by inferring an end date based on the player's date of birth and the age category of the team.
  >
  > **Logic:**
  > - U16 team: end when player turns 17
  > - U17 team: end when player turns 18
  > - U18 team: end when player turns 19
  > - U19 team: end when player turns 20
  > - U20 team: end when player turns 21
  > - U21 team: end when player turns 22
  >
  > **Implementation approach:**
  > 1. Detect age-category teams by parsing club/team names for "U16", "U17", "U18", "U19", "U20", "U21", "under-16", "under-17", etc.
  > 2. For entries missing an `end_date`, calculate the inferred end date from the player's `birth_date` plus the corresponding age limit + 1 year
  > 3. Apply this as a data cleanup step (either at import time in extraction scripts or as a post-processing migration on `player_clubs`)
  > 4. Ensure the roster query and player profile display reflect the corrected end dates so these teams no longer appear as "Current"
  >
  > **Affected areas:** Player profiles (club history, "Current" badge), team rosters (youth team rosters showing aged-out players)
  > Added: 2026-02-08

- **[UX] Clean Up Position Categories**
  > Standardize position names throughout the Rosters page to reduce redundancy and confusion. Changes needed:
  > - Rename "Wing half" → "Winger"
  > - Unify "fullback" and "full-back" to single format
  > - Review other position variants for similar duplicates
  >
  > Affects web and iOS apps. Improves clarity when browsing rosters and filtering players by position.
  > Added: 2026-02-01

- **[UX] Fix Year Formatting in Roster Display**
  > Remove comma separators from year ranges in the Rosters page. Currently displays "2,024/25" but should display "2024/25". Affects both web and iOS apps throughout season year display.
  > Added: 2026-02-01

### Medium Priority

- **[DATA] Periodic Data Refresh Strategy** - Priority: MEDIUM
  > Establish a workflow for keeping player and club data up to date across both data sources. Considerations:
  > 1. Schedule regular re-runs of `extract_footballdata.py sync-all` for current/recent seasons
  > 2. Re-run the merge script after each sync to propagate updates to players.db
  > 3. Detect and flag players whose "current team" has changed (transfer window updates)
  > 4. Consider a lightweight delta-check mode that only fetches seasons with new matches
  >
  > Prevents the stale data problem from recurring after the initial merge fix.
  > Added: 2026-02-07

- **[DATA] Cross-Source Player Deduplication** - Priority: MEDIUM
  > After merging football-data.org data into players.db, audit for duplicate player entries that were not matched during import. Approach:
  > 1. Find players with very similar normalized names and overlapping career dates
  > 2. Use birth date as strong signal for matching (when available from both sources)
  > 3. Build a manual review tool or CSV export for borderline cases
  > 4. Merge duplicates by consolidating club histories and keeping the richer profile
  >
  > Ensures data quality after combining two independent data sources.
  > Added: 2026-02-07

- **[GAME] Expanded Leagues & National Teams**
  > Add player data from Portuguese (Primeira Liga), Dutch (Eredivisie), and Turkish (Süper Lig) leagues. Update extract_wikidata.py SPARQL queries to include these leagues. Also prioritize women's leagues and women's national teams with better Wikidata coverage.
  > Added: 2026-01-19 | Updated: 2026-01-27

- **[META] Multiplayer Mode**
  > Allow multiple users to join the same session and guess in parallel. Implement real-time or near-real-time progress synchronization so players can see each other's guesses, player counts, and session leaderboards. Will require WebSocket support or polling mechanism for live updates.
  > Added: 2026-01-19

- **[GAME] Give Up and Reveal All Players** - Priority: MEDIUM
  > Add a "Give Up" feature that ends the current session and reveals all unguessed players in the roster view. Once the user gives up, they should no longer be able to submit new guesses.
  >
  > **Backend changes:**
  > 1. Add a `given_up` boolean (or `given_up_at` timestamp) column to the `sessions` table
  > 2. Add a new endpoint (e.g., `POST /api/sessions/{id}/give-up`) to mark the session as given up
  > 3. Modify the guess endpoint (`POST /api/sessions/{id}/guess/{player_id}`) to reject guesses when the session is in a "given up" state
  > 4. Modify the roster endpoint to return full player names (instead of "?????") when the session is given up
  >
  > **Frontend changes:**
  > 1. Add a "Give Up" button (with confirmation dialog to prevent accidental clicks)
  > 2. After giving up, reveal all unguessed player names in the roster view so the user can see who they missed
  > 3. Disable the guess input field and submit button
  > 4. Display a summary showing total guessed vs. total available players
  > 5. Persist the given-up state so it survives page reloads
  >
  > **iOS app:** Will also need equivalent changes in the SwiftUI app if this feature is implemented on web first.
  > Added: 2026-02-08

- **[GAME] Additional Sports Integration**
  > Extend data model and extraction scripts to support basketball and baseball in addition to soccer. Create abstracted sport-agnostic schema and UI that can display relevant statistics for each sport.
  > Added: 2026-01-19

- **[OTHER] Rate Limiting & Abuse Prevention**
  > Implement rate limiting on API endpoints to prevent abuse if deployed publicly. Add IP-based throttling, request frequency caps, and monitoring for suspicious patterns.
  > Added: 2026-01-19

- **[OTHER] Session ID Security**
  > Replace auto-incrementing integer session IDs with UUIDs to prevent enumeration attacks and improve security for production deployment. Update both backend and frontend.
  > Added: 2026-01-19

- **[UX] Player Photos & Media**
  > Integrate player images from Wikidata commons. Display photos alongside player information to enhance UX and provide visual verification for guesses.
  > Added: 2026-01-19

- **[META] Social Sharing**
  > Add ability to share session results via social media (Twitter/X, Instagram). Generate shareable image with player count, top stats, and unique session code.
  > Added: 2026-01-19

- **[UX] Mobile Touch Improvements**
  > Enhance mobile experience: (1) Increase touch targets slightly, (2) Add swipe-to-dismiss on modal, (3) Consider bottom-sheet style modal on mobile, (4) Haptic feedback on successful guesses.
  > Added: 2026-01-19 | Source: UX Review

- **[OTHER] Docker Containerization**
  > Create Docker Compose configuration for easy deployment. Include backend, frontend, and database services with volume mounts for persistence.
  > Added: 2026-01-19

### Low Priority

- **[PERF] Database Query Optimization**
  > Profile and optimize player lookup queries, especially fuzzy matching performance. Add database indexes for frequently queried fields beyond normalized_name. Consider caching top 1000 most-guessed players in memory for instant lookups.
  > Added: 2026-01-19

- **[PERF] Frontend Caching Strategy**
  > Implement aggressive caching of player lookups to reduce API calls. Use IndexedDB for persistent cache, LRU cache in memory for current session. Add cache invalidation strategy when database is updated.
  > Added: 2026-01-19

- **[META] Session Persistence Across Tabs**
  > Sessions should persist when users open multiple tabs. Current implementation may lose session state or create duplicate sessions. Test with multiple browser tabs and implement session ID sharing mechanism.
  > Added: 2026-01-19

- **[META] User Accounts & Authentication**
  > Implement user registration, login, and session persistence across devices. Track lifetime statistics (total players guessed, sessions played, personal best). Allow users to resume incomplete sessions and compare stats with friends.
  > Added: 2026-01-19

- **[OTHER] Automated Test Suite**
  > Create pytest suite covering: (1) Player lookup with fuzzy matching, (2) Session management and guess recording, (3) Club/nationality filtering, (4) Ambiguity handling, (5) Name normalization edge cases. Aim for 80%+ coverage on backend logic.
  > Added: 2026-01-19

- **[META] Session Management UI**
  > Add a "New Game" button or settings menu with options to: (1) Reset current progress, (2) View session statistics, (3) Share progress with friends. Gives users control and reduces friction when wanting to restart.
  > Added: 2026-01-19 | Source: UX Review

- **[GAME] Gamification Features**
  > Add engagement mechanics: (1) Streaks for consecutive days played, (2) Category completion tracking (all players from a club/country), (3) Daily challenges with random player subsets to find. Increases retention and gives reasons to return.
  > Added: 2026-01-19 | Source: UX Review

- **[META] Competitive Mode**
  > Long-term competitive features: (1) Global leaderboards by sport/league, (2) Daily challenges with scoring algorithms, (3) Seasonal rankings, (4) Achievement badges, (5) Friend challenges with score multipliers.
  > Added: 2026-01-19

- **[UX] Roster Sharing Feature**
  > Add share button for completed or partial roster achievements. Generate shareable card or link showing roster completion percentage and highlighted guessed players. Enables social engagement and allows users to showcase progress.
  > Social feature to drive engagement and word-of-mouth promotion.
  > Added: 2026-01-26 | Source: UX Review

- **[OTHER] API Documentation Improvements**
  > Enhance Swagger/OpenAPI documentation with more detailed response examples, error codes, and ambiguity resolution flow. Add documentation for pagination (if implementing for large result sets).
  > Added: 2026-01-19

- **[GAME] Different Game Modes**
  > Implement multiple game variants: (1) Classic - guess as many players as possible, (2) Timed - 10 minute rounds, (3) Blind - only show position/nationality, no club history, (4) Club specialist - focus on specific club's entire roster.
  > Added: 2026-01-19

---

## Completed

- **[GAME] Player Info Display Settings**
  > Implemented configurable display preferences for player information shown after a successful guess. Five toggleable fields via Settings UI:
  > - Nationality (toggle)
  > - Position (toggle)
  > - Career Span, e.g. "2005-2020" or "2018-present" (toggle)
  > - Top 3 Clubs by appearances (toggle)
  > - Full Club History (toggle, requires Top 3 to be enabled)
  >
  > Settings persist in localStorage. Replaces the concept of "hints" with user-controlled display preferences.
  > Completed: 2026-01-26 | Commit: 85bc42d

- **[GAME] Team Roster Lookup**
  > Implemented exploration tool to help users recall players by browsing team rosters. Features:
  > - Backend API: /api/clubs/search (club search with autocomplete), /api/clubs/{id}/roster (roster retrieval), /api/clubs/{id}/years (season/year selection)
  > - Frontend: Dual-tab interface with "Guessed Players" and "Team Roster" tabs
  > - Club search with autocomplete, roster display with season navigation
  > - Guessed players shown in green, unguessed shown as "?????" (not revealed)
  > - Toggleable in Settings under "Exploration Tools"
  >
  > Active discovery tool separate from passive display settings.
  > Completed: 2026-01-26 | Commit: 85bc42d

- **[GAME] Filter Guessed Players**
  > Implemented filtering controls for the guessed players list to help users organize and review their progress:
  > - Position filter dropdown (Goalkeeper, Defender, Midfielder, Forward)
  > - Nationality filter dropdown (auto-populated from guessed players)
  > - Clear button to reset all active filters
  > - All filters work together with existing text search
  > - Nationality dropdown updates dynamically as new players are guessed
  >
  > Builds on existing filter infrastructure and helps users identify gaps in their knowledge by category.
  > Completed: 2026-01-27

- **[PERF] Full-Text Search (FTS5)**
  > Implemented SQLite FTS5 virtual table with unicode61 tokenizer for comprehensive full-text search capabilities. Features:
  > - FTS5 virtual table with auto-sync triggers to keep index updated
  > - fts_search() function for fast prefix-based player lookup
  > - fts_search_fuzzy() function combining FTS5 with Levenshtein distance filtering
  > - Handles common typos: "ronaldino" → Ronaldinho, "naymar" → Neymar, "christiano" → Cristiano
  > - Seamlessly integrated into /api/players/lookup endpoint as fallback when exact/prefix match fails
  >
  > Significantly improves UX for users making typos and expands fuzzy matching capabilities beyond Levenshtein distance alone.
  > Completed: 2026-01-27

- **[UX] Smart Name Matching**
  > Comprehensive name matching system that balances usability with game integrity. Features:
  > - **Typo tolerance**: FTS5 + Levenshtein distance with length-based thresholds (0 edits for ≤4 chars, 1 for 5-8, 2 for 9+)
  > - **First + last name requirement**: Players must be guessed with full name (e.g., "Lionel Messi" not just "Messi")
  > - **Mononym support**: ~50 players known by single names (Pelé, Neymar, Ronaldinho, etc.) can be guessed with one name
  > - **Length ratio check**: Prevents "Ronaldo" from matching "Ronaldinho" (must be within 20% length)
  > - **Phonetic algorithms**: Soundex and Metaphone for sound-alike matching
  >
  > Design decision: Disambiguation UI (showing candidates when multiple players match) was intentionally omitted to keep the game challenging. When ambiguous, users must provide more specific names.
  >
  > Key files: `fuzzy_matching.py`, `database.py` (FTS5 functions), `players.py` (KNOWN_MONONYMS)
  > Completed: 2026-01-27 | Combines: FTS5, fuzzy matching algorithms, first+last name requirement

- **[UX] Recently Viewed Clubs Quick Access**
  > Quick access to recently viewed clubs in Team Roster Lookup. Features:
  > - Stores up to 5 most recently viewed clubs in localStorage
  > - Displays as clickable chips below the search input
  > - Clicking a chip immediately loads that club's roster
  > - **Active club highlighting**: Currently viewed club is highlighted in blue
  > - **Clear button**: × button to clear all recent clubs
  > - Chips have hover/focus states, staggered animations, and responsive design
  > - List updates automatically when new clubs are viewed (most recent first)
  >
  > Speeds up workflow for users who frequently browse the same team rosters.
  > Key files: `frontend/app.js` (recentClubs state, render functions), `frontend/styles.css` (.recent-club-chip)
  > Completed: 2026-01-27

- **[UX] Clickable Team Links in Player Profiles**
  > All team names in player profiles are now clickable, navigating to that team's roster. Features:
  > - **Nationality link**: Clicks navigate to the national team roster (searches for "[Country] national team")
  > - **Top Clubs links**: Each club name is clickable, opens that club's roster
  > - **Full Club History links**: Every club/team in the history is clickable
  > - **Current team highlighting**: Teams where player is still active (no end_date) show:
  >   - Blue gradient background in club history
  >   - "Current" badge next to the team name
  >   - Bold text in top clubs list
  >
  > Creates seamless navigation between player profiles and team rosters for exploration.
  > Key files: `frontend/app.js` (navigateToClubRoster, navigateToNationalTeam), `frontend/styles.css` (.club-link, .current-club)
  > Completed: 2026-01-27

- **[BUG] Team Roster Shows Too Many Players**
  > Team rosters are showing far too many players (Dortmund: 79, Juventus: 200+). Fixed by filtering corrupted dates and adding tenure heuristic to properly filter players by season. The roster query now correctly includes only players active in the selected season.
  > Completed: 2026-01-29

- **[BUG] Roster Doesn't Update When Guessing Player From Current Team**
  > When viewing a team's roster and guessing a player from that team, the roster now updates in real-time. Fixed by calling loadRoster() after a successful guess to refresh the roster display with updated player status.
  > Completed: 2026-01-29

- **[UX] Shorter National Team Names**
  > Implemented format_national_team_name() function to rename national teams to shorter, more readable format:
  > - "Argentina men's national association football team" → "Argentina (M)"
  > - "Germany women's national football team" → "Germany (W)"
  > - "Brazil national under-20 football team" → "Brazil U20"
  > - "France national under-23 football team" → "France U23"
  > Affects display in player profiles, roster headers, and search results throughout the UI.
  > Completed: 2026-01-29

- **[DATA] Prioritize Senior National Teams**
  > Implemented get_national_team_priority() function to prioritize top men's and women's senior teams over youth teams in search results. Senior national teams now appear at the top when searching and are the default when clicking a nationality link, improving user experience when exploring teams by country.
  > Completed: 2026-01-29

- **[META] Native iOS App**
  > Built native SwiftUI iOS app (iOS 17+) with full offline capability. See [BACKLOG-IOS.md](BACKLOG-IOS.md) for iOS-specific tasks and details.
  > Completed: 2026-01-29

- **[UX] Dark Mode**
  > Implemented dark mode theme with automatic detection via prefers-color-scheme media query and manual toggle in settings. Features:
  > - **Theme Options**: System (default), Light, Dark
  > - **CSS Variables**: All colors converted to theme-aware CSS variables (--bg-primary, --text-primary, --border-color, etc.)
  > - **Persistence**: Theme preference stored in localStorage for persistence across sessions
  > - **Auto Detection**: Respects user's system dark mode preference if "System" is selected
  > - **Smooth Transitions**: Subtle fade transitions when switching themes
  > - **Full Coverage**: Dark mode applied throughout web app including modals, cards, input fields, and all interactive elements
  >
  > Enhances accessibility and reduces eye strain during extended play sessions. Provides better user experience for night-time usage.
  > Completed: 2026-02-07

- **[META] Reset Progress Button**
  > Added "Reset Progress" button to settings modal allowing users to clear all guessed players and start fresh. Includes confirmation dialog showing current player count before resetting.
  > Completed: 2026-02-07

- **[DATA] Football-data.org Extraction Tool**
  > Built `backend/scripts/extract_footballdata.py` -- a self-contained extraction tool for football-data.org's free API tier. Features:
  > - **Subcommands**: `sync-teams`, `sync-matches`, `sync-lineups`, `sync-all`, `stats`
  > - **12 free-tier competitions**: PL, BL1, PD, SA, FL1, DED, PPL, ELC, BSA, CL, WC, EC
  > - **Season range**: 2000-2025
  > - **Separate database**: Stores in `backend/data/footballdata.db` (does not touch players.db)
  > - **Raw API response caching**: `api_responses` table with hash-based deduplication avoids redundant API calls
  > - **3-layer resumability**: (1) API response cache skips already-fetched endpoints, (2) `sync_status` table tracks completed competition/season/step combos, (3) UNIQUE constraints prevent duplicate parsed records
  > - **Structured tables**: competitions, teams, persons, matches, match_lineups, team_competitions
  > - **API key resolution**: CLI flag, environment variable, or `.env` file
  > - **Rate limiting**: Built-in request throttling for free-tier limits
  > - **Zero project dependencies**: Uses only stdlib (urllib, sqlite3, json) -- copy-pasteable to other projects
  >
  > Provides a second, independent data source to cross-reference and correct Wikidata's often-stale club assignments.
  > Key file: `backend/scripts/extract_footballdata.py`
  > Completed: 2026-02-07
