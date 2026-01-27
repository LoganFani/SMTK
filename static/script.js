async function loadDownloadedModels() {
    const dropdown = document.getElementById('modelSelect');
    const response = await fetch('/models/downloaded');
    const data = await response.json();
    
    dropdown.innerHTML = '';
    
    data.downloaded_models.forEach(model => {
        const opt = document.createElement('option');
        // value is "Helsinki-NLP/opus-mt-en-es"
        opt.value = model.repo_id; 
        // text is "English ➜ Spanish"
        opt.textContent = model.name; 
        dropdown.appendChild(opt);
    });
}

// Character Count for Transcript Input
const transcript = document.getElementById('transcriptInput');
const charCount = document.getElementById('charCount');

transcript.addEventListener('input', () => {
charCount.innerText = `chars ${transcript.value.length}`;
})


// File Upload Handling
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
    const modelId = document.getElementById('modelSelect').value;

    const joinSentences = document.getElementById('join_sentences').checked;

    if (!transcript.trim()) {
        alert("Please provide text or upload a file first!");
        return;
    }

    // Capture the button to show loading state
    const btn = document.getElementById('generate-btn');
    const originalText = btn.textContent;
    btn.textContent = "Processing...";
    btn.disabled = true;

    const payload = {
        content: transcript,
        model_id: modelId,
        join_sentences: joinSentences
    };

    try {
        const response = await fetch('http://127.0.0.1:8000/generate', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });

        if (response.ok) {
            const result = await response.json();
            
            // 1. Store the translations in sessionStorage
            sessionStorage.setItem('pendingCards', JSON.stringify(result.translations));

            // 2. Redirect to the review page
            window.location.href = "/review";
        } else {
            alert("Backend returned an error: " + response.statusText);
        }
    } catch (error) {
        console.error("Connection Error:", error);
        alert("Could not connect to the Python backend.");
    } finally {
        btn.textContent = originalText;
        btn.disabled = false;
    }


}

document.addEventListener('DOMContentLoaded', loadDownloadedModels);
