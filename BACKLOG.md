# Project Backlog

Last updated: 2026-01-19

## In Progress
<!-- Tasks currently being worked on -->

## To Do

### Critical Priority
<!-- Tasks that block other work or are urgent -->

- **[FEATURE] Multiplayer Mode** - Priority: CRITICAL
  > Allow multiple users to join the same session and guess in parallel. Implement real-time or near-real-time progress synchronization so players can see each other's guesses, player counts, and session leaderboards. This is a foundational feature that will significantly expand the game's appeal and differentiate it from single-player alternatives. Will require WebSocket support or polling mechanism for live updates.
  > Added: 2026-01-19 | Status: To Do

- **[BUG] Session Persistence Across Tabs** - Priority: CRITICAL
  > Sessions should persist when users open multiple tabs. Current implementation may lose session state or create duplicate sessions. Test with multiple browser tabs and implement session ID sharing mechanism.
  > Added: 2026-01-19 | Status: To Do

### High Priority
<!-- Important tasks that should be done soon -->

- **[FEATURE] Hint System** - Priority: HIGH
  > Implement hints to assist player recall: (1) Show team rosters with blanks for unguessed players, (2) Toggle difficulty by hiding/showing positions, (3) Toggle visibility of player birth years, (4) Progressive hint levels (show position → show year → show nationality). This feature should be optional and track hint usage for competitive scoring.
  > Added: 2026-01-19 | Status: To Do

- **[FEATURE] Native iOS App** - Priority: HIGH
  > Build React Native mobile application that connects to the existing FastAPI backend. Current REST API architecture supports this. Should share session management with web version and support offline caching of player data.
  > Added: 2026-01-19 | Status: To Do

- **[FEATURE] Expanded Leagues** - Priority: HIGH
  > Add player data from Portuguese (Primeira Liga), Dutch (Eredivisie), and Turkish (Süper Lig) leagues. Update extract_wikidata.py SPARQL queries to include these leagues. Prioritize women's leagues with better Wikidata coverage.
  > Added: 2026-01-19 | Status: To Do

- **[FEATURE] User Accounts & Authentication** - Priority: HIGH
  > Implement user registration, login, and session persistence across devices. Track lifetime statistics (total players guessed, sessions played, personal best). Allow users to resume incomplete sessions and compare stats with friends.
  > Added: 2026-01-19 | Status: To Do

- **[FEATURE] Full-Text Search** - Priority: HIGH
  > Migrate from simple prefix matching to SQLite FTS5 for better fuzzy matching on misspelled player names. This will significantly improve UX for users making typos (e.g., "Christiano" → "Cristiano Ronaldo").
  > Added: 2026-01-19 | Status: To Do

- **[UX] Autocomplete Hints for Player Names** - Priority: HIGH
  > Add "Did you mean..." suggestions after failed lookups to help with spelling of international names. Could show phonetically similar matches without revealing the full player list. Reduces frustration from typos.
  > Added: 2026-01-19 | Status: To Do | Source: UX Review

- **[PERF] Database Query Optimization** - Priority: HIGH
  > Profile and optimize player lookup queries, especially fuzzy matching performance. Add database indexes for frequently queried fields beyond normalized_name. Consider caching top 1000 most-guessed players in memory for instant lookups.
  > Added: 2026-01-19 | Status: To Do

- **[DOCS] API Documentation Improvements** - Priority: HIGH
  > Enhance Swagger/OpenAPI documentation with more detailed response examples, error codes, and ambiguity resolution flow. Add documentation for pagination (if implementing for large result sets).
  > Added: 2026-01-19 | Status: To Do

- **[TEST] Add Automated Test Suite** - Priority: HIGH
  > Create pytest suite covering: (1) Player lookup with fuzzy matching, (2) Session management and guess recording, (3) Club/nationality filtering, (4) Ambiguity handling, (5) Name normalization edge cases. Aim for 80%+ coverage on backend logic.
  > Added: 2026-01-19 | Status: To Do

### Medium Priority
<!-- Standard development work -->

- **[UX] Progress Visualization** - Priority: MEDIUM
  > Add a visual progress bar beneath the player count showing progress toward 1000. Include milestone markers at 100, 250, 500, 750, 1000 with optional achievement badges (e.g., "Century Club" at 100). Creates stronger sense of accomplishment and goal proximity.
  > Added: 2026-01-19 | Status: To Do | Source: UX Review

- **[UX] Session Management UI** - Priority: MEDIUM
  > Add a "New Game" button or settings menu with options to: (1) Reset current progress, (2) View session statistics, (3) Share progress with friends. Gives users control and reduces friction when wanting to restart.
  > Added: 2026-01-19 | Status: To Do | Source: UX Review

- **[UX] Gamification Features** - Priority: MEDIUM
  > Add engagement mechanics: (1) Streaks for consecutive days played, (2) Category completion tracking (all players from a club/country), (3) Daily challenges with random player subsets to find. Increases retention and gives reasons to return.
  > Added: 2026-01-19 | Status: To Do | Source: UX Review

