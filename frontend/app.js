/**
 * 1000 Soccer Players - Frontend Application
 */

const API_BASE = 'http://localhost:8000/api';

// Default display settings
const DEFAULT_SETTINGS = {
    showNationality: true,
    showPosition: true,
    showCareerSpan: true,
    showTopClubs: true,
    showFullHistory: true,
    showRosterLookup: true,
    theme: 'system' // 'system', 'light', or 'dark'
};

// Maximum number of recent clubs to store
const MAX_RECENT_CLUBS = 5;

// State
let sessionId = null;
let guessedPlayers = [];
let displaySettings = { ...DEFAULT_SETTINGS };
let recentClubs = []; // Recently viewed clubs for quick access

// Load settings from localStorage
function loadSettings() {
    const stored = localStorage.getItem('displaySettings');
    if (stored) {
        try {
            displaySettings = { ...DEFAULT_SETTINGS, ...JSON.parse(stored) };
        } catch (e) {
            displaySettings = { ...DEFAULT_SETTINGS };
        }
    }
}

// Save settings to localStorage
function saveSettings() {
    localStorage.setItem('displaySettings', JSON.stringify(displaySettings));
}

// Apply theme based on current setting
function applyTheme() {
    const theme = displaySettings.theme || 'system';
    if (theme === 'system') {
        document.documentElement.removeAttribute('data-theme');
    } else {
        document.documentElement.setAttribute('data-theme', theme);
    }
    updateThemeButtons();
}

// Update theme button states
function updateThemeButtons() {
    const theme = displaySettings.theme || 'system';
    document.querySelectorAll('.theme-btn').forEach(btn => {
        const isPressed = btn.dataset.theme === theme;
        btn.setAttribute('aria-pressed', isPressed);
    });
}

// Set theme and save
function setTheme(theme) {
    displaySettings.theme = theme;
    saveSettings();
    applyTheme();
}

// Load recent clubs from localStorage
function loadRecentClubs() {
    const stored = localStorage.getItem('recentClubs');
    if (stored) {
        try {
            recentClubs = JSON.parse(stored);
        } catch (e) {
            recentClubs = [];
        }
    }
}

// Save recent clubs to localStorage
function saveRecentClubs() {
    localStorage.setItem('recentClubs', JSON.stringify(recentClubs));
}

// Add a club to the recent clubs list
function addToRecentClubs(clubId, clubName, displayName) {
    // Remove if already exists (to move it to front)
    recentClubs = recentClubs.filter(c => c.id !== clubId);

    // Add to front (store both name for searching and displayName for display)
    recentClubs.unshift({ id: clubId, name: clubName, displayName: displayName || clubName });

    // Keep only MAX_RECENT_CLUBS
    if (recentClubs.length > MAX_RECENT_CLUBS) {
        recentClubs = recentClubs.slice(0, MAX_RECENT_CLUBS);
    }

    saveRecentClubs();
    renderRecentClubs();
}

// Render recent clubs as clickable chips
function renderRecentClubs() {
    if (recentClubs.length === 0) {
        recentClubsContainer.classList.add('hidden');
        return;
    }

    // Determine which club is currently active
    const activeClubId = currentClub ? currentClub.id : null;

    recentClubsContainer.innerHTML = `
        <span class="recent-clubs-label">Recent:</span>
        ${recentClubs.map(club => {
            const display = club.displayName || club.name;
            return `
            <button class="recent-club-chip${club.id === activeClubId ? ' active' : ''}" data-club-id="${club.id}" data-club-name="${escapeHtml(club.name)}" aria-label="Load ${escapeHtml(display)} roster" title="${escapeHtml(display)}">
                ${escapeHtml(display)}
            </button>
        `}).join('')}
        <button class="recent-clubs-clear" aria-label="Clear recent clubs" title="Clear recent clubs">&times;</button>
    `;

    // Add click handlers for chips
    recentClubsContainer.querySelectorAll('.recent-club-chip').forEach(chip => {
        chip.addEventListener('click', () => {
            selectClub(parseInt(chip.dataset.clubId), chip.dataset.clubName);
        });
    });

    // Add click handler for clear button
    recentClubsContainer.querySelector('.recent-clubs-clear').addEventListener('click', clearRecentClubs);

    // Show the container (visibility controlled by search input focus)
    updateRecentClubsVisibility();
}

// Clear all recent clubs
function clearRecentClubs() {
    recentClubs = [];
    localStorage.removeItem('recentClubs');
    recentClubsContainer.classList.add('hidden');
    recentClubsContainer.innerHTML = '';
}

