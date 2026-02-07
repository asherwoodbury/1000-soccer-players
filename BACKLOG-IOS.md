# iOS App Backlog

Last updated: 2026-02-07

This backlog tracks all iOS-specific development tasks, including App Store publishing.

---

## Category Index

| Item | Priority |
|------|----------|
| App Icon & Launch Screen | HIGH |
| App Store Screenshots & Metadata | HIGH |
| TestFlight Beta Testing | HIGH |
| Unit Tests for Search Algorithms | MEDIUM |
| Haptic Feedback | MEDIUM |
| iPad Layout Optimization | MEDIUM |
| Accessibility Audit | MEDIUM |
| Onboarding Flow | MEDIUM |
| Widgets (Lock Screen/Home Screen) | LOW |
| App Clips Support | LOW |
| Share Progress Feature | LOW |
| Game Center Integration | LOW |
| Siri Shortcuts | LOW |
| Database Update Mechanism | LOW |

---

## To Do

### High Priority

- **App Icon & Launch Screen**
  > Design and implement custom app icon (1024x1024 for App Store, scaled versions for device). Create branded launch screen with app logo. Soccer ball or player silhouette theme recommended.
  > Required for App Store submission.
  > Added: 2026-01-29

- **App Store Screenshots & Metadata**
  > Create App Store listing materials:
  > - Screenshots for iPhone 6.7" (required), 6.5", 5.5" displays
  > - Screenshots for iPad 12.9" (if supporting iPad)
  > - App description (short and full)
  > - Keywords for ASO
  > - Privacy policy URL
  > - Support URL
  > - Category selection (Games > Trivia or Sports)
  > Added: 2026-01-29

- **TestFlight Beta Testing**
  > Set up TestFlight for beta distribution:
  > - Configure App Store Connect
  > - Create internal testing group
  > - Distribute to external testers
  > - Collect crash reports and feedback
  > - Test on multiple device sizes (iPhone SE, iPhone 15 Pro Max, iPad)
  > Added: 2026-01-29

### Medium Priority

- **Unit Tests for Search Algorithms**
  > Create XCTest suite for iOS app covering:
  > - NameNormalizer (diacritics removal, whitespace handling)
  > - FuzzyMatcher (Levenshtein distance, Soundex, prefix variations)
  > - PlayerRepository (search accuracy, mononym handling)
  > - Edge cases: empty strings, very long names, special characters
  > Aim for 80%+ coverage on search logic.
  > Added: 2026-01-29

- **Haptic Feedback**
  > Add haptic feedback for key interactions:
  > - Success haptic on correct guess (UINotificationFeedbackGenerator.success)
  > - Warning haptic on duplicate guess
  > - Selection haptic on filter changes
  > - Impact haptic on tab switches
  > Improves tactile feel and user satisfaction.
  > Added: 2026-01-29

- **iPad Layout Optimization**
  > Optimize layouts for iPad:
  > - Multi-column player grid on larger screens
  > - Side-by-side layout for roster browsing
  > - Keyboard shortcuts for external keyboards
  > - Pointer/trackpad support
  > - Stage Manager compatibility
  > Added: 2026-01-29

- **Accessibility Audit**
  > Comprehensive accessibility review:
  > - VoiceOver labels for all interactive elements
  > - Dynamic Type support verification (all text sizes)
  > - Reduce Motion support (disable animations)
  > - High contrast mode support
  > - Accessibility hints for complex interactions
  > Added: 2026-01-29

- **Onboarding Flow**
  > Create first-launch onboarding:
  > - Brief tutorial explaining the game (1-3 screens)
  > - Example of entering a player name
  > - Highlight mononym support (Pelé, Neymar)
  > - Show how to use roster exploration
  > - Skip option for returning users
  > Added: 2026-01-29

- **Scroll Through Guessed Players on Play Tab**
  > Enhance the main "Play" screen to allow scrolling back through all previously guessed players, not just showing the most recent one. Consider combining the "Play" and "Players" tabs into a unified interface like the web app for better UX.
  >
  > Currently the Play tab only shows the most recent guess. This limits users' ability to review their full guessing history without switching tabs.
  > Added: 2026-02-01

- **Clickable Player Clubs in Roster**
  > Make player club entries clickable in player detail views, allowing navigation directly to that club's Rosters page. Creates seamless exploration flow matching the web app's functionality where team names are already clickable.
  > Added: 2026-02-01

### Low Priority

- **Widgets (Lock Screen/Home Screen)**
  > Implement iOS widgets:
  > - Small widget: Player count progress
  > - Medium widget: Recent guesses + progress
  > - Lock screen widget: Quick count display
  > Uses WidgetKit, requires App Group for data sharing.
  > Added: 2026-01-29