- **[FEATURE] Different Game Modes** - Priority: MEDIUM
  > Implement multiple game variants: (1) Classic - guess as many players as possible, (2) Timed - 10 minute rounds, (3) Blind - only show position/nationality, no club history, (4) Club specialist - focus on specific club's entire roster.
  > Added: 2026-01-19 | Status: To Do

- **[FEATURE] Competitive Mode** - Priority: MEDIUM
  > Long-term competitive features: (1) Global leaderboards by sport/league, (2) Daily challenges with scoring algorithms, (3) Seasonal rankings, (4) Achievement badges, (5) Friend challenges with score multipliers.
  > Added: 2026-01-19 | Status: To Do

- **[FEATURE] Additional Sports Integration** - Priority: MEDIUM
  > Extend data model and extraction scripts to support basketball and baseball in addition to soccer. Create abstracted sport-agnostic schema and UI that can display relevant statistics for each sport (e.g., height/weight for basketball, ERA/RBIs for baseball).
  > Added: 2026-01-19 | Status: To Do

- **[UX] Improved Ambiguity Resolution** - Priority: MEDIUM
  > Enhance UX when multiple players match a name: (1) Show thumbnail photos of matching players, (2) Display nationality/club/position inline to help disambiguation, (3) Quick select from list rather than typing again.
  > Added: 2026-01-19 | Status: To Do

- **[UX] Player Statistics Dashboard** - Priority: MEDIUM
  > Display session-specific stats: (1) Distribution by nationality, (2) Distribution by position, (3) Distribution by league, (4) Current streak, (5) Average time between guesses. Include charts/visualizations.
  > Added: 2026-01-19 | Status: To Do

- **[INFRA] Rate Limiting & Abuse Prevention** - Priority: MEDIUM
  > Implement rate limiting on extraction scripts to prevent abuse if deployed publicly. Add IP-based throttling, request frequency caps, and monitoring for suspicious patterns. Document in CLAUDE.md.
  > Added: 2026-01-19 | Status: To Do

- **[INFRA] Session ID Security** - Priority: MEDIUM
  > Replace auto-incrementing integer session IDs with UUIDs to prevent enumeration attacks and improve security for production deployment. Update both backend and frontend.
  > Added: 2026-01-19 | Status: To Do

- **[PERF] Frontend Caching Strategy** - Priority: MEDIUM
  > Implement aggressive caching of player lookups to reduce API calls. Use IndexedDB for persistent cache, LRU cache in memory for current session. Add cache invalidation strategy when database is updated.
  > Added: 2026-01-19 | Status: To Do

- **[REFACTOR] Extract Player Matching Logic** - Priority: MEDIUM
  > Refactor fuzzy matching logic from routers/players.py into a separate PlayerMatcher service class. Improves testability and allows reuse across different endpoints (mobile app, alternative UIs).
  > Added: 2026-01-19 | Status: To Do

### Low Priority
<!-- Nice-to-have improvements, can be deferred -->

- **[FEATURE] Player Photos & Media** - Priority: LOW
  > Integrate player images from Wikidata commons. Display photos alongside player information to enhance UX and provide visual verification for guesses. Handle missing/broken image links gracefully.
  > Added: 2026-01-19 | Status: To Do

- **[FEATURE] Social Sharing** - Priority: LOW
  > Add ability to share session results via social media (Twitter/X, Instagram). Generate shareable image with player count, top stats, and unique session code. Allow friends to view public leaderboards without joining.
  > Added: 2026-01-19 | Status: To Do

- **[FEATURE] Voice Input** - Priority: LOW
  > Add speech recognition for player guesses on web and mobile. Improves accessibility and adds fun factor to gameplay.
  > Added: 2026-01-19 | Status: To Do

- **[FEATURE] Export Player Data** - Priority: LOW
  > Allow users to export their guessed player list as CSV or JSON. Useful for analysis, sharing with friends, or external tools.
  > Added: 2026-01-19 | Status: To Do

- **[UX] Enhanced Empty State** - Priority: LOW
  > Improve the empty state with engaging content: (1) Example player names as inspiration, (2) Suggested categories to explore ("Start with World Cup winners", "Premier League legends"), (3) Random "Did you know?" facts about players. Reduces blank page paralysis.
  > Added: 2026-01-19 | Status: To Do | Source: UX Review

- **[UX] Mobile Touch Improvements** - Priority: LOW
  > Enhance mobile experience: (1) Increase touch targets slightly, (2) Add swipe-to-dismiss on modal, (3) Consider bottom-sheet style modal on mobile, (4) Haptic feedback on successful guesses.
  > Added: 2026-01-19 | Status: To Do | Source: UX Review

- **[UX] Dark Mode** - Priority: LOW
  > Implement dark mode theme toggle in frontend. Persist theme preference in localStorage. Improve contrast and eye comfort for long play sessions.
  > Added: 2026-01-19 | Status: To Do

