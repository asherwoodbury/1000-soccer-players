# Project Backlog

Last updated: 2026-02-09 15:00

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
| Clean Up Position Categories | COMPLETED |
| Fix Year Formatting in Roster Display | COMPLETED |
| Separate Club and National Team History | HIGH |
| Sort Roster Players by Popularity | MEDIUM |
| Player Photos & Media | MEDIUM |
| Mobile Touch Improvements | MEDIUM |

### Bugs (BUG)
| Item | Priority |
|------|----------|
| Incorrect Team Assignments (Stale Data) | COMPLETED |
| Malformed End Dates in Club History (URLs in Date Fields) | COMPLETED |
| Overlapping Club Stints Due to Missing End Dates | COMPLETED |

### Data (DATA)
| Item | Priority |
|------|----------|
| Football-data.org Extraction Tool | COMPLETED |
| Merge Football-data.org Data into players.db | COMPLETED |
| Cap Club History at 2025-26 Season | COMPLETED |
| Infer End Dates for Youth/Age-Restricted Teams | COMPLETED |
| Periodic Data Refresh Strategy | MEDIUM |
| Cross-Source Player Deduplication | MEDIUM |

### Game Features (GAME)
| Item | Priority |
|------|----------|
| Player Info Display Settings | COMPLETED |
| Team Roster Lookup | COMPLETED |
| Filter Guessed Players | COMPLETED |
| Expanded Leagues & National Teams | MEDIUM |
| Give Up and Reveal All Players | COMPLETED |
| Post-Game Summary Screen | LOW |
| Revealed Player Enrichment | MEDIUM |
| Styled Give-Up Confirmation Dialog | LOW |
| Better Roster Visual Differentiation | LOW |
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

### High Priority

- **[UX] Separate Club and National Team History** - Priority: HIGH
  > Group club teams and national teams into distinct sections in the player club history display. Currently, club and national team entries are interleaved chronologically, making career history harder to read at a glance.
  >
  > **Changes needed:**
  > 1. Split the player's club history into two labeled groups: "Club Career" and "International Career"
  > 2. Use the existing `is_national_team` boolean on `player_clubs` entries to determine grouping
  > 3. Within each group, maintain chronological ordering
  > 4. Apply to the full club history view in the player profile modal (web frontend)
  > 5. Apply the same grouping in the iOS app's player detail view
  >
  > This is primarily a frontend/display change -- the backend already returns the `is_national_team` flag with each club history entry, so no API changes should be needed. Improves readability and follows the convention used on sites like Wikipedia and Transfermarkt.
  > Added: 2026-02-09

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

- **[GAME] Revealed Player Enrichment** - Priority: MEDIUM
  > When clicking revealed players in roster view after giving up, fetch full player details (clubs, career span, nationality) so the modal shows the same rich data as guessed players. Currently only shows name/position from roster data. Makes the post-game experience educational.
  > Added: 2026-02-08 | Source: UX Review

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

- **[UX] Sort Roster Players by Popularity** - Priority: MEDIUM
  > Players in the team roster drilldown view are not sorted in a meaningful order. They should be sorted by some measure of popularity or importance so that the most recognizable players appear first, making it easier for users to scan rosters and recall names.
  >
  > **Possible sorting metrics (TBD -- may require experimentation):**
  > 1. **Minutes played per season** -- available in `match_lineups` data from football-data.org; most directly reflects importance to the team in a given season
  > 2. **Appearances per season** -- simpler variant of minutes; count of matches the player appeared in
  > 3. **Wikipedia page views** -- proxy for general fame/recognizability; would require a new data source (Wikimedia REST API)
  > 4. **Career caps / total appearances** -- available from Wikidata for some players; biased toward older players
  > 5. **Composite score** -- combine multiple signals (e.g., appearances + page views) for a balanced ranking
  >
  > **Implementation considerations:**
  > - May need a `popularity_score` or `sort_order` column on `player_clubs` or a separate ranking table
  > - The roster API endpoint (`/api/clubs/{id}/roster`) would need to return players in the new order
  > - Fallback sorting (e.g., alphabetical) needed for players without ranking data
  > - Should apply to both web and iOS roster views
  >
  > The exact metric is open for experimentation. Starting with appearance counts from football-data.org lineup data may be the lowest-effort first step since that data is already in the system.
  > Added: 2026-02-09

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

- **[GAME] Post-Game Summary Screen** - Priority: LOW
  > Show a summary overlay after giving up with stats: total guessed count, percentage, top nationalities guessed, position breakdown. Creates an emotional endpoint to the game session. Include a "Browse Results" button to dismiss.
  > Added: 2026-02-08 | Source: UX Review

- **[UX] Styled Give-Up Confirmation Dialog** - Priority: LOW
  > Replace browser `confirm()` with an in-app styled dialog matching the game's visual language. Possibly add a brief undo toast after giving up. Maintains friction while keeping the experience polished.
  > Added: 2026-02-08 | Source: UX Review

- **[UX] Better Roster Visual Differentiation** - Priority: LOW
  > Use distinct background colors instead of opacity for revealed vs guessed players. Add a legend/icons at top of roster explaining color coding. Consider a toggle to filter "only guessed" or "only revealed."
  > Added: 2026-02-08 | Source: UX Review

