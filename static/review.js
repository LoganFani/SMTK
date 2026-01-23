let allCards = JSON.parse(sessionStorage.getItem('pendingCards') || "[]");

async function initPage() {
    renderTable(allCards);
    await populateDeckDropdown();
}

/**
 * Fetches existing decks from the DB to fill the select menu
 */
async function populateDeckDropdown() {
    const response = await fetch('/decks/list');
    const data = await response.json();
    const dropdown = document.getElementById('toDeck');

    // Keep the default option
    dropdown.innerHTML = '<option value="select">Select Deck</option>';

    if (data.decks) {
        data.decks.forEach(deckName => {
            if (deckName === "sqlite_sequence") return;
            const option = document.createElement('option');
            option.value = deckName;
            option.textContent = deckName;
            dropdown.appendChild(option);
        });
    }
}

function renderTable(cards) {
    const tbody = document.getElementById('deckTableBody');
    tbody.innerHTML = '';
    
    cards.forEach((card, index) => {
        const row = `
            <tr>
                <td>
                    <textarea 
                        onchange="updateCard(${index}, 'source', this.value)"
                        rows="2"
                    >${card.source}</textarea>
                </td>
                <td>
                    <textarea 
                        onchange="updateCard(${index}, 'translation', this.value)"
                        rows="2"
                    >${card.translation}</textarea>
                </td>
                <td style="text-align: right;">
                    <button class="btn-delete" onclick="deleteRow(${index})">
                        DELETE
                    </button>
                </td>
            </tr>`;
        tbody.innerHTML += row;
    });
}

function updateCard(index, field, value) {
    allCards[index][field] = value;
}

function deleteRow(index) {
    allCards.splice(index, 1);
    renderTable(allCards);
}

/**
 * Sends the final reviewed cards to the backend to be saved
 */
async function addCardsToDeck() {
    const deckName = document.getElementById('toDeck').value;
    if (deckName === 'select' || deckName === 'default_deck') {
        alert("Please select a valid deck!");
        return;
    }

    const response = await fetch('/decks/insert_batch', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            deck: deckName,
            cards: allCards
        })
    });

    if (response.ok) {
        alert("Success! Cards added to " + deckName);
        window.location.href = "/decks"; // Go see your updated deck
    } else {
        alert("Error saving cards.");
    }
}

document.addEventListener('DOMContentLoaded', initPage);