/**
 * 1000 Soccer Players - Frontend Application
 */

const API_BASE = 'http://localhost:8000/api';

// State
let sessionId = null;
let guessedPlayers = [];

// DOM Elements
const playerInput = document.getElementById('player-input');
const guessForm = document.getElementById('guess-form');
const messageDiv = document.getElementById('message');
const playerCountEl = document.getElementById('player-count');
const playersList = document.getElementById('players-list');
const filterInput = document.getElementById('filter-input');
const filteredCountEl = document.getElementById('filtered-count');
const modal = document.getElementById('player-modal');
const modalClose = document.querySelector('.modal-close');

// Initialize
document.addEventListener('DOMContentLoaded', async () => {
    await initSession();
    setupEventListeners();
});

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
    document.addEventListener('keydown', (e) => {
        if (e.key === 'Escape') closeModal();
    });
}

async function handleGuess(e) {
    e.preventDefault();

    const name = playerInput.value.trim();
    if (!name) return;

    // Disable input while processing
    playerInput.disabled = true;
    const submitBtn = guessForm.querySelector('button');
    submitBtn.disabled = true;

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
                guessed_at: new Date().toISOString()
            });
        }

        updateUI();
        playerInput.value = '';

    } catch (e) {
        showMessage('Error connecting to server', 'error');
        console.error(e);
    }

    playerInput.disabled = false;
    submitBtn.disabled = false;
    playerInput.focus();
}

function handleFilter() {
    renderPlayersList();
}

function updateUI() {
    playerCountEl.textContent = guessedPlayers.length;
    renderPlayersList();
}

function renderPlayersList() {
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

    playersList.innerHTML = filteredPlayers.map(player => `
        <div class="player-card" data-player-id="${player.id}">
            <div class="player-name">${escapeHtml(player.name)}</div>
            <div class="player-info">
                ${escapeHtml(player.nationality || 'Unknown')} · ${escapeHtml(player.position || 'Unknown')}
            </div>
            <div class="player-clubs">
                ${player.top_clubs?.map(c => escapeHtml(c)).join(', ') || 'No clubs'}
            </div>
        </div>
    `).join('');

    // Add click handlers
    document.querySelectorAll('.player-card').forEach(card => {
        card.addEventListener('click', () => {
            const playerId = parseInt(card.dataset.playerId);
            const player = guessedPlayers.find(p => p.id === playerId);
            if (player) showPlayerModal(player);
        });
    });
}

function showPlayerModal(player) {
    document.getElementById('modal-player-name').textContent = player.name;
    document.getElementById('modal-nationality').textContent = player.nationality || 'Unknown';
    document.getElementById('modal-position').textContent = player.position || 'Unknown';

    const clubsList = document.getElementById('modal-clubs');

    if (player.clubs && player.clubs.length > 0) {
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
    } else {
        clubsList.innerHTML = '<li>No club history available</li>';
    }

    modal.classList.remove('hidden');
}

function closeModal() {
    modal.classList.add('hidden');
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