// Update recent clubs visibility based on search input state
function updateRecentClubsVisibility() {
    if (recentClubs.length === 0) {
        recentClubsContainer.classList.add('hidden');
        return;
    }

    // Always show recent clubs when there are any saved
    // They provide quick navigation between frequently viewed teams
    recentClubsContainer.classList.remove('hidden');
}

// DOM Elements
const playerInput = document.getElementById('player-input');
const guessForm = document.getElementById('guess-form');
const messageDiv = document.getElementById('message');
const playerCountEl = document.getElementById('player-count');
const playersList = document.getElementById('players-list');
const filterInput = document.getElementById('filter-input');
const filterPosition = document.getElementById('filter-position');
const filterNationality = document.getElementById('filter-nationality');
const clearFiltersBtn = document.getElementById('clear-filters');
const filteredCountEl = document.getElementById('filtered-count');
const modal = document.getElementById('player-modal');
const modalClose = modal.querySelector('.modal-close');

// Settings DOM Elements
const settingsBtn = document.getElementById('settings-btn');
const settingsModal = document.getElementById('settings-modal');
const settingsClose = document.getElementById('settings-close');
const settingCheckboxes = {
    nationality: document.getElementById('setting-nationality'),
    position: document.getElementById('setting-position'),
    careerSpan: document.getElementById('setting-career-span'),
    topClubs: document.getElementById('setting-top-clubs'),
    fullHistory: document.getElementById('setting-full-history'),
    rosterLookup: document.getElementById('setting-roster-lookup')
};

// Tabs
const tabs = document.querySelectorAll('.tab');
const guessedTab = document.getElementById('guessed-tab');
const rosterTab = document.getElementById('roster-tab');
const rosterTabBtn = document.querySelector('.tab[data-tab="roster"]');

// Roster lookup DOM Elements
const clubSearchInput = document.getElementById('club-search-input');
const clubSearchResults = document.getElementById('club-search-results');
const recentClubsContainer = document.getElementById('recent-clubs');
const rosterDisplay = document.getElementById('roster-display');
const rosterEmpty = document.getElementById('roster-empty');
const rosterClubName = document.getElementById('roster-club-name');
const rosterSeason = document.getElementById('roster-season');
const rosterGuessedCount = document.getElementById('roster-guessed-count');
const rosterTotalCount = document.getElementById('roster-total-count');
const rosterPlayers = document.getElementById('roster-players');
const seasonPrevBtn = document.getElementById('season-prev');
const seasonNextBtn = document.getElementById('season-next');

// Roster state
let currentClub = null;
let currentSeason = new Date().getFullYear();
let clubYearRange = { min: 2000, max: 2025 };
let clubSearchTimeout = null;
let highlightedResultIndex = -1;

// Initialize
document.addEventListener('DOMContentLoaded', async () => {
    loadSettings();
    loadRecentClubs();
    applyTheme(); // Apply theme immediately to prevent flash
    applySettingsToUI();
    await initSession();
    setupEventListeners();
    renderRecentClubs();
});

// Apply current settings to the settings UI checkboxes
function applySettingsToUI() {
    settingCheckboxes.nationality.checked = displaySettings.showNationality;
    settingCheckboxes.position.checked = displaySettings.showPosition;
    settingCheckboxes.careerSpan.checked = displaySettings.showCareerSpan;
    settingCheckboxes.topClubs.checked = displaySettings.showTopClubs;
    settingCheckboxes.fullHistory.checked = displaySettings.showFullHistory;
    settingCheckboxes.rosterLookup.checked = displaySettings.showRosterLookup;
    updateFullHistoryState();
    updateRosterTabVisibility();
    updateThemeButtons();
}

// Update roster tab visibility based on settings
function updateRosterTabVisibility() {
    if (displaySettings.showRosterLookup) {
        rosterTabBtn.classList.remove('hidden');
    } else {
        rosterTabBtn.classList.add('hidden');
        // If roster tab is active and we're hiding it, switch to guessed tab
        if (rosterTab.classList.contains('active')) {
            switchTab('guessed');
        }
    }
}

// Update the full history checkbox state based on top clubs
function updateFullHistoryState() {
    const fullHistoryItem = settingCheckboxes.fullHistory.closest('.setting-item');
    if (!displaySettings.showTopClubs) {
        fullHistoryItem.classList.add('disabled');
        settingCheckboxes.fullHistory.disabled = true;
    } else {
        fullHistoryItem.classList.remove('disabled');
        settingCheckboxes.fullHistory.disabled = false;
    }
}

