/**
 * Theme Switcher Module
 * Handles Light/Dark mode toggling and local storage persistence.
 */
(function () {
    const themeKey = 'ai_quiz_theme';
    const currentTheme = localStorage.getItem(themeKey) || 'dark';
    document.documentElement.setAttribute('data-theme', currentTheme);

    window.addEventListener('DOMContentLoaded', () => {
        const themeBtn = document.getElementById('theme-toggle-btn');
        if (themeBtn) {
            updateIcon(currentTheme);
            themeBtn.addEventListener('click', () => {
                const activeTheme = document.documentElement.getAttribute('data-theme');
                const newTheme = activeTheme === 'dark' ? 'light' : 'dark';
                document.documentElement.setAttribute('data-theme', newTheme);
                localStorage.setItem(themeKey, newTheme);
                updateIcon(newTheme);
            });
        }
    });

    function updateIcon(theme) {
        const themeBtn = document.getElementById('theme-toggle-btn');
        if (!themeBtn) return;
        if (theme === 'dark') {
            themeBtn.innerHTML = '<i class="bi bi-sun-fill text-warning fs-5"></i>';
            themeBtn.setAttribute('title', 'Switch to Light Mode');
        } else {
            themeBtn.innerHTML = '<i class="bi bi-moon-stars-fill text-primary fs-5"></i>';
            themeBtn.setAttribute('title', 'Switch to Dark Mode');
        }
    }
})();
