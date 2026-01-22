async function loadModels() {
    const response = await fetch('/models/list');
    const data = await response.json();
    const container = document.getElementById('modelList');
    container.innerHTML = '';

    data.models.forEach(model => {
        const card = document.createElement('div');
        card.className = 'model-card'; // Add styling for this in style.css
        card.innerHTML = `
            <div style="border: 1px solid #ddd; padding: 15px; margin: 10px 0; border-radius: 8px; display: flex; justify-content: space-between; align-items: center;">
                <div>
                    <strong>${model.name}</strong><br>
                    <small style="color: #666;">${model.path}</small>
                </div>
                <div>
                    ${model.downloaded 
                        ? '<span style="color: green;">✓ Downloaded</span>' 
                        : `<button class="btn btn-small" onclick="downloadModel('${model.path}', this)">Download</button>`}
                </div>
            </div>
        `;
        container.appendChild(card);
    });
}

async function downloadModel(path, btn) {
    btn.textContent = "Downloading...";
    btn.disabled = true;

    const response = await fetch('/models/download', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ path: path })
    });

    if (response.ok) {
        alert("Download complete!");
        loadModels();
    } else {
        alert("Download failed.");
        btn.textContent = "Download";
        btn.disabled = false;
    }
}

document.addEventListener('DOMContentLoaded', loadModels);