async function initSession() {
    // Check for existing session in localStorage
    const storedSessionId = localStorage.getItem('sessionId');

    if (storedSessionId) {
        try {
            const response = await fetch(`${API_BASE}/sessions/${storedSessionId}`);
            if (response.ok) {
                const data = await response.json();
                sessionId = data.id;
                guessedPlayers = data.players;
                updateUI();
                return;
            }
        } catch (e) {
            console.log('Could not restore session, creating new one');
        }
    }

    // Create new session
    try {
        const response = await fetch(`${API_BASE}/sessions/`, {
            method: 'POST'
        });
        const data = await response.json();
        sessionId = data.id;
        localStorage.setItem('sessionId', sessionId);
        guessedPlayers = [];
        updateUI();
    } catch (e) {
        showMessage('Could not connect to server. Make sure the backend is running.', 'error');
    }
}

function setupEventListeners() {
    guessForm.addEventListener('submit', handleGuess);
    filterInput.addEventListener('input', handleFilter);
    filterInput.addEventListener('keydown', handleFilterKeydown);
    filterPosition.addEventListener('change', handleFilter);
    filterNationality.addEventListener('change', handleFilter);
    clearFiltersBtn.addEventListener('click', clearAllFilters);
    modalClose.addEventListener('click', closeModal);
    modal.addEventListener('click', (e) => {
        if (e.target === modal) closeModal();
    });

    // Settings modal
    settingsBtn.addEventListener('click', openSettings);
    settingsClose.addEventListener('click', closeSettings);
    settingsModal.addEventListener('click', (e) => {
        if (e.target === settingsModal) closeSettings();
    });

    // Settings checkboxes
    settingCheckboxes.nationality.addEventListener('change', (e) => {
        displaySettings.showNationality = e.target.checked;
        saveSettings();
        renderPlayersList();
    });
    settingCheckboxes.position.addEventListener('change', (e) => {
        displaySettings.showPosition = e.target.checked;
        saveSettings();
        renderPlayersList();
    });
    settingCheckboxes.careerSpan.addEventListener('change', (e) => {
        displaySettings.showCareerSpan = e.target.checked;
        saveSettings();
        renderPlayersList();
    });
    settingCheckboxes.topClubs.addEventListener('change', (e) => {
        displaySettings.showTopClubs = e.target.checked;
        // If top clubs is disabled, also disable full history
        if (!e.target.checked) {
            displaySettings.showFullHistory = false;
            settingCheckboxes.fullHistory.checked = false;
        }
        updateFullHistoryState();
        saveSettings();
        renderPlayersList();
    });
    settingCheckboxes.fullHistory.addEventListener('change', (e) => {
        displaySettings.showFullHistory = e.target.checked;
        saveSettings();
    });
    settingCheckboxes.rosterLookup.addEventListener('change', (e) => {
        displaySettings.showRosterLookup = e.target.checked;
        updateRosterTabVisibility();
        saveSettings();
    });

    // Theme buttons
    document.querySelectorAll('.theme-btn').forEach(btn => {
        btn.addEventListener('click', (e) => {
            e.preventDefault();
            e.stopPropagation();
            setTheme(btn.dataset.theme);
        });
    });

    // Tabs
    tabs.forEach(tab => {
        tab.addEventListener('click', () => {
            switchTab(tab.dataset.tab);
        });
    });

    // Club search
    clubSearchInput.addEventListener('input', () => {
        handleClubSearch();
        updateRecentClubsVisibility();
    });
    clubSearchInput.addEventListener('focus', () => {
        if (clubSearchInput.value.length >= 2) {
            clubSearchResults.classList.remove('hidden');
        }
        updateRecentClubsVisibility();
    });
    clubSearchInput.addEventListener('keydown', handleClubSearchKeydown);

    // Close search results when clicking outside
    document.addEventListener('click', (e) => {
        if (!e.target.closest('.roster-search')) {
            clubSearchResults.classList.add('hidden');
        }
    });

    // Season navigation
    seasonPrevBtn.addEventListener('click', () => changeSeason(-1));
    seasonNextBtn.addEventListener('click', () => changeSeason(1));

    // Close modals on Escape
    document.addEventListener('keydown', (e) => {
        if (e.key === 'Escape') {
            closeModal();
            closeSettings();
        }
    });
}

function openSettings() {
    settingsModal.classList.remove('hidden');
    settingsClose.focus();
}

function closeSettings() {
    settingsModal.classList.add('hidden');
    settingsBtn.focus();
}

