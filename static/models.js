async function loadModels() {
    const response = await fetch('/models/list');
    const data = await response.json();
    const container = document.getElementById('modelList');
    container.innerHTML = '';

    data.models.forEach(model => {
        const card = document.createElement('div');
        card.className = 'model-card'; // Styling handled in components.css
        
        const statusClass = model.downloaded ? 'status-installed' : 'status-missing';
        const statusText = model.downloaded ? '● INSTALLED' : '○ AVAILABLE';

        card.innerHTML = `
            <div class="model-info">
                <span class="status-badge ${statusClass}">${statusText}</span>
                <h4 style="margin: 10px 0 5px 0; font-size: 1.1rem;">${model.name}</h4>
                <p style="font-family: 'JetBrains Mono'; font-size: 0.7rem; color: var(--text-dim);">${model.path}</p>
            </div>
            <div class="model-actions" style="margin-top: 20px; display: flex; gap: 10px;">
                ${model.downloaded 
                    ? `<button class="btn-delete" onclick="deleteModel('${model.path}')">DELETE</button>` 
                    : `<button class="btn" style="padding: 5px 15px; font-size: 0.7rem;" onclick="downloadModel('${model.path}', this)">DOWNLOAD</button>`}
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


async function deleteModel(repoId) {
    if (!confirm(`Are you sure you want to delete the local files for ${repoId}? You will need to re-download them to use this language.`)) {
        return;
    }

    const response = await fetch(`/models/delete/${encodeURIComponent(repoId)}`, {
        method: 'DELETE'
    });

    if (response.ok) {
        loadModels(); // Refresh the list
    } else {
        alert("Failed to delete model files.");
    }
}

document.addEventListener('DOMContentLoaded', loadModels);