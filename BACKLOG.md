# Project Backlog

Last updated: 2026-02-01 16:45

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
| Clean Up Position Categories | MEDIUM |
| Fix Year Formatting in Roster Display | MEDIUM |
| Scroll Through Guessed Players on Play Tab (iOS) | MEDIUM |
| Clickable Player Clubs on iOS Roster | MEDIUM |
| Progress Visualization | MEDIUM |
| Player Statistics Dashboard | LOW |
| Player Photos & Media | MEDIUM |
| Enhanced Empty State | MEDIUM |
| Mobile Touch Improvements | MEDIUM |
| Filter Roster by Guessed/Unguessed | LOW |

### Bugs (BUG)
| Item | Priority |
|------|----------|
| Incorrect Team Assignments (Stale Data) | CRITICAL |
| [iOS] Session Not Ready Error | COMPLETED |
| [iOS] Rosters Reveal Unguessed Players | COMPLETED |

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
| Native iOS App | COMPLETED |
| Multiplayer Mode | MEDIUM |
| Session Persistence Across Tabs | MEDIUM |
| User Accounts & Authentication | MEDIUM |
| Session Management UI | MEDIUM |
| Competitive Mode | MEDIUM |
| Social Sharing | MEDIUM |

### iOS App (IOS)
| Item | Priority |
|------|----------|
| App Icon & Launch Screen | HIGH |
| App Store Screenshots & Metadata | HIGH |
| TestFlight Beta Testing | HIGH |
| Unit Tests for Search Algorithms | MEDIUM |
| Haptic Feedback | MEDIUM |
| iPad Layout Optimization | MEDIUM |
| Widgets (Lock Screen/Home Screen) | LOW |
| App Clips Support | LOW |

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

- **[PERF] Database Query Optimization**
  > Profile and optimize player lookup queries, especially fuzzy matching performance. Add database indexes for frequently queried fields beyond normalized_name. Consider caching top 1000 most-guessed players in memory for instant lookups.
  > Added: 2026-01-19

- **[PERF] Frontend Caching Strategy**
  > Implement aggressive caching of player lookups to reduce API calls. Use IndexedDB for persistent cache, LRU cache in memory for current session. Add cache invalidation strategy when database is updated.
  > Added: 2026-01-19

- **[UX] Dark Mode**
  > Implement dark mode theme toggle in frontend. Persist theme preference in localStorage. Improve contrast and eye comfort for long play sessions.
  > Added: 2026-01-19

- **[GAME] Expanded Leagues & National Teams**
  > Add player data from Portuguese (Primeira Liga), Dutch (Eredivisie), and Turkish (Süper Lig) leagues. Update extract_wikidata.py SPARQL queries to include these leagues. Also prioritize women's leagues and women's national teams with better Wikidata coverage.
  > Added: 2026-01-19 | Updated: 2026-01-27

### iOS App - High Priority

- **[IOS] App Icon & Launch Screen**
  > Design and implement custom app icon (1024x1024 for App Store, scaled versions for device). Create branded launch screen with app logo. Soccer ball or player silhouette theme recommended.
  > Required for App Store submission.
  > Added: 2026-01-29

- **[IOS] App Store Screenshots & Metadata**
  > Create App Store listing materials:
  > - Screenshots for iPhone 6.7" (required), 6.5", 5.5" displays
  > - Screenshots for iPad 12.9" (if supporting iPad)
  > - App description (short and full)
  > - Keywords for ASO
  > - Privacy policy URL
  > - Support URL
  > - Category selection (Games > Trivia or Sports)
  > Added: 2026-01-29

- **[IOS] TestFlight Beta Testing**
  > Set up TestFlight for beta distribution:
  > - Configure App Store Connect
  > - Create internal testing group
  > - Distribute to external testers
  > - Collect crash reports and feedback
  > - Test on multiple device sizes (iPhone SE, iPhone 15 Pro Max, iPad)
  > Added: 2026-01-29

