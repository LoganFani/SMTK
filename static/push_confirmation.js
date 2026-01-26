let pendingCards = [];
let ankiUrl = "";

async function init() {
    // 1. Load cards from session
    const data = sessionStorage.getItem('pending_cards');
    if (!data) { window.location.href = '/'; return; }
    pendingCards = JSON.parse(data);
    document.getElementById('card_count').innerText = `READY TO PUSH: ${pendingCards.length} CARDS`;

    // 2. Load settings to get Anki URL
    const settingsResp = await fetch('/api/settings');
    const settings = await settingsResp.json();
    ankiUrl = settings.anki_url || 'http://localhost:8765';
    if (!ankiUrl.startsWith('http')) ankiUrl = 'http://' + ankiUrl;

    // 3. Fetch Decks from Anki
    try {
        const response = await fetch(ankiUrl, {
            method: 'POST',
            body: JSON.stringify({ "action": "deckNames", "version": 6 })
        });
        const res = await response.json();
        const select = document.getElementById('anki_deck_select');
        select.innerHTML = '<option value="">-- Select Existing Deck --</option>';
        res.result.forEach(name => {
            const opt = document.createElement('option');
            opt.value = name;
            opt.innerText = name;
            select.appendChild(opt);
        });
    } catch (e) {
        alert("COULD_NOT_REACH_ANKI: Ensure Anki is open.");
    }
}

async function executePush() {
    const existingDeck = document.getElementById('anki_deck_select').value;
    const newDeck = document.getElementById('new_deck_name').value.trim();
    const finalDeckName = newDeck || existingDeck;

    if (!finalDeckName) return alert("Please select or name a deck.");

    // --- NEW: PRE-FLIGHT DECK CREATION ---
    try {
        const createResp = await fetch(ankiUrl, {
            method: 'POST',
            body: JSON.stringify({
                action: "createDeck",
                version: 6,
                params: { deck: finalDeckName }
            })
        });
        const createResult = await createResp.json();
        if (createResult.error) throw new Error("DECK_CREATION_FAILED: " + createResult.error);
    } catch (e) {
        alert(e.message);
        return;
    }
    // --- END PRE-FLIGHT ---

    // Show Progress Bar
    const progressContainer = document.getElementById('progress_container');
    const progressBar = document.getElementById('progress_bar');
    const progressPercent = document.getElementById('progress_percent');
    progressContainer.style.display = 'block';

    const CHUNK_SIZE = 5;
    let successCount = 0;

    for (let i = 0; i < pendingCards.length; i += CHUNK_SIZE) {
        const chunk = pendingCards.slice(i, i + CHUNK_SIZE);
        
        const notes = chunk.map(c => ({
            deckName: finalDeckName,
            modelName: "Basic",
            fields: { Front: c.source, Back: c.translation },
            tags: ["SMTK_PUSH"]
        }));

        try {
            const response = await fetch(ankiUrl, {
                method: 'POST',
                body: JSON.stringify({
                    action: "addNotes",
                    version: 6,
                    params: { notes: notes }
                })
            });
            const result = await response.json();
            
            if (result.error) throw new Error(result.error);
            
            successCount += chunk.length;
            const percent = Math.round((successCount / pendingCards.length) * 100);
            progressBar.style.width = `${percent}%`;
            progressPercent.innerText = `${percent}%`;

        } catch (e) {
            alert(`PUSH_INTERRUPTED: ${e.message}`);
            return; 
        }
    }

    alert(`SUCCESS: Uploaded ${successCount} cards to ${finalDeckName}`);
    sessionStorage.removeItem('pending_cards');
    window.location.href = '/decks';
}

document.addEventListener('DOMContentLoaded', init);