- **[INFRA] Docker Containerization** - Priority: LOW
  > Create Docker Compose configuration for easy deployment. Include backend, frontend, and database services with volume mounts for persistence.
  > Added: 2026-01-19 | Status: To Do

- **[DOCS] Video Tutorial** - Priority: LOW
  > Create short video tutorial (2-3 min) showing how to play the game, use filters, and understand game mechanics. Host on project README.
  > Added: 2026-01-19 | Status: To Do

## Completed

- **[FEAT] FastAPI Backend with SQLite Database** - Priority: HIGH
  > Created backend application with FastAPI framework, implemented SQLite schema for players, clubs, player_clubs, sessions, and guessed_players tables. Set up database connection management, migrations, and initial schema creation in app/models/database.py.
  > Added: 2026-01-19 | Completed: 2026-01-19

- **[FEAT] Player Lookup with Fuzzy Matching** - Priority: HIGH
  > Implemented player lookup endpoint with name normalization (lowercase, diacritics removal), exact match first approach, then prefix matching. Handles ambiguous matches by returning multiple results with user prompt for disambiguation.
  > Added: 2026-01-19 | Completed: 2026-01-19

- **[FEAT] Session Management** - Priority: HIGH
  > Implemented session creation, retrieval, and guess recording endpoints. Sessions track all guessed players with timestamps. Prevents duplicate guesses within a session.
  > Added: 2026-01-19 | Completed: 2026-01-19

- **[FEAT] Club and Nationality Filtering** - Priority: HIGH
  > Implemented session filtering endpoints to retrieve guessed players filtered by club or nationality. Supports career history filtering across multiple clubs and national team selections.
  > Added: 2026-01-19 | Completed: 2026-01-19

- **[FEAT] Wikidata Extraction Scripts** - Priority: HIGH
  > Created extract_sample.py for quick testing (20 players) and extract_wikidata.py for full extraction (47k+ players). Scripts query Wikidata SPARQL API for player data including name, nationality, position, club history. Supports efficient batching and error handling.
  > Added: 2026-01-19 | Completed: 2026-01-19

- **[FEAT] Vanilla JavaScript Frontend** - Priority: HIGH
  > Built responsive single-page application with vanilla JavaScript (no frameworks). Features include player search input, session creation, result display with club history, club/nationality filtering, and mobile-friendly UI with CSS variables for theming.
  > Added: 2026-01-19 | Completed: 2026-01-19

- **[FEAT] CORS Configuration** - Priority: MEDIUM
  > Configured CORS in FastAPI backend to allow requests from localhost:3000 and localhost:5173 for development. Set up proper origin validation for secure cross-origin requests.
  > Added: 2026-01-19 | Completed: 2026-01-19

- **[FEAT] Session Persistence in LocalStorage** - Priority: MEDIUM
  > Implemented localStorage caching of session ID on frontend for persistence across page reloads. Backend remains stateless with all progress stored in database.
  > Added: 2026-01-19 | Completed: 2026-01-19

- **[DOCS] Comprehensive Project Documentation** - Priority: HIGH
  > Created OVERVIEW.md with full project architecture, data model documentation, API endpoint reference, technology stack, and development guidelines. Included setup instructions and security considerations.
  > Added: 2026-01-19 | Completed: 2026-01-19

- **[DOCS] CLAUDE.md Development Guidance** - Priority: MEDIUM
  > Created CLAUDE.md with build/run commands, architecture overview, key design patterns, and code organization reference for AI assistance during development.
  > Added: 2026-01-19 | Completed: 2026-01-19

- **[INFRA] Run Script for Local Development** - Priority: MEDIUM
  > Created run.sh script that starts both FastAPI backend (port 8000) and frontend server (port 3000) simultaneously with single command for convenient local development.
  > Added: 2026-01-19 | Completed: 2026-01-19

- **[UX] Accessibility Enhancements** - Priority: HIGH
  > Added ARIA labels to inputs/buttons, role="dialog" on modal, keyboard navigation (Enter/Space) for player cards, proper focus management (modal captures focus, restores on close).
  > Added: 2026-01-19 | Completed: 2026-01-19 | Source: UX Review

- **[UX] Loading States and Animations** - Priority: MEDIUM
  > Added loading spinner on Guess button during API calls, count bump animation on successful guess, slide-in animation for new player cards, fade/slide transitions for messages, modal open animations.
  > Added: 2026-01-19 | Completed: 2026-01-19 | Source: UX Review

- **[UX] Micro-interactions** - Priority: LOW
  > Added hover lift effect on player cards, button press effect, focus-visible outlines with proper offset, focus ring shadows on inputs.
  > Added: 2026-01-19 | Completed: 2026-01-19 | Source: UX Review

- **[FEAT] Club History Batch Fetching Script** - Priority: HIGH
  > Created fetch_club_histories.py to efficiently fetch club histories for players in batches of 50 using SPARQL queries. Much faster than individual queries for large datasets.
  > Added: 2026-01-19 | Completed: 2026-01-19
