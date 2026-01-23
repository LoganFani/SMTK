// Function to apply the theme based on localStorage
function applyTheme() {
    const savedTheme = localStorage.getItem('smtk-theme');
    const body = document.body;
    const themeToggle = document.getElementById('themeToggle');

    if (savedTheme === 'light') {
        body.classList.add('light-mode');
        if (themeToggle) themeToggle.textContent = "THEME: LIGHT";
    } else {
        body.classList.remove('light-mode');
        if (themeToggle) themeToggle.textContent = "THEME: DARK";
    }
}

// Function to toggle and save the theme
function toggleTheme() {
    const body = document.body;
    const isLight = body.classList.toggle('light-mode');
    
    // Save the new state
    localStorage.setItem('smtk-theme', isLight ? 'light' : 'dark');
    
    // Update the button text if it exists on the page
    const themeToggle = document.getElementById('themeToggle');
    if (themeToggle) {
        themeToggle.textContent = isLight ? "THEME: LIGHT" : "THEME: DARK";
    }
}

// Initialize on every page load
document.addEventListener('DOMContentLoaded', () => {
    applyTheme();
    
    const themeToggle = document.getElementById('themeToggle');
    if (themeToggle) {
        themeToggle.addEventListener('click', toggleTheme);
    }
});