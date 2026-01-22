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
        tbody.innerHTML += `
            <tr style="border-bottom: 1px solid #eee;">
                <td style="padding: 10px;"><input type="text" value="${card.source}" onchange="updateCard(${index}, 'source', this.value)" style="width:100%;"></td>
                <td style="padding: 10px;"><input type="text" value="${card.translation}" onchange="updateCard(${index}, 'translation', this.value)" style="width:100%;"></td>
                <td style="padding: 10px;"><button onclick="deleteRow(${index})" style="color:red; cursor:pointer;">✕</button></td>
            </tr>`;
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