### iOS App - Medium Priority

- **[IOS] Unit Tests for Search Algorithms**
  > Create XCTest suite for iOS app covering:
  > - NameNormalizer (diacritics removal, whitespace handling)
  > - FuzzyMatcher (Levenshtein distance, Soundex, prefix variations)
  > - PlayerRepository (search accuracy, mononym handling)
  > - Edge cases: empty strings, very long names, special characters
  > Aim for 80%+ coverage on search logic.
  > Added: 2026-01-29

- **[IOS] Haptic Feedback**
  > Add haptic feedback for key interactions:
  > - Success haptic on correct guess (UINotificationFeedbackGenerator.success)
  > - Warning haptic on duplicate guess
  > - Selection haptic on filter changes
  > - Impact haptic on tab switches
  > Improves tactile feel and user satisfaction.
  > Added: 2026-01-29

- **[IOS] iPad Layout Optimization**
  > Optimize layouts for iPad:
  > - Multi-column player grid on larger screens
  > - Side-by-side layout for roster browsing
  > - Keyboard shortcuts for external keyboards
  > - Pointer/trackpad support
  > - Stage Manager compatibility
  > Added: 2026-01-29

- **[IOS] Accessibility Audit**
  > Comprehensive accessibility review:
  > - VoiceOver labels for all interactive elements
  > - Dynamic Type support verification (all text sizes)
  > - Reduce Motion support (disable animations)
  > - High contrast mode support
  > - Accessibility hints for complex interactions
  > Added: 2026-01-29

- **[IOS] Onboarding Flow**
  > Create first-launch onboarding:
  > - Brief tutorial explaining the game (1-3 screens)
  > - Example of entering a player name
  > - Highlight mononym support (Pelé, Neymar)
  > - Show how to use roster exploration
  > - Skip option for returning users
  > Added: 2026-01-29

### iOS App - Low Priority

- **[IOS] Widgets (Lock Screen/Home Screen)**
  > Implement iOS widgets:
  > - Small widget: Player count progress
  > - Medium widget: Recent guesses + progress
  > - Lock screen widget: Quick count display
  > Uses WidgetKit, requires App Group for data sharing.
  > Added: 2026-01-29

- **[IOS] App Clips Support**
  > Create App Clip for instant try-before-download:
  > - Lightweight version with sample database (~100 players)
  > - Full game experience with limited data
  > - Prompt to download full app for complete experience
  > Requires App Clip target and separate bundle.
  > Added: 2026-01-29

- **[IOS] Share Progress Feature**
  > Add share sheet for progress sharing:
  > - Generate shareable image with player count, top stats
  > - Include app link for virality
  > - Share to Messages, Twitter, Instagram Stories
  > Uses UIActivityViewController and custom image generation.
  > Added: 2026-01-29

- **[IOS] Game Center Integration**
  > Integrate Apple Game Center:
  > - Leaderboard for total players guessed
  > - Achievements (100 players, 500 players, 1000 players, all positions, etc.)
  > - Challenge friends
  > Increases engagement and provides competitive element.
  > Added: 2026-01-29

- **[IOS] Siri Shortcuts**
  > Add Siri Shortcuts support:
  > - "How many players have I guessed?"
  > - "Open Soccer Players game"
  > - Custom shortcuts via Shortcuts app
  > Uses App Intents framework (iOS 16+).
  > Added: 2026-01-29

- **[IOS] Database Update Mechanism**
  > Implement optional database updates:
  > - Check for newer database version on app launch
  > - Download delta updates or full database
  > - Migrate session data to new database
  > - Background download support
  > Allows adding new players without app update.
  > Added: 2026-01-29

### Medium Priority

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

- **[UX/IOS] Scroll Through Guessed Players on Play Tab**
  > iOS only: Enhance the main "Play" screen to allow scrolling back through all previously guessed players, not just showing the most recent one. Consider combining the "Play" and "Players" tabs into a unified interface like the web app for better UX.
  >
  > Currently the Play tab only shows the most recent guess. This limits users' ability to review their full guessing history without switching tabs.
  > Added: 2026-02-01

