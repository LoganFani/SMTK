function showTab(tabId) {
    document.querySelectorAll('.settings-tab').forEach(tab => tab.style.display = 'none');
    document.querySelectorAll('.tab-btn').forEach(btn => btn.classList.remove('active'));
    
    document.getElementById(tabId).style.display = 'block';
    event.currentTarget.classList.add('active');
}

async function loadSettings() {
    const response = await fetch('/api/settings');
    const data = await response.json();
    
    document.getElementById('model_dir').value = data.model_dir;
    document.getElementById('default_name').value = data.default_name;
    document.getElementById('anki_url').value = data.anki_url;
    document.getElementById('anki_deck').value = data.anki_deck;
    document.getElementById('anki_key').value = data.anki_key;
}

async function saveSettings() {
    const settings = {
        model_dir: document.getElementById('model_dir').value,
        default_name: document.getElementById('default_name').value,
        anki_url: document.getElementById('anki_url').value,
        anki_deck: document.getElementById('anki_deck').value,
        anki_key: document.getElementById('anki_key').value
    };

    const response = await fetch('/api/settings', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(settings)
    });

    if (response.ok) {
        alert("SETTINGS_SAVED_SUCCESSFULLY");
    }
}

async function testAnkiConnection() {
    let url = document.getElementById('anki_url').value || 'http://localhost:8765';
    // FIX: Ensure the URL has the http protocol prefix
    if (!url.startsWith('http://') && !url.startsWith('https://')) {
        url = 'http://' + url;
    }

    const statusEl = document.getElementById('connection_status');
    
    statusEl.innerText = "CHECKING...";
    statusEl.style.color = "var(--text-dim)";

    try {
        const response = await fetch(url, {
            method: 'POST',
            body: JSON.stringify({ "action": "version", "version": 6 })
        });

        const data = await response.json();
        
        if (data.result) {
            statusEl.innerText = `CONNECTED (v${data.result})`;
            statusEl.style.color = "var(--primary-green)";
        } else {
            throw new Error("Invalid Response");
        }
    } catch (e) {
        statusEl.innerText = "OFFLINE: Check Anki & AnkiConnect";
        statusEl.style.color = "#ff5555"; // Terminal Red
    }
}

document.addEventListener('DOMContentLoaded', loadSettings);