async function handleGuess(e) {
    e.preventDefault();

    const name = playerInput.value.trim();
    if (!name) return;

    // Disable input while processing
    playerInput.disabled = true;
    const submitBtn = guessForm.querySelector('button');
    submitBtn.disabled = true;
    submitBtn.classList.add('loading');

    try {
        // Look up the player
        const lookupResponse = await fetch(
            `${API_BASE}/players/lookup?name=${encodeURIComponent(name)}`
        );
        const lookupData = await lookupResponse.json();

        if (!lookupData.found) {
            if (lookupData.ambiguous) {
                showMessage(lookupData.message, 'warning');
            } else {
                showMessage(lookupData.message, 'error');
            }
            playerInput.disabled = false;
            submitBtn.disabled = false;
            submitBtn.classList.remove('loading');
            playerInput.select();
            return;
        }

        // Player found - add to session
        const guessResponse = await fetch(
            `${API_BASE}/sessions/${sessionId}/guess/${lookupData.player.id}`,
            { method: 'POST' }
        );
        const guessData = await guessResponse.json();

        if (guessData.already_guessed) {
            showMessage(guessData.message, 'warning');
        } else {
            showMessage(`${lookupData.player.name} added!`, 'success');

            // Add to local state
            guessedPlayers.unshift({
                id: lookupData.player.id,
                name: lookupData.player.name,
                nationality: lookupData.player.nationality,
                position: lookupData.player.position,
                top_clubs: lookupData.player.top_clubs,
                clubs: lookupData.player.clubs,
                career_span: lookupData.player.career_span,
                guessed_at: new Date().toISOString(),
                isNew: true
            });

            updateUI(true);

            // Refresh roster display if a club is currently loaded
            // so the newly guessed player shows as revealed
            if (currentClub) {
                loadRoster();
            }
        }
        playerInput.value = '';

    } catch (e) {
        showMessage('Error connecting to server', 'error');
        console.error(e);
    }

    playerInput.disabled = false;
    submitBtn.disabled = false;
    submitBtn.classList.remove('loading');
    playerInput.focus();
}

function handleFilter() {
    updateFilterVisualStates();
    renderPlayersList();
}

function handleFilterKeydown(e) {
    // Escape clears the text filter
    if (e.key === 'Escape' && filterInput.value) {
        e.preventDefault();
        filterInput.value = '';
        handleFilter();
    }
}

function clearAllFilters() {
    filterInput.value = '';
    filterPosition.value = '';
    filterNationality.value = '';
    updateFilterVisualStates();
    renderPlayersList();
}

function updateFilterVisualStates() {
    const textFilter = filterInput.value.trim();
    const positionFilter = filterPosition.value;
    const nationalityFilter = filterNationality.value;
    const hasActiveFilters = textFilter || positionFilter || nationalityFilter;

    // Update Clear button state
    clearFiltersBtn.classList.toggle('has-filters', hasActiveFilters);

    // Update dropdown visual states
    filterPosition.classList.toggle('has-value', !!positionFilter);
    filterNationality.classList.toggle('has-value', !!nationalityFilter);
}

function updateNationalityOptions() {
    // Get unique nationalities from guessed players, sorted alphabetically
    const nationalities = [...new Set(
        guessedPlayers
            .map(p => p.nationality)
            .filter(Boolean)
    )].sort();

    // Preserve current selection if still valid
    const currentValue = filterNationality.value;

    // Rebuild options
    filterNationality.innerHTML = '<option value="">All Nationalities</option>';
    nationalities.forEach(nat => {
        const option = document.createElement('option');
        option.value = nat;
        option.textContent = nat;
        filterNationality.appendChild(option);
    });

    // Restore selection if still valid
    if (nationalities.includes(currentValue)) {
        filterNationality.value = currentValue;
    }
}

function updateUI(isNewPlayer = false) {
    playerCountEl.textContent = guessedPlayers.length;

    // Animate the count when a new player is added
    if (isNewPlayer) {
        playerCountEl.classList.add('bump');
        setTimeout(() => {
            playerCountEl.classList.remove('bump');
        }, 300);
    }

    // Update nationality dropdown options
    updateNationalityOptions();

    renderPlayersList(isNewPlayer);
}

