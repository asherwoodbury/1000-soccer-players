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
    showRosterLookup: true
};

// State
let sessionId = null;
let guessedPlayers = [];
let displaySettings = { ...DEFAULT_SETTINGS };

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

// DOM Elements
const playerInput = document.getElementById('player-input');
const guessForm = document.getElementById('guess-form');
const messageDiv = document.getElementById('message');
const playerCountEl = document.getElementById('player-count');
const playersList = document.getElementById('players-list');
const filterInput = document.getElementById('filter-input');
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
    applySettingsToUI();
    await initSession();
    setupEventListeners();
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

    // Tabs
    tabs.forEach(tab => {
        tab.addEventListener('click', () => {
            switchTab(tab.dataset.tab);
        });
    });

    // Club search
    clubSearchInput.addEventListener('input', handleClubSearch);
    clubSearchInput.addEventListener('focus', () => {
        if (clubSearchInput.value.length >= 2) {
            clubSearchResults.classList.remove('hidden');
        }
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
    renderPlayersList();
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

    renderPlayersList(isNewPlayer);
}

function renderPlayersList(highlightNew = false) {
    const filter = filterInput.value.toLowerCase().trim();

    let filteredPlayers = guessedPlayers;

    if (filter) {
        filteredPlayers = guessedPlayers.filter(player => {
            // Match on name, nationality, or clubs
            if (player.name.toLowerCase().includes(filter)) return true;
            if (player.nationality?.toLowerCase().includes(filter)) return true;
            if (player.top_clubs?.some(c => c.toLowerCase().includes(filter))) return true;
            return false;
        });
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
            playersList.innerHTML = `
                <div class="empty-state">
                    No players match your filter.
                </div>
            `;
        }
        return;
    }

    playersList.innerHTML = filteredPlayers.map((player, index) => {
        const isNew = highlightNew && index === 0 && player.isNew;

        // Build info line based on settings
        const infoParts = [];
        if (displaySettings.showNationality && player.nationality) {
            infoParts.push(escapeHtml(player.nationality));
        }
        if (displaySettings.showPosition && player.position) {
            infoParts.push(escapeHtml(player.position));
        }
        if (displaySettings.showCareerSpan && player.career_span) {
            infoParts.push(escapeHtml(player.career_span));
        }
        const infoLine = infoParts.join(' · ') || '';

        // Build clubs line based on settings
        const clubsLine = displaySettings.showTopClubs && player.top_clubs?.length
            ? player.top_clubs.map(c => escapeHtml(c)).join(', ')
            : '';

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

    // Add click and keyboard handlers
    document.querySelectorAll('.player-card').forEach(card => {
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

let lastFocusedElement = null;

function showPlayerModal(player) {
    // Store the element that had focus before opening modal
    lastFocusedElement = document.activeElement;

    document.getElementById('modal-player-name').textContent = player.name;

    // Nationality
    const nationalityRow = document.getElementById('modal-nationality-row');
    if (displaySettings.showNationality) {
        document.getElementById('modal-nationality').textContent = player.nationality || 'Unknown';
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

    // Top clubs
    const topClubsSection = document.getElementById('modal-top-clubs-section');
    if (displaySettings.showTopClubs && player.top_clubs?.length) {
        document.getElementById('modal-top-clubs').textContent = player.top_clubs.join(', ');
        topClubsSection.style.display = '';
    } else {
        topClubsSection.style.display = 'none';
    }

    // Full club history
    const clubsSection = document.getElementById('modal-clubs-section');
    const clubsList = document.getElementById('modal-clubs');

    if (displaySettings.showTopClubs && displaySettings.showFullHistory && player.clubs?.length) {
        clubsList.innerHTML = player.clubs.map(club => {
            const startYear = club.start_date ? club.start_date.substring(0, 4) : '?';
            const endYear = club.end_date ? club.end_date.substring(0, 4) : 'Present';
            const isNational = club.is_national_team;

            return `
                <li class="${isNational ? 'national-team' : ''}">
                    ${escapeHtml(club.name)}
                    <span class="club-dates">(${startYear} - ${endYear})</span>
                </li>
            `;
        }).join('');
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
                    <div class="club-result" data-club-id="${club.id}" data-club-name="${escapeHtml(club.name)}" data-index="${index}">
                        <span class="club-result-name">${escapeHtml(club.name)}</span>
                        ${club.is_national_team ? '<span class="club-result-badge">National Team</span>' : ''}
                    </div>
                `).join('');

                // Add click handlers
                clubSearchResults.querySelectorAll('.club-result[data-club-id]').forEach(result => {
                    result.addEventListener('click', () => {
                        selectClub(
                            parseInt(result.dataset.clubId),
                            result.dataset.clubName
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
                selected.dataset.clubName
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
async function selectClub(clubId, clubName) {
    currentClub = { id: clubId, name: clubName };
    clubSearchInput.value = clubName;
    clubSearchResults.classList.add('hidden');

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

        // Update UI
        rosterClubName.textContent = data.club_name;
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
