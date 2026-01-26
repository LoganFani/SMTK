async function loadDecks() {
    const response = await fetch('/decks/list');
    const data = await response.json();
    const tableBody = document.getElementById('deckTableBody');
    tableBody.innerHTML = '';

    data.decks.forEach(deckName => {
        if (deckName === "sqlite_sequence") return;

        const row = document.createElement('tr');
        row.innerHTML = `
            <td>
                <a href="/view_deck?name=${encodeURIComponent(deckName)}" class="deck-link">
                    ${deckName}
                </a>
            </td>
            <td style="text-align: right; position: relative;">
                <div class="action-dropdown">
                    <button class="btn btn-small action-trigger" onclick="toggleMenu(this)">
                        ACTIONS ▾
                    </button>
                    <div class="action-menu">
                        <button onclick="exportDeck('${deckName}', 'csv')">EXPORT CSV</button>
                        <button onclick="exportDeck('${deckName}', 'anki_apkg')">EXPORT ANKI</button>
                        <button onclick="exportDeck('${deckName}', 'push')">PUSH TO ANKI</button>
                        <div class="menu-divider"></div>
                        <button class="menu-delete" onclick="removeDeck('${deckName}')">DELETE DECK</button>
                    </div>
                </div>
            </td>
        `;
        tableBody.appendChild(row);
    });
}

// Simple toggle function for the menu
function toggleMenu(btn) {
    // Close all other menus first
    document.querySelectorAll('.action-menu').forEach(menu => {
        if (menu !== btn.nextElementSibling) menu.classList.remove('show');
    });
    btn.nextElementSibling.classList.toggle('show');
}

// Close menus if clicking outside
window.onclick = function(event) {
    if (!event.target.matches('.action-trigger')) {
        document.querySelectorAll('.action-menu').forEach(menu => menu.classList.remove('show'));
    }
}

async function exportDeck(deckName, format) {
    if (format === 'push') {
        try {
            const response = await fetch(`/decks/get_cards/${encodeURIComponent(deckName)}`);
            const data = await response.json();
            
            // FIX: Check if 'data' is an array OR if it has a 'cards' property
            const cardsList = Array.isArray(data) ? data : (data.cards || []);

            if (cardsList.length === 0) {
                alert("This deck is empty!");
                return;
            }

            // Save the extracted list to session storage
            sessionStorage.setItem('pending_cards', JSON.stringify(cardsList));
            window.location.href = '/push_confirmation';
        } catch (e) {
            console.error("Fetch Error:", e);
            alert("Failed to load deck data for push.");
        }
    } else {
        window.location.href = `/export?format=${format}&name=${encodeURIComponent(deckName)}`;
    }
}

async function addDeck() {
    const inputField = document.getElementById('newDeckName');
    const deckName = inputField.value.trim();
    
    if (!deckName) {
        alert("Please enter a valid deck name.");
        return;
    }

    const response = await fetch('/decks/create', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ deck_name: deckName })
    });

    if (response.ok) {
        inputField.value = ''; // Corrected: clear the actual input element
        await loadDecks();
    } else {
        alert("Failed to create deck.");
    }
}

async function removeDeck(deckName) {
    if (!confirm(`Are you sure you want to delete the deck "${deckName}"? This action cannot be undone.`)) {
        return;
    }
    const response = await fetch(`decks/delete/${deckName}`, {
        method: 'DELETE'
    });

    if (response.ok) {
        await loadDecks();
    } else {
        alert("Failed to delete deck.");
    }
}

// Using the same event listener style as your other pages
document.addEventListener('DOMContentLoaded', loadDecks);