- **App Clips Support**
  > Create App Clip for instant try-before-download:
  > - Lightweight version with sample database (~100 players)
  > - Full game experience with limited data
  > - Prompt to download full app for complete experience
  > Requires App Clip target and separate bundle.
  > Added: 2026-01-29

- **Share Progress Feature**
  > Add share sheet for progress sharing:
  > - Generate shareable image with player count, top stats
  > - Include app link for virality
  > - Share to Messages, Twitter, Instagram Stories
  > Uses UIActivityViewController and custom image generation.
  > Added: 2026-01-29

- **Game Center Integration**
  > Integrate Apple Game Center:
  > - Leaderboard for total players guessed
  > - Achievements (100 players, 500 players, 1000 players, all positions, etc.)
  > - Challenge friends
  > Increases engagement and provides competitive element.
  > Added: 2026-01-29

- **Siri Shortcuts**
  > Add Siri Shortcuts support:
  > - "How many players have I guessed?"
  > - "Open Soccer Players game"
  > - Custom shortcuts via Shortcuts app
  > Uses App Intents framework (iOS 16+).
  > Added: 2026-01-29

- **Database Update Mechanism**
  > Implement optional database updates:
  > - Check for newer database version on app launch
  > - Download delta updates or full database
  > - Migrate session data to new database
  > - Background download support
  > Allows adding new players without app update.
  > Added: 2026-01-29

---

## App Store Publishing Checklist

### Prerequisites

- [ ] **Enroll in Apple Developer Program** - Priority: CRITICAL
  > Enroll in Apple Developer Program ($99/year membership). Enrollment typically takes 24-48 hours for approval. Required to create App IDs, certificates, and provisioning profiles for App Store submission.

- [ ] **Create App ID with Bundle Identifier** - Priority: CRITICAL
  > Create unique App ID in Apple Developer account. Define bundle identifier (e.g., com.yourname.soccerplayers). This identifier is permanent and must be unique across all App Store apps. Register in Certificates, Identifiers & Profiles section.

- [ ] **Register App in App Store Connect** - Priority: CRITICAL
  > Register the app in App Store Connect. This is where you'll manage app metadata, screenshots, pricing, availability, and submit for review. Create app record with bundle identifier matching your Xcode project.

### Technical Preparation

- [ ] **Set Bundle Identifier in Xcode** - Priority: HIGH
  > Configure the unique bundle identifier in Xcode project settings. Match the identifier registered in Apple Developer account and App Store Connect. Verify in: Project settings → Signing & Capabilities → Bundle Identifier.

- [ ] **Configure App Version and Build Number** - Priority: HIGH
  > Set app version to 1.0.0 (or appropriate semantic version) in Xcode project settings. Configure build number to auto-increment for each archive. Update in: Project settings → General → Version and Build fields.

- [ ] **Verify Deployment Target** - Priority: HIGH
  > Verify minimum iOS deployment target is set appropriately (iOS 17+ recommended). Check in: Project settings → General → Minimum Deployments. Ensure all dependencies support this target.

- [ ] **Create App Icon (1024x1024)** - Priority: HIGH
  > Design and create app icon at 1024x1024 pixels for App Store. Icon should be distinctive, communicate "soccer players" game, and include padding. No transparency, no rounded corners (OS applies these). Common themes: soccer ball, player silhouette, or trophy.

- [ ] **Add Icon to Asset Catalog** - Priority: HIGH
  > Add 1024x1024 icon to Xcode Asset Catalog. Xcode will automatically generate all required sizes (1024, 512, 180, 167, 152, 144, 120, 114, 100, 76, 60, 58, 57, 40, 29, 20). Import via: Assets.xcassets → AppIcon → select all required sizes.

- [ ] **Configure Launch Screen** - Priority: HIGH
  > Create branded launch screen (splash screen shown on app start). Can use Storyboard or SwiftUI. Should match app theme, show app name/logo, and provide smooth transition to first screen. Avoid static content that changes frequently (use dynamic view instead).

- [ ] **Create Distribution Certificate** - Priority: HIGH
  > Create Apple Distribution certificate in Certificates, Identifiers & Profiles. This certificate is used to sign the app for App Store distribution. Download and install in Xcode. Valid for 1 year, must renew annually.

- [ ] **Create App Store Provisioning Profile** - Priority: HIGH
  > Create App Store provisioning profile in Certificates, Identifiers & Profiles. Select: App Store type, specify Bundle ID, select distribution certificate. Download and install in Xcode. Used during archive signing.

### App Store Assets & Metadata

