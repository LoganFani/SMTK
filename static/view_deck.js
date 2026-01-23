const urlParams = new URLSearchParams(window.location.search);
const deckName = urlParams.get('name');
let deckCards = [];

document.getElementById('deckTitle').textContent = `Deck: ${deckName}`;

async function loadDeckData() {
    const response = await fetch(`/decks/get_cards/${encodeURIComponent(deckName)}`);
    deckCards = await response.json();
    renderCards(deckCards);
}

function renderCards(cards) {
    const tbody = document.getElementById('cardTableBody');
    // Using deckCards index for updateLocal, but card.id for server-side deletion
    tbody.innerHTML = cards.map((card, index) => `
        <tr>
            <td>
                <textarea 
                    onchange="updateLocal(${index}, 'source', this.value)"
                    rows="2"
                >${card.source}</textarea>
            </td>
            <td>
                <textarea 
                    onchange="updateLocal(${index}, 'translation', this.value)"
                    rows="2"
                >${card.translation}</textarea>
            </td>
            <td style="text-align: right;">
                <button class="btn-delete" onclick="deleteCard(${card.id})">
                    DELETE
                </button>
            </td>
        </tr>
    `).join('');
}

function updateLocal(index, field, value) {
    deckCards[index][field] = value;
}

async function saveChanges() {
    const response = await fetch(`/decks/update_batch`, {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({ deck: deckName, cards: deckCards })
    });
    if (response.ok) alert("Changes saved to Database!");
}

async function deleteCard(cardId) {
    if (!confirm("Are you sure you want to delete this card?")) return;

    try {
        const response = await fetch(`/decks/${encodeURIComponent(deckName)}/cards/${cardId}`, {
            method: 'DELETE'
        });

        if (response.ok) {
            // Remove from local array and re-render
            deckCards = deckCards.filter(card => card.id !== cardId);
            renderCards(deckCards);
        } else {
            alert("Failed to delete card from server.");
        }
    } catch (error) {
        console.error("Delete error:", error);
    }
}

/**
 * Optional: Search/Filter function for the toolbar
 */
function filterView() {
    const term = document.getElementById('cardSearch').value.toLowerCase();
    const filtered = deckCards.filter(card => 
        card.source.toLowerCase().includes(term) || 
        card.translation.toLowerCase().includes(term)
    );
    renderCards(filtered);
}

loadDeckData();