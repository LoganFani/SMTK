
async function loadDecks() {
    
    const response = await fetch('/decks/list');
    const data = await response.json();

    const tableBody = document.getElementById('deckTableBody');
    tableBody.innerHTML = '';

    data.decks.forEach(deckName => {
        // Skip sql lite made table (cannot delete)
        if (deckName === "sqlite_sequence") return;
        const row = `
            <tr style="border-bottom: 1px solid #eee;">
                <td style="padding: 10px;">${deckName}</td>
                <td style="padding: 10px; text-align: right;">
                    <button class="btn btn-manage" 
                            style="background-color: #ff7675; color: white; border: none;" 
                            onclick="removeDeck('${deckName}')">Delete</button>
                </td>
            </tr>`;
        tableBody.innerHTML += row;
    });
}

async function addDeck() {
    const deckName = document.getElementById('newDeckName').value.trim();
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
        deckName.value = '';
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
// Load decks on page load
window.onload = loadDecks;