# Project Backlog

Last updated: 2026-01-19

## Category Index

### Performance (PERF)
| Item | Priority |
|------|----------|
| Full-Text Search (FTS5) | MEDIUM |
| Database Query Optimization | MEDIUM |
| Frontend Caching Strategy | MEDIUM |

### UX Improvements (UX)
| Item | Priority |
|------|----------|
| Autocomplete Hints | HIGH |
| Improved Ambiguity Resolution | HIGH |
| Progress Visualization | MEDIUM |
| Player Statistics Dashboard | LOW |
| Player Photos & Media | MEDIUM |
| Enhanced Empty State | MEDIUM |
| Mobile Touch Improvements | MEDIUM |
| Dark Mode | MEDIUM |

### Game Features (GAME)
| Item | Priority |
|------|----------|
| Hint System | HIGH |
| Expanded Leagues | MEDIUM |
| Different Game Modes | LOW |
| Gamification Features | MEDIUM |
| Additional Sports | MEDIUM |

### Meta Features (META)
| Item | Priority |
|------|----------|
| Multiplayer Mode | MEDIUM |
| Session Persistence Across Tabs | MEDIUM |
| Native iOS App | MEDIUM |
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
| Refactor Player Matching Logic | MEDIUM |
| Docker Containerization | MEDIUM |

---

## In Progress
<!-- Tasks currently being worked on -->

---

## To Do

### High Priority

- **[GAME] Hint System**
  > Implement hints to assist player recall: (1) Show team rosters with blanks for unguessed players, (2) Toggle difficulty by hiding/showing positions, (3) Toggle visibility of player birth years, (4) Progressive hint levels. This feature should be optional and track hint usage for competitive scoring.
  > Added: 2026-01-19

- **[UX] Improved Ambiguity Resolution**
  > Enhance UX when multiple players match a name: (1) Show thumbnail photos of matching players, (2) Display nationality/club/position inline to help disambiguation, (3) Quick select from list rather than typing again.
  > Added: 2026-01-19

- **[UX] Autocomplete Hints for Player Names**
  > Add "Did you mean..." suggestions after failed lookups to help with spelling of international names. Could show phonetically similar matches without revealing the full player list. Reduces frustration from typos.
  > Added: 2026-01-19 | Source: UX Review

### Medium Priority

- **[META] Multiplayer Mode**
  > Allow multiple users to join the same session and guess in parallel. Implement real-time or near-real-time progress synchronization so players can see each other's guesses, player counts, and session leaderboards. Will require WebSocket support or polling mechanism for live updates.
  > Added: 2026-01-19

- **[META] Session Persistence Across Tabs**
  > Sessions should persist when users open multiple tabs. Current implementation may lose session state or create duplicate sessions. Test with multiple browser tabs and implement session ID sharing mechanism.
  > Added: 2026-01-19

- **[META] Native iOS App**
  > Build React Native mobile application that connects to the existing FastAPI backend. Current REST API architecture supports this. Should share session management with web version and support offline caching of player data.
  > Added: 2026-01-19

- **[GAME] Expanded Leagues**
  > Add player data from Portuguese (Primeira Liga), Dutch (Eredivisie), and Turkish (Süper Lig) leagues. Update extract_wikidata.py SPARQL queries to include these leagues. Prioritize women's leagues with better Wikidata coverage.
  > Added: 2026-01-19

- **[META] User Accounts & Authentication**
  > Implement user registration, login, and session persistence across devices. Track lifetime statistics (total players guessed, sessions played, personal best). Allow users to resume incomplete sessions and compare stats with friends.
  > Added: 2026-01-19

- **[PERF] Full-Text Search**
  > Migrate from simple prefix matching to SQLite FTS5 for better fuzzy matching on misspelled player names. This will significantly improve UX for users making typos (e.g., "Christiano" → "Cristiano Ronaldo").
  > Added: 2026-01-19

- **[PERF] Database Query Optimization**
  > Profile and optimize player lookup queries, especially fuzzy matching performance. Add database indexes for frequently queried fields beyond normalized_name. Consider caching top 1000 most-guessed players in memory for instant lookups.
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

- **[PERF] Frontend Caching Strategy**
  > Implement aggressive caching of player lookups to reduce API calls. Use IndexedDB for persistent cache, LRU cache in memory for current session. Add cache invalidation strategy when database is updated.
  > Added: 2026-01-19

- **[OTHER] Refactor Player Matching Logic**
  > Refactor fuzzy matching logic from routers/players.py into a separate PlayerMatcher service class. Improves testability and allows reuse across different endpoints.
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

- **[UX] Dark Mode**
  > Implement dark mode theme toggle in frontend. Persist theme preference in localStorage. Improve contrast and eye comfort for long play sessions.
  > Added: 2026-01-19

- **[OTHER] Docker Containerization**
  > Create Docker Compose configuration for easy deployment. Include backend, frontend, and database services with volume mounts for persistence.
  > Added: 2026-01-19

### Low Priority

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
