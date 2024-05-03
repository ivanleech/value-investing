document.addEventListener('DOMContentLoaded', function() {
    const toggleButton = document.getElementById('toggleAdvanced');
    const advancedOptions = document.getElementById('advancedOptions');

    // Set initial visibility based on button state
    advancedOptions.style.display = 'none';

    // Add event listener to the toggle button
    toggleButton.addEventListener('click', function() {
        const isVisible = advancedOptions.style.display === 'block';
        advancedOptions.style.display = isVisible ? 'none' : 'block';
        toggleButton.textContent = isVisible ? 'Show Advanced Options ▼' : 'Hide Advanced Options ▲';
    });
});
