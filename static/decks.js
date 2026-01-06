
async function loadDecks() {
    
    const response = await fetch('/decks/list');
    const data = await response.json();

    const tableBody = document.getElementById('deckTableBody');
    tableBody.innerHTML = '';

    data.decks.forEach(deckName => {
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