function renderPlayersList(highlightNew = false) {
    const textFilter = filterInput.value.toLowerCase().trim();
    const positionFilter = filterPosition.value;
    const nationalityFilter = filterNationality.value;

    let filteredPlayers = guessedPlayers;

    // Apply text filter (name or club)
    if (textFilter) {
        filteredPlayers = filteredPlayers.filter(player => {
            if (player.name.toLowerCase().includes(textFilter)) return true;
            if (player.top_clubs?.some(c => c.toLowerCase().includes(textFilter))) return true;
            return false;
        });
    }

    // Apply position filter
    if (positionFilter) {
        filteredPlayers = filteredPlayers.filter(player =>
            player.position === positionFilter
        );
    }

    // Apply nationality filter
    if (nationalityFilter) {
        filteredPlayers = filteredPlayers.filter(player =>
            player.nationality === nationalityFilter
        );
    }

    // Update filter count display
    const hasActiveFilters = textFilter || positionFilter || nationalityFilter;
    if (hasActiveFilters) {
        filteredCountEl.textContent = `(showing ${filteredPlayers.length})`;
    } else {
        filteredCountEl.textContent = '';
    }

    if (filteredPlayers.length === 0) {
        if (guessedPlayers.length === 0) {
            playersList.innerHTML = `
                <div class="empty-state">
                    Start guessing players! Enter a first and last name above.
                </div>
            `;
        } else {
            // Build a description of active filters for the empty state message
            const activeFilters = [];
            if (textFilter) activeFilters.push(`"${filterInput.value}"`);
            if (positionFilter) activeFilters.push(positionFilter + 's');
            if (nationalityFilter) activeFilters.push(nationalityFilter + ' players');

            const filterDesc = activeFilters.length > 0
                ? `No players match ${activeFilters.join(' + ')}.`
                : 'No players match your filter.';

            playersList.innerHTML = `
                <div class="empty-state filter-empty">
                    ${filterDesc}
                    <br><button class="clear-inline-btn" onclick="clearAllFilters()">Clear filters</button>
                </div>
            `;
        }
        return;
    }

    playersList.innerHTML = filteredPlayers.map((player, index) => {
        const isNew = highlightNew && index === 0 && player.isNew;

        // Determine current clubs (where end_date is null and not national team)
        // Use display_name to match against top_clubs which also uses display names
        const currentClubNames = new Set(
            (player.clubs || [])
                .filter(c => !c.end_date && !c.is_national_team)
                .map(c => c.display_name || c.name)
        );

        // Build info line based on settings (nationality is clickable)
        const infoParts = [];
        if (displaySettings.showNationality && player.nationality) {
            infoParts.push(`<a href="#" class="card-link nationality-link" data-nationality="${escapeHtml(player.nationality)}">${escapeHtml(player.nationality)}</a>`);
        }
        if (displaySettings.showPosition && player.position) {
            infoParts.push(escapeHtml(player.position));
        }
        if (displaySettings.showCareerSpan && player.career_span) {
            infoParts.push(escapeHtml(player.career_span));
        }
        const infoLine = infoParts.join(' · ') || '';

        // Build clubs line based on settings (each club is clickable)
        let clubsLine = '';
        if (displaySettings.showTopClubs && player.top_clubs?.length) {
            clubsLine = player.top_clubs.map(clubName => {
                const isCurrent = currentClubNames.has(clubName);
                return `<a href="#" class="card-link club-link${isCurrent ? ' current-club' : ''}" data-club="${escapeHtml(clubName)}">${escapeHtml(clubName)}</a>`;
            }).join(', ');
        }

        return `
        <div class="player-card${isNew ? ' new' : ''}" data-player-id="${player.id}" tabindex="0" role="button" aria-label="View details for ${escapeHtml(player.name)}">
            <div class="player-name">${escapeHtml(player.name)}</div>
            ${infoLine ? `<div class="player-info">${infoLine}</div>` : ''}
            ${clubsLine ? `<div class="player-clubs">${clubsLine}</div>` : ''}
        </div>
    `}).join('');

    // Clear the "new" flag after rendering
    if (highlightNew && guessedPlayers.length > 0) {
        guessedPlayers[0].isNew = false;
    }

    // Add click handlers for club/nationality links in cards (stop propagation to prevent modal open)
    document.querySelectorAll('.player-card .club-link').forEach(link => {
        link.addEventListener('click', (e) => {
            e.preventDefault();
            e.stopPropagation();
            navigateToClubRoster(link.dataset.club);
        });
    });

    document.querySelectorAll('.player-card .nationality-link').forEach(link => {
        link.addEventListener('click', (e) => {
            e.preventDefault();
            e.stopPropagation();
            navigateToNationalTeam(link.dataset.nationality);
        });
    });

    // Add click and keyboard handlers for opening modal (on card itself, not on links)
    document.querySelectorAll('.player-card').forEach(card => {
        const openModal = () => {
            const playerId = parseInt(card.dataset.playerId);
            const player = guessedPlayers.find(p => p.id === playerId);
            if (player) showPlayerModal(player);
        };

        card.addEventListener('click', (e) => {
            // Only open modal if the click was not on a link
            if (!e.target.closest('.card-link')) {
                openModal();
            }
        });
        card.addEventListener('keydown', (e) => {
            if (e.key === 'Enter' || e.key === ' ') {
                // Only open modal if focus is on the card itself, not a link
                if (!e.target.closest('.card-link')) {
                    e.preventDefault();
                    openModal();
                }
            }
        });
    });
}

let lastFocusedElement = null;