- **[UX/IOS] Clickable Player Clubs on iOS Roster**
  > iOS only: Make player club entries clickable in player detail views, allowing navigation directly to that club's Rosters page. Creates seamless exploration flow matching the web app's functionality where team names are already clickable.
  >
  > Priority: HIGH for iOS app UX consistency.
  > Added: 2026-02-01

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

## App Store Publishing Checklist

### Prerequisites

- **[IOS] Enroll in Apple Developer Program** - Priority: CRITICAL
  > Enroll in Apple Developer Program ($99/year membership). Enrollment typically takes 24-48 hours for approval. Required to create App IDs, certificates, and provisioning profiles for App Store submission.
  > Added: 2026-02-01

- **[IOS] Create App ID with Bundle Identifier** - Priority: CRITICAL
  > Create unique App ID in Apple Developer account. Define bundle identifier (e.g., com.yourname.soccerplayers). This identifier is permanent and must be unique across all App Store apps. Register in Certificates, Identifiers & Profiles section.
  > Added: 2026-02-01

- **[IOS] Register App in App Store Connect** - Priority: CRITICAL
  > Register the app in App Store Connect. This is where you'll manage app metadata, screenshots, pricing, availability, and submit for review. Create app record with bundle identifier matching your Xcode project.
  > Added: 2026-02-01

### Technical Preparation

- **[IOS] Set Bundle Identifier in Xcode** - Priority: HIGH
  > Configure the unique bundle identifier in Xcode project settings. Match the identifier registered in Apple Developer account and App Store Connect. Verify in: Project settings → Signing & Capabilities → Bundle Identifier.
  > Added: 2026-02-01

- **[IOS] Configure App Version and Build Number** - Priority: HIGH
  > Set app version to 1.0.0 (or appropriate semantic version) in Xcode project settings. Configure build number to auto-increment for each archive. Update in: Project settings → General → Version and Build fields.
  > Added: 2026-02-01

- **[IOS] Verify Deployment Target** - Priority: HIGH
  > Verify minimum iOS deployment target is set appropriately (iOS 17+ recommended). Check in: Project settings → General → Minimum Deployments. Ensure all dependencies support this target.
  > Added: 2026-02-01

- **[IOS] Create App Icon (1024x1024)** - Priority: HIGH
  > Design and create app icon at 1024x1024 pixels for App Store. Icon should be distinctive, communicate "soccer players" game, and include padding. No transparency, no rounded corners (OS applies these). Common themes: soccer ball, player silhouette, or trophy.
  > Added: 2026-02-01

- **[IOS] Add Icon to Asset Catalog** - Priority: HIGH
  > Add 1024x1024 icon to Xcode Asset Catalog. Xcode will automatically generate all required sizes (1024, 512, 180, 167, 152, 144, 120, 114, 100, 76, 60, 58, 57, 40, 29, 20). Import via: Assets.xcassets → AppIcon → select all required sizes.
  > Added: 2026-02-01

- **[IOS] Configure Launch Screen** - Priority: HIGH
  > Create branded launch screen (splash screen shown on app start). Can use Storyboard or SwiftUI. Should match app theme, show app name/logo, and provide smooth transition to first screen. Avoid static content that changes frequently (use dynamic view instead).
  > Added: 2026-02-01

- **[IOS] Create Distribution Certificate** - Priority: HIGH
  > Create Apple Distribution certificate in Certificates, Identifiers & Profiles. This certificate is used to sign the app for App Store distribution. Download and install in Xcode. Valid for 1 year, must renew annually.
  > Added: 2026-02-01

- **[IOS] Create App Store Provisioning Profile** - Priority: HIGH
  > Create App Store provisioning profile in Certificates, Identifiers & Profiles. Select: App Store type, specify Bundle ID, select distribution certificate. Download and install in Xcode. Used during archive signing.
  > Added: 2026-02-01

