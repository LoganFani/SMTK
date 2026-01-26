/**
 * Main switchboard for exports.
 */
async function handleExport(cards, defaultName, format) {
    let fileName = prompt("ENTER_FILENAME:", defaultName);
    if (fileName === null) return;
    if (fileName.trim() === "") fileName = "SMTK_Export";

    if (format === 'anki_connect') {
        await pushToAnki(cards, fileName);
    } else {
        await downloadFile(cards, fileName, format);
    }
}

/**
 * Path A: Download CSV or APKG via the Backend
 */
async function downloadFile(cards, fileName, format) {
    try {
        const response = await fetch(`/export?format=${format}&name=${encodeURIComponent(fileName)}`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(cards)
        });

        if (!response.ok) throw new Error("NETWORK_RESPONSE_NOT_OK");

        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `${fileName}.${format === 'csv' ? 'csv' : 'apkg'}`;
        document.body.appendChild(a);
        a.click();
        window.URL.revokeObjectURL(url);
        a.remove();
    } catch (e) {
        console.error("DOWNLOAD_ERROR:", e);
        alert("FAILED_TO_GENERATE_FILE");
    }
}

async function pushToAnki(cards) {
    // Store cards in session storage so the next page can grab them
    sessionStorage.setItem('pending_cards', JSON.stringify(cards));
    // Redirect to the confirmation screen
    window.location.href = '/push_confirmation';
}