- [ ] **Capture Screenshots for 6.7" Display** - Priority: HIGH
  > Create 5-8 screenshots (1290 x 2796 px) for iPhone 15 Pro Max (6.7" display). Show key game flow: (1) Welcome/empty state, (2) Entering a player name, (3) Successful guess with player info, (4) Guessed players list with filters, (5) Team roster exploration, (6) Player detail view. Include text overlays describing features.

- [ ] **Capture Screenshots for 6.5" Display** - Priority: HIGH
  > Create 5-8 screenshots (1284 x 2778 px) for iPhone 14 Plus (6.5" display). Same flow as 6.7" display. Ensures visual consistency across large iPhones in App Store listing.

- [ ] **Write App Name and Subtitle** - Priority: HIGH
  > Define app name (primary title, max 30 chars), subtitle (optional, max 30 chars), and promotional text (max 170 chars) for App Store Connect. Examples:
  > - Name: "Soccer Players"
  > - Subtitle: "Guess 1000 World Players"
  > - Promo text: "Test your soccer knowledge by naming 1000 players"

- [ ] **Define App Store Keywords** - Priority: HIGH
  > Choose keywords for App Store search optimization (ASO). Select 5-10 terms users would search for. Examples: "soccer", "football", "trivia", "guessing game", "sports", "memory", "players", "world cup", "premier league". Comma-separated in App Store Connect.

- [ ] **Create and Host Privacy Policy** - Priority: HIGH
  > Create privacy policy document and host at a public URL. App Store requires privacy policy for submission. Should disclose:
  > - Data collected (none from network, only local session data)
  > - Data stored (session progress stored in app only)
  > - No user tracking, analytics, or external data sharing
  > - Wikidata CC0 attribution (data source)

- [ ] **Set Up Support URL** - Priority: MEDIUM
  > Create support/contact page (can be simple email or form on website) and provide URL to App Store Connect. Allows users to contact developer with issues. Can be same domain as privacy policy.

- [ ] **Select App Store Category** - Priority: HIGH
  > Select primary category (Games > Trivia recommended) and optional secondary category in App Store Connect. "Trivia" best matches the guessing game mechanic. Alternative: Games > Word or Games > Sports if available.

- [ ] **Complete Age Rating Questionnaire** - Priority: HIGH
  > Complete IARC age rating questionnaire in App Store Connect. Answer questions about app content:
  > - No violence, profanity, or inappropriate content
  > - No gambling, real money transactions, or ads
  > - Educational (sports/soccer knowledge)
  > Likely results in 4+ rating (suitable for all ages).

### Submission & Review

- [ ] **Archive Build in Xcode** - Priority: HIGH
  > Create production archive in Xcode: Product → Archive. Ensure device is set to "Any iOS Device (arm64)". Archive will appear in Organizer. This creates signed binary for App Store submission.

- [ ] **Upload Build to App Store Connect** - Priority: HIGH
  > Upload archived build to App Store Connect using Xcode or Transporter app. Select build from Organizer and click "Distribute App". Follow wizard to select App Store distribution method. Upload may take 5-15 minutes.

- [ ] **Configure App Store Pricing & Availability** - Priority: MEDIUM
  > Set pricing tier (Free recommended for initial launch) and select countries/regions where app is available. Default includes ~175 countries. Specify release date (can be automatic or manual).

- [ ] **Submit for App Review** - Priority: HIGH
  > Submit app for App Review in App Store Connect. Ensure build is processed and ready (typically 30 min - 2 hours after upload). Review usually takes 24-48 hours. Apple reviews for:
  > - App functionality and stability
  > - Privacy compliance (matches privacy policy)
  > - Content appropriateness
  > - Performance and security
  > - Design and UX standards

- [ ] **Monitor Review Status & Respond to Feedback** - Priority: HIGH
  > Check App Store Connect daily for review feedback. If rejected, carefully read rejection reason and fix issues. Common rejections: broken links in privacy policy, bugs, metadata inaccuracies. Respond quickly with new build if needed.

- [ ] **Configure Pricing & Availability for Release** - Priority: MEDIUM
  > Once approved, finalize pricing, availability, and release strategy in App Store Connect. Can schedule automatic release or manually release to App Store. Ensure all metadata and screenshots are final before release.

### Post-Launch

- [ ] **Monitor App Store Reviews & Ratings** - Priority: MEDIUM
  > Monitor user reviews and ratings in App Store Connect. Respond to user feedback professionally. Look for common issues or feature requests that could be added in future updates. Track rating trends across iOS versions.

- [ ] **Set Up App Analytics** - Priority: MEDIUM
  > Enable App Analytics in App Store Connect to track: (1) Downloads and updates, (2) Active devices and sessions, (3) Page views in listings, (4) Pre-order conversions. Use data to inform marketing and feature prioritization.

---

## Notes

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

- **Native iOS App**
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

- **[BUG] Session Not Ready Error**
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

- **[BUG] Rosters Reveal Unguessed Players**
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
