# Project Backlog

Last updated: 2026-01-29 14:32

## Category Index

### Performance (PERF)
| Item | Priority |
|------|----------|
| Database Query Optimization | HIGH |
| Frontend Caching Strategy | HIGH |
| Full-Text Search (FTS5) | COMPLETED |

### UX Improvements (UX)
| Item | Priority |
|------|----------|
| Smart Name Matching | COMPLETED |
| Recently Viewed Clubs Quick Access | COMPLETED |
| Clickable Team Links in Player Profiles | COMPLETED |
| Shorter National Team Names | COMPLETED |
| Dark Mode | HIGH |
| Progress Visualization | MEDIUM |
| Player Statistics Dashboard | LOW |
| Player Photos & Media | MEDIUM |
| Enhanced Empty State | MEDIUM |
| Mobile Touch Improvements | MEDIUM |
| Filter Roster by Guessed/Unguessed | LOW |

### Bugs (BUG)
| Item | Priority |
|------|----------|

### Data (DATA)
| Item | Priority |
|------|----------|

### Game Features (GAME)
| Item | Priority |
|------|----------|
| Player Info Display Settings | COMPLETED |
| Team Roster Lookup | COMPLETED |
| Filter Guessed Players | COMPLETED |
| Expanded Leagues & National Teams | HIGH |
| Category Progress Indicators | MEDIUM |
| Same Team Indicator | MEDIUM |
| Different Game Modes | LOW |
| Gamification Features | MEDIUM |
| Additional Sports | MEDIUM |

### Meta Features (META)
| Item | Priority |
|------|----------|
| Native iOS App | HIGH |
| Multiplayer Mode | MEDIUM |
| Session Persistence Across Tabs | MEDIUM |
| User Accounts & Authentication | MEDIUM |
| Session Management UI | MEDIUM |
| Competitive Mode | MEDIUM |
| Social Sharing | MEDIUM |

### Other (OTHER)
| Item | Priority |
|------|----------|
| API Documentation Improvements | LOW |
| Automated Test Suite | MEDIUM |
| Rate Limiting & Abuse Prevention | MEDIUM |
| Session ID Security | MEDIUM |
| Docker Containerization | MEDIUM |

---

## To Do

### Critical Priority

- **[PERF] Database Query Optimization**
  > Profile and optimize player lookup queries, especially fuzzy matching performance. Add database indexes for frequently queried fields beyond normalized_name. Consider caching top 1000 most-guessed players in memory for instant lookups.
  > Added: 2026-01-19

- **[PERF] Frontend Caching Strategy**
  > Implement aggressive caching of player lookups to reduce API calls. Use IndexedDB for persistent cache, LRU cache in memory for current session. Add cache invalidation strategy when database is updated.
  > Added: 2026-01-19

- **[UX] Dark Mode**
  > Implement dark mode theme toggle in frontend. Persist theme preference in localStorage. Improve contrast and eye comfort for long play sessions.
  > Added: 2026-01-19

- **[META] Native iOS App**
  > Build React Native mobile application that connects to the existing FastAPI backend. Current REST API architecture supports this. Should share session management with web version and support offline caching of player data.
  > Added: 2026-01-19

- **[GAME] Expanded Leagues & National Teams**
  > Add player data from Portuguese (Primeira Liga), Dutch (Eredivisie), and Turkish (Süper Lig) leagues. Update extract_wikidata.py SPARQL queries to include these leagues. Also prioritize women's leagues and women's national teams with better Wikidata coverage.
  > Added: 2026-01-19 | Updated: 2026-01-27

### Medium Priority

- **[UX] Season Jumping in Roster Navigation**
  > Replace or augment prev/next buttons in Team Roster with dropdown or direct input for quick navigation to historical seasons. Consider adding decade jump buttons as optional feature for rapid navigation across large date ranges.
  > Reduces friction when exploring team histories across many seasons.
  > Added: 2026-01-26 | Source: UX Review

