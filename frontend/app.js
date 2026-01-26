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
    showFullHistory: true
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
    fullHistory: document.getElementById('setting-full-history')
};

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
    updateFullHistoryState();
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
