// Theme Management System
class ThemeManager {
    constructor() {
        // Get theme from data-theme attribute on body, then localStorage, then system preference
        const bodyTheme = document.body.getAttribute('data-theme');
        this.theme = bodyTheme || this.getStoredTheme() || this.getSystemTheme();
        this.init();
    }

    // Initialize theme system
    init() {
        // Apply theme immediately to prevent flash of unstyled content
        this.applyTheme(this.theme);

        // Wait for DOM to be ready for interactive elements
        if (document.readyState === 'loading') {
            document.addEventListener('DOMContentLoaded', () => {
                this.createThemeToggle();
                this.setupSystemThemeListener();
            });
        } else {
            this.createThemeToggle();
            this.setupSystemThemeListener();
        }
    }

    // Get stored theme from localStorage
    getStoredTheme() {
        return localStorage.getItem('smartbiller-theme');
    }

    // Store theme preference
    setStoredTheme(theme) {
        localStorage.setItem('smartbiller-theme', theme);
    }

    // Get system theme preference
    getSystemTheme() {
        if (window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches) {
            return 'dark';
        }
        return 'light';
    }

    // Apply theme to document
    applyTheme(theme) {
        document.documentElement.setAttribute('data-theme', theme);
        this.theme = theme;
        this.setStoredTheme(theme);
        this.updateThemeToggleIcon();
    }

    // Toggle between light and dark themes
    toggleTheme() {
        const newTheme = this.theme === 'light' ? 'dark' : 'light';
        this.applyTheme(newTheme);

        // Send theme change to server if user is logged in
        this.syncThemeWithServer(newTheme);
    }

    // Create theme toggle button
    createThemeToggle() {
        // Update existing theme toggle buttons
        const existingToggles = document.querySelectorAll('.theme-toggle');
        existingToggles.forEach(toggle => {
            toggle.innerHTML = this.getThemeIcon(this.theme);
            toggle.onclick = () => this.toggleTheme();
        });
    }

    // Update theme toggle icon
    updateThemeToggleIcon() {
        const toggles = document.querySelectorAll('.theme-toggle');
        toggles.forEach(toggle => {
            toggle.innerHTML = this.getThemeIcon(this.theme);
        });
    }

    // Get appropriate icon for theme
    getThemeIcon(theme) {
        if (theme === 'dark') {
            return '<i class="fas fa-sun"></i>';
        } else {
            return '<i class="fas fa-moon"></i>';
        }
    }

    // Listen for system theme changes
    setupSystemThemeListener() {
        if (window.matchMedia) {
            const mediaQuery = window.matchMedia('(prefers-color-scheme: dark)');
            mediaQuery.addEventListener('change', (e) => {
                // Only auto-switch if user hasn't set a preference
                if (!this.getStoredTheme()) {
                    this.applyTheme(e.matches ? 'dark' : 'light');
                }
            });
        }
    }

    // Sync theme with server
    async syncThemeWithServer(theme) {
        try {
            const response = await fetch('/api/theme', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-Requested-With': 'XMLHttpRequest'
                },
                body: JSON.stringify({ theme: theme })
            });

            if (!response.ok) {
                console.warn('Failed to sync theme with server');
            }
        } catch (error) {
            console.warn('Error syncing theme:', error);
        }
    }

    // Get current theme
    getCurrentTheme() {
        return this.theme;
    }

    // Check if dark mode is active
    isDarkMode() {
        return this.theme === 'dark';
    }

    // Check if light mode is active
    isLightMode() {
        return this.theme === 'light';
    }
}

// Initialize theme manager immediately and when DOM is loaded
function initializeTheme() {
    if (!window.themeManager) {
        window.themeManager = new ThemeManager();
    }
}

// Initialize immediately if DOM is already loaded
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initializeTheme);
} else {
    initializeTheme();
}

// Export for use in other scripts
if (typeof module !== 'undefined' && module.exports) {
    module.exports = ThemeManager;
}

// Theme-aware utility functions
window.ThemeUtils = {
    // Get CSS variable value
    getCSSVariable(name) {
        return getComputedStyle(document.documentElement).getPropertyValue(name);
    },

    // Set CSS variable value
    setCSSVariable(name, value) {
        document.documentElement.style.setProperty(name, value);
    },

    // Check if element is visible in current theme
    isElementVisible(element) {
        const style = getComputedStyle(element);
        return style.display !== 'none' && style.visibility !== 'hidden';
    },

    // Add theme-aware class
    addThemeClass(element, lightClass, darkClass) {
        const theme = window.themeManager?.getCurrentTheme() || 'light';
        if (theme === 'dark') {
            element.classList.add(darkClass);
            element.classList.remove(lightClass);
        } else {
            element.classList.add(lightClass);
            element.classList.remove(darkClass);
        }
    },

    // Create theme-aware element
    createThemeAwareElement(tag, lightClasses, darkClasses) {
        const element = document.createElement(tag);
        this.addThemeClass(element, lightClasses, darkClasses);
        return element;
    }
};

// Auto-initialize theme for dynamically loaded content
const observer = new MutationObserver((mutations) => {
    mutations.forEach((mutation) => {
        if (mutation.type === 'childList') {
            mutation.addedNodes.forEach((node) => {
                if (node.nodeType === Node.ELEMENT_NODE) {
                    // Apply theme to new elements
                    if (window.themeManager) {
                        const theme = window.themeManager.getCurrentTheme();
                        node.setAttribute('data-theme', theme);
                    }
                }
            });
        }
    });
});

// Start observing when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    observer.observe(document.body, {
        childList: true,
        subtree: true
    });
});

// Theme-aware form handling
document.addEventListener('DOMContentLoaded', () => {
    // Enhance form inputs with theme awareness
    const forms = document.querySelectorAll('form');
    forms.forEach(form => {
        const inputs = form.querySelectorAll('input, select, textarea');
        inputs.forEach(input => {
            // Add theme-aware focus styles
            input.addEventListener('focus', () => {
                input.style.borderColor = ThemeUtils.getCSSVariable('--accent-primary');
            });

            input.addEventListener('blur', () => {
                input.style.borderColor = ThemeUtils.getCSSVariable('--input-border');
            });
        });
    });
});

// Theme-aware modal handling
document.addEventListener('DOMContentLoaded', () => {
    // Enhance modals with theme awareness
    const modals = document.querySelectorAll('.modal');
    modals.forEach(modal => {
        modal.addEventListener('show.bs.modal', () => {
            const theme = window.themeManager?.getCurrentTheme() || 'light';
            modal.setAttribute('data-theme', theme);
        });
    });
});

// Performance optimization: Debounce theme changes
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

// Debounced theme sync
const debouncedThemeSync = debounce((theme) => {
    if (window.themeManager) {
        window.themeManager.syncThemeWithServer(theme);
    }
}, 1000);

// Enhanced theme toggle with debouncing
document.addEventListener('click', (e) => {
    if (e.target.closest('.theme-toggle')) {
        const themeManager = window.themeManager;
        if (themeManager) {
            themeManager.toggleTheme();
            debouncedThemeSync(themeManager.getCurrentTheme());
        }
    }
}); 