function showPlayerModal(player) {
    // Store the element that had focus before opening modal
    lastFocusedElement = document.activeElement;

    document.getElementById('modal-player-name').textContent = player.name;

    // Nationality (clickable to view national team)
    const nationalityRow = document.getElementById('modal-nationality-row');
    const nationalityEl = document.getElementById('modal-nationality');
    if (displaySettings.showNationality) {
        if (player.nationality) {
            nationalityEl.innerHTML = `<a href="#" class="club-link" data-nationality="${escapeHtml(player.nationality)}">${escapeHtml(player.nationality)}</a>`;
            nationalityEl.querySelector('.club-link').addEventListener('click', (e) => {
                e.preventDefault();
                navigateToNationalTeam(player.nationality);
            });
        } else {
            nationalityEl.textContent = 'Unknown';
        }
        nationalityRow.style.display = '';
    } else {
        nationalityRow.style.display = 'none';
    }

    // Position
    const positionRow = document.getElementById('modal-position-row');
    if (displaySettings.showPosition) {
        document.getElementById('modal-position').textContent = player.position || 'Unknown';
        positionRow.style.display = '';
    } else {
        positionRow.style.display = 'none';
    }

    // Career span
    const careerSpanRow = document.getElementById('modal-career-span-row');
    if (displaySettings.showCareerSpan && player.career_span) {
        document.getElementById('modal-career-span').textContent = player.career_span;
        careerSpanRow.style.display = '';
    } else {
        careerSpanRow.style.display = 'none';
    }

    // Top clubs (clickable)
    const topClubsSection = document.getElementById('modal-top-clubs-section');
    const topClubsEl = document.getElementById('modal-top-clubs');
    if (displaySettings.showTopClubs && player.top_clubs?.length) {
        // Check which clubs are current (player still there)
        // Use display_name to match against top_clubs which also uses display names
        const currentClubNames = new Set(
            (player.clubs || [])
                .filter(c => !c.end_date && !c.is_national_team)
                .map(c => c.display_name || c.name)
        );

        topClubsEl.innerHTML = player.top_clubs.map(clubName => {
            const isCurrent = currentClubNames.has(clubName);
            return `<a href="#" class="club-link${isCurrent ? ' current-club' : ''}" data-club="${escapeHtml(clubName)}">${escapeHtml(clubName)}</a>`;
        }).join(', ');

        topClubsEl.querySelectorAll('.club-link').forEach(link => {
            link.addEventListener('click', (e) => {
                e.preventDefault();
                navigateToClubRoster(link.dataset.club);
            });
        });
        topClubsSection.style.display = '';
    } else {
        topClubsSection.style.display = 'none';
    }

    // Full club history (clickable with current team highlighting)
    const clubsSection = document.getElementById('modal-clubs-section');
    const clubsList = document.getElementById('modal-clubs');

    if (displaySettings.showTopClubs && displaySettings.showFullHistory && player.clubs?.length) {
        clubsList.innerHTML = player.clubs.map(club => {
            const startYear = club.start_date ? club.start_date.substring(0, 4) : '?';
            const endYear = club.end_date ? club.end_date.substring(0, 4) : 'Present';
            const isNational = club.is_national_team;
            const isCurrent = !club.end_date;
            const displayName = club.display_name || club.name;

            const classes = [
                isNational ? 'national-team' : '',
                isCurrent ? 'current-club' : ''
            ].filter(Boolean).join(' ');

            return `
                <li class="${classes}">
                    <a href="#" class="club-link" data-club="${escapeHtml(club.name)}">${escapeHtml(displayName)}</a>
                    <span class="club-dates">(${startYear} - ${endYear})</span>
                    ${isCurrent ? '<span class="current-badge">Current</span>' : ''}
                </li>
            `;
        }).join('');

        // Add click handlers for club links
        clubsList.querySelectorAll('.club-link').forEach(link => {
            link.addEventListener('click', (e) => {
                e.preventDefault();
                navigateToClubRoster(link.dataset.club);
            });
        });

        clubsSection.style.display = '';
    } else {
        clubsSection.style.display = 'none';
    }

    modal.classList.remove('hidden');

    // Focus the close button for accessibility
    modalClose.focus();
}

function closeModal() {
    modal.classList.add('hidden');

    // Restore focus to the element that opened the modal
    if (lastFocusedElement) {
        lastFocusedElement.focus();
        lastFocusedElement = null;
    }
}

// Navigate to a club's roster by searching for it by name
async function navigateToClubRoster(clubName) {
    try {
        // Search for the club
        const response = await fetch(
            `${API_BASE}/clubs/search?query=${encodeURIComponent(clubName)}&limit=5`
        );
        const clubs = await response.json();

        if (clubs.length === 0) {
            showMessage(`Could not find "${clubName}" in database`, 'warning');
            return;
        }

        // Find exact match or use first result
        const exactMatch = clubs.find(c => c.name.toLowerCase() === clubName.toLowerCase());
        const club = exactMatch || clubs[0];

        // Close the modal and switch to roster tab
        closeModal();
        switchTab('roster');

        // Select the club
        await selectClub(club.id, club.name, club.display_name);

    } catch (e) {
        console.error('Error navigating to club:', e);
        showMessage('Error loading club roster', 'error');
    }
}