### App Store Assets & Metadata

- **[IOS] Capture Screenshots for 6.7" Display** - Priority: HIGH
  > Create 5-8 screenshots (1290 x 2796 px) for iPhone 15 Pro Max (6.7" display). Show key game flow: (1) Welcome/empty state, (2) Entering a player name, (3) Successful guess with player info, (4) Guessed players list with filters, (5) Team roster exploration, (6) Player detail view. Include text overlays describing features.
  > Added: 2026-02-01

- **[IOS] Capture Screenshots for 6.5" Display** - Priority: HIGH
  > Create 5-8 screenshots (1284 x 2778 px) for iPhone 14 Plus (6.5" display). Same flow as 6.7" display. Ensures visual consistency across large iPhones in App Store listing.
  > Added: 2026-02-01

- **[IOS] Write App Name and Subtitle** - Priority: HIGH
  > Define app name (primary title, max 30 chars), subtitle (optional, max 30 chars), and promotional text (max 170 chars) for App Store Connect. Examples:
  > - Name: "Soccer Players"
  > - Subtitle: "Guess 1000 World Players"
  > - Promo text: "Test your soccer knowledge by naming 1000 players"
  > Added: 2026-02-01

- **[IOS] Define App Store Keywords** - Priority: HIGH
  > Choose keywords for App Store search optimization (ASO). Select 5-10 terms users would search for. Examples: "soccer", "football", "trivia", "guessing game", "sports", "memory", "players", "world cup", "premier league". Comma-separated in App Store Connect.
  > Added: 2026-02-01

- **[IOS] Create and Host Privacy Policy** - Priority: HIGH
  > Create privacy policy document and host at a public URL. App Store requires privacy policy for submission. Should disclose:
  > - Data collected (none from network, only local session data)
  > - Data stored (session progress stored in app only)
  > - No user tracking, analytics, or external data sharing
  > - Wikidata CC0 attribution (data source)
  > Added: 2026-02-01

- **[IOS] Set Up Support URL** - Priority: MEDIUM
  > Create support/contact page (can be simple email or form on website) and provide URL to App Store Connect. Allows users to contact developer with issues. Can be same domain as privacy policy.
  > Added: 2026-02-01

- **[IOS] Select App Store Category** - Priority: HIGH
  > Select primary category (Games > Trivia recommended) and optional secondary category in App Store Connect. "Trivia" best matches the guessing game mechanic. Alternative: Games > Word or Games > Sports if available.
  > Added: 2026-02-01

- **[IOS] Complete Age Rating Questionnaire** - Priority: HIGH
  > Complete IARC age rating questionnaire in App Store Connect. Answer questions about app content:
  > - No violence, profanity, or inappropriate content
  > - No gambling, real money transactions, or ads
  > - Educational (sports/soccer knowledge)
  > Likely results in 4+ rating (suitable for all ages).
  > Added: 2026-02-01

### Submission & Review

- **[IOS] Archive Build in Xcode** - Priority: HIGH
  > Create production archive in Xcode: Product → Archive. Ensure device is set to "Any iOS Device (arm64)". Archive will appear in Organizer. This creates signed binary for App Store submission.
  > Added: 2026-02-01

- **[IOS] Upload Build to App Store Connect** - Priority: HIGH
  > Upload archived build to App Store Connect using Xcode or Transporter app. Select build from Organizer and click "Distribute App". Follow wizard to select App Store distribution method. Upload may take 5-15 minutes.
  > Added: 2026-02-01

- **[IOS] Configure App Store Pricing & Availability** - Priority: MEDIUM
  > Set pricing tier (Free recommended for initial launch) and select countries/regions where app is available. Default includes ~175 countries. Specify release date (can be automatic or manual).
  > Added: 2026-02-01

- **[IOS] Submit for App Review** - Priority: HIGH
  > Submit app for App Review in App Store Connect. Ensure build is processed and ready (typically 30 min - 2 hours after upload). Review usually takes 24-48 hours. Apple reviews for:
  > - App functionality and stability
  > - Privacy compliance (matches privacy policy)
  > - Content appropriateness
  > - Performance and security
  > - Design and UX standards
  > Added: 2026-02-01

- **[IOS] Monitor Review Status & Respond to Feedback** - Priority: HIGH
  > Check App Store Connect daily for review feedback. If rejected, carefully read rejection reason and fix issues. Common rejections: broken links in privacy policy, bugs, metadata inaccuracies. Respond quickly with new build if needed.
  > Added: 2026-02-01

- **[IOS] Configure Pricing & Availability for Release** - Priority: MEDIUM
  > Once approved, finalize pricing, availability, and release strategy in App Store Connect. Can schedule automatic release or manually release to App Store. Ensure all metadata and screenshots are final before release.
  > Added: 2026-02-01

### Post-Launch

- **[IOS] Monitor App Store Reviews & Ratings** - Priority: MEDIUM
  > Monitor user reviews and ratings in App Store Connect. Respond to user feedback professionally. Look for common issues or feature requests that could be added in future updates. Track rating trends across iOS versions.
  > Added: 2026-02-01

- **[IOS] Set Up App Analytics** - Priority: MEDIUM
  > Enable App Analytics in App Store Connect to track: (1) Downloads and updates, (2) Active devices and sessions, (3) Page views in listings, (4) Pre-order conversions. Use data to inform marketing and feature prioritization.
  > Added: 2026-02-01

### Notes

**Data & Privacy:**
- App uses Wikidata (CC0 license) for player data - properly attributed
- All session data stored locally in SQLite - no external network calls after initial bundle
- No user accounts, authentication, or personal data collection
- No analytics, tracking, or third-party integrations
- Fully compliant with App Store privacy guidelines

**Technical Considerations:**
- App is fully offline-capable after download - no internet required
- Database (~48MB compressed) is bundled with app
- Consider versioning strategy for future database updates (App Store Connect > Update Method)
- TestFlight beta testing recommended before final submission to catch device-specific issues

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

- **[META] Native iOS App**
  > Built native SwiftUI iOS app (iOS 17+) with full offline capability. Features:
  > - **Architecture**: MVVM with GRDB.swift for SQLite access
  > - **Database**: Bundled 47k+ player database (~48MB, ~20MB compressed)
  > - **Search**: Ported FTS5 fuzzy matching, Levenshtein distance, mononyms support
  > - **4 Tabs**: Play (guess input), Players (filtered list), Rosters (club browsing), Settings
  > - **Session persistence**: UserDefaults for session ID, SQLite for guesses
  > - **UI**: Player cards, detail sheets, filtering, roster grids, recent clubs
  >
  > Key files: `SoccerPlayers/` directory with 31 Swift files
  > Completed: 2026-01-29

- **[BUG/IOS] Session Not Ready Error**
  > Fixed "Session not ready" error when attempting to guess a player.
  >
  > **Root cause:** Race condition where users could interact with the input before `GameViewModel.setup()` completed and created/loaded a session.
  >
  > **Fix:**
  > - Added `isSessionReady` published property to `GameViewModel`
  > - Set to `true` only after session is successfully loaded/created
  > - Disabled input and submit button until `isSessionReady` is true
  > - Added "Setting up session..." loading indicator
  >
  > Completed: 2026-01-29

- **[BUG/IOS] Rosters Reveal Unguessed Players**
  > Fixed roster tab revealing all player names regardless of guess status.
  >
  > **Fix:**
  > - Added `SessionRepository` to `RosterViewModel` to query guessed players
  > - Added `guessedPlayerIds: Set<Int64>` to track which players have been guessed
  > - Updated `RosterGridView` to accept guessed IDs and mask unguessed players as "?????"
  > - Guessed players now show with green highlight background
  > - Guessed IDs refresh when loading/changing rosters
  >
  > Completed: 2026-01-29