- **[GAME] Category Progress Indicators**
  > Show completion percentages by category to motivate collection and reveal knowledge gaps. Example: "German players: 47/312 (15%)", "Goalkeepers: 23/89 (26%)".
  >
  > **Needs refinement:** Determine the right categories to track. Candidates include:
  > - By nationality (top 10-20 countries?)
  > - By position (4 main positions)
  > - By league (top 5 leagues + women's)
  > - By decade (1990s, 2000s, 2010s, 2020s)
  > - By club (major clubs only?)
  >
  > Should be toggleable - some users may find this motivating, others overwhelming.
  > Added: 2026-01-25 | Status: Needs design refinement

- **[GAME] Same Team Indicator**
  > When a player is guessed, optionally show how many players from their notable teams have been guessed. Example: "You've now guessed 3/5 players from 2015 Barcelona" or "4 players from Germany national team."
  >
  > Creates mini collection goals and encourages users to complete team rosters. Should be toggleable in Settings.
  >
  > **Needs refinement:** Determine which teams to highlight (all clubs? just notable ones? national teams?), and how to calculate roster sizes.
  > Added: 2026-01-25 | Status: Needs design refinement

- **[META] Multiplayer Mode**
  > Allow multiple users to join the same session and guess in parallel. Implement real-time or near-real-time progress synchronization so players can see each other's guesses, player counts, and session leaderboards. Will require WebSocket support or polling mechanism for live updates.
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

- **[UX] Progress Visualization**
  > Add a visual progress bar beneath the player count showing progress toward 1000. Include milestone markers at 100, 250, 500, 750, 1000 with optional achievement badges (e.g., "Century Club" at 100). Creates stronger sense of accomplishment and goal proximity.
  > Added: 2026-01-19 | Source: UX Review

- **[META] Session Management UI**
  > Add a "New Game" button or settings menu with options to: (1) Reset current progress, (2) View session statistics, (3) Share progress with friends. Gives users control and reduces friction when wanting to restart.
  > Added: 2026-01-19 | Source: UX Review

- **[GAME] Gamification Features**
  > Add engagement mechanics: (1) Streaks for consecutive days played, (2) Category completion tracking (all players from a club/country), (3) Daily challenges with random player subsets to find. Increases retention and gives reasons to return.
  > Added: 2026-01-19 | Source: UX Review

- **[META] Competitive Mode**
  > Long-term competitive features: (1) Global leaderboards by sport/league, (2) Daily challenges with scoring algorithms, (3) Seasonal rankings, (4) Achievement badges, (5) Friend challenges with score multipliers.
  > Added: 2026-01-19

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

- **[UX] Enhanced Empty State**
  > Improve the empty state with engaging content: (1) Example player names as inspiration, (2) Suggested categories to explore, (3) Random "Did you know?" facts about players.
  > Added: 2026-01-19 | Source: UX Review

- **[UX] Mobile Touch Improvements**
  > Enhance mobile experience: (1) Increase touch targets slightly, (2) Add swipe-to-dismiss on modal, (3) Consider bottom-sheet style modal on mobile, (4) Haptic feedback on successful guesses.
  > Added: 2026-01-19 | Source: UX Review

- **[OTHER] Docker Containerization**
  > Create Docker Compose configuration for easy deployment. Include backend, frontend, and database services with volume mounts for persistence.
  > Added: 2026-01-19

### Low Priority

- **[UX] Filter Roster by Guessed/Unguessed**
  > Add toggle filter to Team Roster Lookup feature: "All | Guessed | Unguessed" to help users find gaps in their knowledge for specific teams. Users can focus on which players they haven't identified yet or review their completed rosters.
  > Pairs well with existing Filter Guessed Players feature and leverages current Team Roster exploration infrastructure.
  > Added: 2026-01-26 | Source: UX Review

- **[UX] Roster Progress Indicator**
  > Add visual progress bar showing roster completion percentage for currently viewed team, with color transitions as completion increases. Display mini-goal/milestone tracker to encourage roster completion (e.g., "3/23 players guessed").
  > Creates visual feedback and encourages users to complete specific team rosters as side goals.
  > Added: 2026-01-26 | Source: UX Review

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

- **[UX] Player Statistics Dashboard**
  > Display session-specific stats: (1) Distribution by nationality, (2) Distribution by position, (3) Distribution by league, (4) Current streak, (5) Average time between guesses. Include charts/visualizations.
  > Added: 2026-01-19

---

## Completed

- **[FEAT] FastAPI Backend with SQLite Database**
  > Created backend application with FastAPI framework, implemented SQLite schema for players, clubs, player_clubs, sessions, and guessed_players tables.
  > Completed: 2026-01-19

- **[FEAT] Player Lookup with Fuzzy Matching**
  > Implemented player lookup endpoint with name normalization (lowercase, diacritics removal), exact match first approach, then prefix matching.
  > Completed: 2026-01-19

- **[FEAT] Session Management**
  > Implemented session creation, retrieval, and guess recording endpoints. Prevents duplicate guesses within a session.
  > Completed: 2026-01-19

- **[FEAT] Club and Nationality Filtering**
  > Implemented session filtering endpoints to retrieve guessed players filtered by club or nationality.
  > Completed: 2026-01-19

- **[FEAT] Wikidata Extraction Scripts**
  > Created extract_sample.py for quick testing and extract_wikidata.py for full extraction (47k+ players).
  > Completed: 2026-01-19

- **[FEAT] Club History Batch Fetching Script**
  > Created fetch_club_histories.py to efficiently fetch club histories in batches of 50 using SPARQL queries.
  > Completed: 2026-01-19

- **[FEAT] Vanilla JavaScript Frontend**
  > Built responsive single-page application with vanilla JavaScript. Mobile-friendly UI with CSS variables.
  > Completed: 2026-01-19

- **[FEAT] CORS Configuration**
  > Configured CORS in FastAPI backend for localhost development servers.
  > Completed: 2026-01-19

- **[FEAT] Session Persistence in LocalStorage**
  > Implemented localStorage caching of session ID for persistence across page reloads.
  > Completed: 2026-01-19

- **[UX] Accessibility Enhancements**
  > Added ARIA labels, keyboard navigation, proper focus management for modal.
  > Completed: 2026-01-19 | Source: UX Review

- **[UX] Loading States and Animations**
  > Added loading spinner, count bump animation, slide-in for new cards, fade/slide transitions.
  > Completed: 2026-01-19 | Source: UX Review

- **[UX] Micro-interactions**
  > Added hover lift effect, button press effect, focus-visible outlines.
  > Completed: 2026-01-19 | Source: UX Review

- **[DOCS] Comprehensive Project Documentation**
  > Created OVERVIEW.md with architecture, data model, API reference, and development guidelines.
  > Completed: 2026-01-19

- **[DOCS] CLAUDE.md Development Guidance**
  > Created CLAUDE.md with build/run commands, architecture overview, agent workflows.
  > Completed: 2026-01-19

- **[INFRA] Run Script with Virtual Environment**
  > Created run.sh that auto-creates venv, installs dependencies, starts both servers.
  > Completed: 2026-01-19

- **[OTHER] Refactor Player Matching Logic**
  > Refactored matching logic into `PlayerMatcher` service class in `backend/app/services/player_matcher.py`. Created separate `fuzzy_matching.py` module with Levenshtein distance, Soundex, and Metaphone algorithms. Added 67 unit tests with full coverage. Improves testability and enables Smart Name Matching feature.
  > Completed: 2026-01-25

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