// Navigate to a national team roster by country name
async function navigateToNationalTeam(nationality) {
    // Search for the national team (try common naming patterns)
    const searchTerms = [
        `${nationality} national`,
        `${nationality} men's national`,
        `${nationality} national football team`
    ];

    try {
        for (const term of searchTerms) {
            const response = await fetch(
                `${API_BASE}/clubs/search?query=${encodeURIComponent(term)}&limit=5`
            );
            const clubs = await response.json();

            // Find a national team (prioritized: senior teams first thanks to backend)
            const nationalTeam = clubs.find(c => c.is_national_team);
            if (nationalTeam) {
                closeModal();
                switchTab('roster');
                await selectClub(nationalTeam.id, nationalTeam.name, nationalTeam.display_name);
                return;
            }
        }

        showMessage(`Could not find ${nationality} national team`, 'warning');

    } catch (e) {
        console.error('Error navigating to national team:', e);
        showMessage('Error loading national team roster', 'error');
    }
}

function showMessage(text, type = 'info') {
    messageDiv.textContent = text;
    messageDiv.className = `message visible ${type}`;

    // Auto-hide after 3 seconds
    setTimeout(() => {
        messageDiv.classList.remove('visible');
    }, 3000);
}

function escapeHtml(text) {
    if (!text) return '';
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

// Tab switching
function switchTab(tabName) {
    tabs.forEach(tab => {
        tab.classList.toggle('active', tab.dataset.tab === tabName);
        tab.setAttribute('aria-selected', tab.dataset.tab === tabName);
    });

    guessedTab.classList.toggle('active', tabName === 'guessed');
    rosterTab.classList.toggle('active', tabName === 'roster');

    // Focus the input for the active tab
    if (tabName === 'guessed') {
        filterInput.focus();
    } else if (tabName === 'roster') {
        clubSearchInput.focus();
    }
}

// Club search with debouncing
function handleClubSearch() {
    const query = clubSearchInput.value.trim();

    // Clear previous timeout
    if (clubSearchTimeout) {
        clearTimeout(clubSearchTimeout);
    }

    // Reset highlighted index on new search
    highlightedResultIndex = -1;

    if (query.length < 2) {
        clubSearchResults.classList.add('hidden');
        clubSearchResults.innerHTML = '';
        return;
    }

    // Debounce the search
    clubSearchTimeout = setTimeout(async () => {
        try {
            const response = await fetch(
                `${API_BASE}/clubs/search?query=${encodeURIComponent(query)}&limit=10`
            );
            const clubs = await response.json();

            if (clubs.length === 0) {
                clubSearchResults.innerHTML = `
                    <div class="club-result" style="color: var(--text-muted); cursor: default;">
                        No clubs found
                    </div>
                `;
            } else {
                clubSearchResults.innerHTML = clubs.map((club, index) => `
                    <div class="club-result" data-club-id="${club.id}" data-club-name="${escapeHtml(club.name)}" data-display-name="${escapeHtml(club.display_name)}" data-index="${index}">
                        <span class="club-result-name">${escapeHtml(club.display_name)}</span>
                        ${club.is_national_team ? '<span class="club-result-badge">National Team</span>' : ''}
                    </div>
                `).join('');

                // Add click handlers
                clubSearchResults.querySelectorAll('.club-result[data-club-id]').forEach(result => {
                    result.addEventListener('click', () => {
                        selectClub(
                            parseInt(result.dataset.clubId),
                            result.dataset.clubName,
                            result.dataset.displayName
                        );
                    });
                });
            }

            clubSearchResults.classList.remove('hidden');
        } catch (e) {
            console.error('Club search error:', e);
        }
    }, 300);
}

// Keyboard navigation for club search results
function handleClubSearchKeydown(e) {
    const results = clubSearchResults.querySelectorAll('.club-result[data-club-id]');
    if (results.length === 0) return;

    if (e.key === 'ArrowDown') {
        e.preventDefault();
        highlightedResultIndex = Math.min(highlightedResultIndex + 1, results.length - 1);
        updateHighlightedResult(results);
    } else if (e.key === 'ArrowUp') {
        e.preventDefault();
        highlightedResultIndex = Math.max(highlightedResultIndex - 1, 0);
        updateHighlightedResult(results);
    } else if (e.key === 'Enter' && highlightedResultIndex >= 0) {
        e.preventDefault();
        const selected = results[highlightedResultIndex];
        if (selected) {
            selectClub(
                parseInt(selected.dataset.clubId),
                selected.dataset.clubName,
                selected.dataset.displayName
            );
        }
    } else if (e.key === 'Escape') {
        clubSearchResults.classList.add('hidden');
        highlightedResultIndex = -1;
    }
}

function updateHighlightedResult(results) {
    results.forEach((result, index) => {
        result.classList.toggle('highlighted', index === highlightedResultIndex);
        if (index === highlightedResultIndex) {
            result.scrollIntoView({ block: 'nearest' });
        }
    });
}

// Select a club and load its roster
async function selectClub(clubId, clubName, displayName) {
    currentClub = { id: clubId, name: clubName, displayName: displayName || clubName };
    clubSearchInput.value = displayName || clubName;
    clubSearchResults.classList.add('hidden');

    // Add to recent clubs for quick access
    addToRecentClubs(clubId, clubName, displayName);

    // Get year range for this club
    try {
        const response = await fetch(`${API_BASE}/clubs/${clubId}/years`);
        const data = await response.json();
        clubYearRange = { min: data.min_year, max: data.max_year };

        // Start with the most recent season
        currentSeason = Math.min(clubYearRange.max, new Date().getFullYear());

        await loadRoster();
    } catch (e) {
        console.error('Error getting club years:', e);
        clubYearRange = { min: 2000, max: new Date().getFullYear() };
        currentSeason = new Date().getFullYear();
        await loadRoster();
    }
}

// Load roster for current club and season
async function loadRoster() {
    if (!currentClub) return;

    // Show loading state
    rosterPlayers.classList.add('loading');

    try {
        const response = await fetch(
            `${API_BASE}/clubs/${currentClub.id}/roster?season=${currentSeason}`
        );
        const data = await response.json();

        // Update UI - use display_name for national teams
        rosterClubName.textContent = data.display_name || data.club_name;
        rosterSeason.textContent = data.season;
        rosterTotalCount.textContent = data.total_count;

        // Get set of guessed player IDs for fast lookup
        const guessedIds = new Set(guessedPlayers.map(p => p.id));

        // Count guessed players in this roster
        const guessedInRoster = data.players.filter(p => guessedIds.has(p.id)).length;
        rosterGuessedCount.textContent = guessedInRoster;

        // Render roster
        if (data.players.length === 0) {
            rosterPlayers.innerHTML = `
                <div class="roster-empty-inline">
                    No player data available for this season.
                </div>
            `;
        } else {
            // Sort: guessed first, then alphabetically
            const sortedPlayers = [...data.players].sort((a, b) => {
                const aGuessed = guessedIds.has(a.id);
                const bGuessed = guessedIds.has(b.id);
                if (aGuessed && !bGuessed) return -1;
                if (!aGuessed && bGuessed) return 1;
                return a.name.localeCompare(b.name);
            });

            rosterPlayers.innerHTML = sortedPlayers.map(player => {
                const isGuessed = guessedIds.has(player.id);
                return `
                    <div class="roster-player ${isGuessed ? 'guessed' : 'unguessed'}" ${isGuessed ? `data-player-id="${player.id}" tabindex="0" role="button" aria-label="View details for ${escapeHtml(player.name)}"` : ''}>
                        <div class="${isGuessed ? '' : 'player-name-hidden'}">
                            ${isGuessed ? escapeHtml(player.name) : '?????'}
                        </div>
                        ${player.position ? `<div class="roster-player-position">${escapeHtml(player.position)}</div>` : ''}
                    </div>
                `;
            }).join('');

            // Add click handlers for guessed players
            rosterPlayers.querySelectorAll('.roster-player.guessed').forEach(card => {
                const openModal = () => {
                    const playerId = parseInt(card.dataset.playerId);
                    const player = guessedPlayers.find(p => p.id === playerId);
                    if (player) showPlayerModal(player);
                };

                card.addEventListener('click', openModal);
                card.addEventListener('keydown', (e) => {
                    if (e.key === 'Enter' || e.key === ' ') {
                        e.preventDefault();
                        openModal();
                    }
                });
            });
        }

        // Update season buttons
        seasonPrevBtn.disabled = currentSeason <= clubYearRange.min;
        seasonNextBtn.disabled = currentSeason >= clubYearRange.max;

        // Show roster display
        rosterDisplay.classList.remove('hidden');
        rosterEmpty.style.display = 'none';

    } catch (e) {
        console.error('Error loading roster:', e);
    } finally {
        rosterPlayers.classList.remove('loading');
    }
}

// Change season
function changeSeason(delta) {
    const newSeason = currentSeason + delta;
    if (newSeason >= clubYearRange.min && newSeason <= clubYearRange.max) {
        currentSeason = newSeason;
        loadRoster();
    }
}