- **[OTHER] API Documentation Improvements**
  > Enhance Swagger/OpenAPI documentation with more detailed response examples, error codes, and ambiguity resolution flow. Add documentation for pagination (if implementing for large result sets).
  > Added: 2026-01-19

- **[GAME] Different Game Modes**
  > Implement multiple game variants: (1) Classic - guess as many players as possible, (2) Timed - 10 minute rounds, (3) Blind - only show position/nationality, no club history, (4) Club specialist - focus on specific club's entire roster.
  > Added: 2026-01-19

---

## Completed

- **[BUG] Malformed End Dates in Club History (URLs in Date Fields)**
  > Fixed malformed dates in `player_clubs` where `end_date` or `start_date` contained URL fragments (e.g., `'http://www'`) or garbage strings (e.g., `'20009-01-0'`) from naive `[:10]` slicing on Wikidata URI values. Added `sanitize_dates()` to `database.py` that NULLs out any date not matching `YYYY-MM-DD` or `YYYY` patterns, called on every DB init. Added `parse_wikidata_date()` validation helper to extraction scripts to prevent future insertion of non-date values. Cleaned ~287 existing rows.
  > Completed: 2026-02-11

- **[BUG] Overlapping Club Stints Due to Missing End Dates**
  > Fixed ~11k players showing simultaneous memberships at multiple clubs due to missing `end_date` values from Wikidata. Added `infer_club_end_dates()` to `database.py` that sets each non-national-team club's `end_date` to the `start_date` of the player's next chronological club, using a single SQL update. Resolves cases like Willy Caballero appearing at both Chelsea and Boca Juniors simultaneously.
  > Completed: 2026-02-11

- **[GAME] Give Up and Reveal All Players**
  > Implemented "Give Up" feature allowing users to end a session and reveal all unguessed players.
  > - Backend: Added `given_up_at` column to sessions table, `POST /sessions/{id}/give-up` endpoint, guess rejection when session is given up, `given_up` field in session response models
  > - Frontend: Give Up button in settings modal with confirmation dialog, input/submit disabled after giving up, roster view reveals all player names (guessed in green, revealed in muted grey), revealed players clickable with basic modal, state persists across reloads
  > - CSS: Revealed player styling (reduced opacity), disabled input styling, warning-colored give-up button
  > Completed: 2026-02-08

- **[UX] Clean Up Position Categories**
  > Standardized position names throughout the Rosters page to reduce redundancy and confusion:
  > - Renamed "Wing half" to "Winger"
  > - Unified "fullback" and "full-back" to single format
  > - Reviewed and consolidated other position variant duplicates
  >
  > Affects web and iOS apps. Improves clarity when browsing rosters and filtering players by position.
  > Completed: 2026-02-08

- **[UX] Fix Year Formatting in Roster Display**
  > Removed comma separators from year ranges in the Rosters page. Previously displayed "2,024/25", now correctly displays "2024/25". Fixed in both web and iOS apps throughout season year display.
  > Completed: 2026-02-08

- **[DATA] Cap Club History at 2025-26 Season**
  > Club history and team roster data no longer extends beyond the 2025-26 season. Implemented season cap in roster query logic, filtered out player_clubs entries with start_date beyond the 2025-26 season, and ensured the /clubs/{id}/years endpoint returns a max year no later than 2025. Prevents confusion from speculative or pre-announced transfer data.
  > Completed: 2026-02-08

- **[DATA] Infer End Dates for Youth/Age-Restricted Teams**
  > Youth and age-restricted team entries (U16-U21) in player club histories now have inferred end dates based on the player's date of birth and the team's age category. Players who have aged out no longer show as "Current" on youth teams. Implemented as a data cleanup step affecting player profiles and team rosters.
  > Completed: 2026-02-08

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

- **[BUG] Incorrect Team Assignments (Stale Data)**
  > Fixed by merging football-data.org squad data into players.db. Added `is_stale` flag to `player_clubs` table to mark outdated records where a player's current team is unclear. Stale records show as "Unconfirmed" in the UI instead of "Current". End dates are inferred from sequential transfers in FD data, and pre-FD records get end dates based on when the player's first FD club started.
  > Completed: 2026-02-08

- **[DATA] Merge Football-data.org Data into players.db**
  > Built `backend/scripts/merge_footballdata.py` — a 4-step merge script:
  > 1. **Schema migration**: Added `is_stale` column to `player_clubs`, created `club_aliases` table
  > 2. **Club matching**: Matched 230/259 FD teams to game DB clubs via normalized names, suffix stripping, and bootstrap alias mapping
  > 3. **Player matching**: Matched 2,761/10,796 FD persons by name (+ DOB disambiguation for ambiguous names)
  > 4. **Association updates**: Added 1,734 new player-club links, marked 958 stale records, inferred 1,952 end dates from transfer sequences
  >
  > Also updated `clubs.py` to filter stale records from rosters/search and search club aliases, and `players.py`/frontend to expose and display the stale flag.
  > Completed: 2026-02-08

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
