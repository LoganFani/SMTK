/**
 * Handle File Upload Reading
 * Listens for change on the hidden file input and populates the textarea
 */
document.getElementById('fileUpload').addEventListener('change', function(e) {
    const file = e.target.files[0];
    if (!file) return;

    const reader = new FileReader();
    reader.onload = function(e) {
        document.getElementById('transcriptInput').value = e.target.result;
    };
    reader.readAsText(file);
});

/**
 * Send Data to FastAPI
 * Packages the text and language selections into a POST request
 */
async function sendData() {
    const transcript = document.getElementById('transcriptInput').value;
    console.log("Transcript:", transcript);
    const source = document.getElementById('sourceLang').value;
    console.log("Source Language:", source);
    const target = document.getElementById('targetLang').value;
    console.log("Target Language:", target);

    const deckElement = document.getElementById('toDeck'); // Get the element first
    const deckValue = deckElement ? deckElement.value : "default_deck"; // Fallback just in case

    if (!transcript.trim()) {
        alert("Please provide some text or upload a file first!");
        return;
    }

    const payload = {
        content: transcript,
        target_lang: source,
        native_lang: target,
        deck: deckValue
    };

    try {
        const response = await fetch('http://127.0.0.1:8000/generate', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });

        if (response.ok) {
            const result = await response.json();
            console.log("Success:", result);
            alert("Mining process started successfully!");
        } else {
            alert("Backend returned an error: " + response.statusText);
        }
    } catch (error) {
        console.error("Connection Error:", error);
        alert("Could not connect to the Python backend. Make sure it is running on port 8000.");
    }
}