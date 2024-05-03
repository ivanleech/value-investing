document.addEventListener('DOMContentLoaded', function() {
    const toggleButton = document.getElementById('toggleTheme');
    const themeIcon = document.getElementById('themeIcon');

    // Function to get the current theme from local storage
    function getCurrentTheme() {
        return localStorage.getItem('theme') || 'dark';
    }

    // Set initial icon based on the current theme
    themeIcon.textContent = getCurrentTheme() === 'dark' ? '☀️' : '🌙';

    // Add event listener to the toggle button
    toggleButton.addEventListener('click', function() {
        const currentTheme = getCurrentTheme();
        const newTheme = currentTheme === 'dark' ? 'light' : 'dark';

        // Update the theme icon first
        updateThemeIcon(newTheme);

        // Update the theme in local storage
        localStorage.setItem('theme', newTheme);

        // Update the theme stylesheet
        updateTheme(newTheme);
    });
});

function updateThemeIcon(theme) {
    const themeIcon = document.getElementById('themeIcon');
    themeIcon.textContent = theme === 'dark' ? '☀️' : '🌙';
}

function updateTheme(theme) {
    // Update the href attribute of the stylesheet based on the selected theme
    document.getElementById('theme-style').href = `static/css/${theme}-theme.css`;
}
