async function loadDecks() {
    const response = await fetch('/decks/list');
    const data = await response.json();

    const tableBody = document.getElementById('deckTableBody');
    tableBody.innerHTML = '';

    data.decks.forEach(deckName => {
        if (deckName === "sqlite_sequence") return;

        // Use the card-table classes and the btn-delete class from components.css
        const row = `
            <tr>
                <td>
                    <a href="/view_deck?name=${encodeURIComponent(deckName)}" class="deck-link">
                        ${deckName}
                    </a>
                </td>
                <td style="text-align: right;">
                    <button class="btn-delete" 
                            onclick="removeDeck('${deckName}')">DELETE</button>
                </td>
            </tr>`;
        tableBody.innerHTML += row;
    });
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