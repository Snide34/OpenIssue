/**
 * OpenIssue Accessibility & Theme Management
 * Enhances accessibility and provides theme switching functionality
 */

class AccessibilityManager {
    constructor() {
        this.init();
    }

    init() {
        this.setupKeyboardNavigation();
        this.setupThemeToggle();
        this.setupSkipLinks();
        this.setupFocusManagement();
        this.setupAriaLiveRegions();
        this.setupFormValidation();
        this.setupTooltips();
        this.setupReducedMotion();
    }

    /**
     * Keyboard Navigation Enhancement
     */
    setupKeyboardNavigation() {
        let isKeyboardNav = false;

        // Detect keyboard navigation
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Tab') {
                isKeyboardNav = true;
                document.body.classList.add('keyboard-nav-active');
            }
        });

        document.addEventListener('mousedown', () => {
            isKeyboardNav = false;
            document.body.classList.remove('keyboard-nav-active');
        });

        // Escape key to close modals/dropdowns
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape') {
                this.closeAllOverlays();
            }
        });
    }

    /**
     * Theme Toggle (Dark/Light Mode)
     */
    setupThemeToggle() {
        const savedTheme = localStorage.getItem('theme') || 'dark';
        document.documentElement.setAttribute('data-theme', savedTheme);

        // Create theme toggle button if it doesn't exist
        if (!document.querySelector('.theme-toggle')) {
            const toggle = document.createElement('button');
            toggle.className = 'theme-toggle';
            toggle.setAttribute('aria-label', 'Toggle theme');
            toggle.innerHTML = `
                <span class="material-symbols-outlined">
                    ${savedTheme === 'dark' ? 'light_mode' : 'dark_mode'}
                </span>
            `;
            document.body.appendChild(toggle);

            toggle.addEventListener('click', () => {
                const currentTheme = document.documentElement.getAttribute('data-theme');
                const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
                
                document.documentElement.setAttribute('data-theme', newTheme);
                localStorage.setItem('theme', newTheme);
                
                toggle.innerHTML = `
                    <span class="material-symbols-outlined">
                        ${newTheme === 'dark' ? 'light_mode' : 'dark_mode'}
                    </span>
                `;

                this.announce(`Theme switched to ${newTheme} mode`);
            });
        }
    }

    /**
     * Skip Links for Keyboard Navigation
     */
    setupSkipLinks() {
        if (!document.querySelector('.skip-nav')) {
            const skipLink = document.createElement('a');
            skipLink.href = '#main-content';
            skipLink.className = 'skip-nav';
            skipLink.textContent = 'Skip to main content';
            document.body.insertBefore(skipLink, document.body.firstChild);

            skipLink.addEventListener('click', (e) => {
                e.preventDefault();
                const mainContent = document.getElementById('main-content') || document.querySelector('main');
                if (mainContent) {
                    mainContent.setAttribute('tabindex', '-1');
                    mainContent.focus();
                }
            });
        }
    }

    /**
     * Focus Management for Modals and Overlays
     */
    setupFocusManagement() {
        // Trap focus in modals
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Tab') {
                const modal = document.querySelector('.modal-overlay.active');
                if (modal) {
                    this.trapFocus(modal, e);
                }
            }
        });
    }

    trapFocus(element, event) {
        const focusableElements = element.querySelectorAll(
            'button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])'
        );
        const firstElement = focusableElements[0];
        const lastElement = focusableElements[focusableElements.length - 1];

        if (event.shiftKey && document.activeElement === firstElement) {
            event.preventDefault();
            lastElement.focus();
        } else if (!event.shiftKey && document.activeElement === lastElement) {
            event.preventDefault();
            firstElement.focus();
        }
    }

    /**
     * ARIA Live Regions for Dynamic Content
     */
    setupAriaLiveRegions() {
        if (!document.getElementById('aria-live-polite')) {
            const polite = document.createElement('div');
            polite.id = 'aria-live-polite';
            polite.setAttribute('aria-live', 'polite');
            polite.setAttribute('aria-atomic', 'true');
            polite.className = 'sr-only';
            document.body.appendChild(polite);
        }

        if (!document.getElementById('aria-live-assertive')) {
            const assertive = document.createElement('div');
            assertive.id = 'aria-live-assertive';
            assertive.setAttribute('aria-live', 'assertive');
            assertive.setAttribute('aria-atomic', 'true');
            assertive.className = 'sr-only';
            document.body.appendChild(assertive);
        }
    }

    /**
     * Announce to Screen Readers
     */
    announce(message, priority = 'polite') {
        const region = document.getElementById(`aria-live-${priority}`);
        if (region) {
            region.textContent = '';
            setTimeout(() => {
                region.textContent = message;
            }, 100);
        }
    }

    /**
     * Form Validation with Accessibility
     */
    setupFormValidation() {
        document.addEventListener('submit', (e) => {
            const form = e.target;
            if (form.tagName === 'FORM') {
                const inputs = form.querySelectorAll('input[required], textarea[required], select[required]');
                let isValid = true;

                inputs.forEach(input => {
                    if (!input.value.trim()) {
                        isValid = false;
                        this.showFieldError(input, 'This field is required');
                    } else {
                        this.clearFieldError(input);
                    }
                });

                if (!isValid) {
                    e.preventDefault();
                    this.announce('Form has errors. Please check the fields.', 'assertive');
                }
            }
        });

        // Real-time validation
        document.addEventListener('blur', (e) => {
            const input = e.target;
            if (input.hasAttribute('required') && !input.value.trim()) {
                this.showFieldError(input, 'This field is required');
            } else if (input.type === 'email' && input.value && !this.isValidEmail(input.value)) {
                this.showFieldError(input, 'Please enter a valid email address');
            } else {
                this.clearFieldError(input);
            }
        }, true);
    }

    showFieldError(input, message) {
        input.classList.add('invalid');
        input.classList.remove('valid');
        input.setAttribute('aria-invalid', 'true');

        let errorElement = input.parentElement.querySelector('.form-error');
        if (!errorElement) {
            errorElement = document.createElement('div');
            errorElement.className = 'form-error';
            errorElement.setAttribute('role', 'alert');
            input.parentElement.appendChild(errorElement);
        }

        errorElement.innerHTML = `
            <span class="material-symbols-outlined" style="font-size: 1rem;">error</span>
            ${message}
        `;

        // Shake animation
        input.classList.add('shake-error');
        setTimeout(() => input.classList.remove('shake-error'), 500);
    }

    clearFieldError(input) {
        input.classList.remove('invalid');
        input.classList.add('valid');
        input.setAttribute('aria-invalid', 'false');

        const errorElement = input.parentElement.querySelector('.form-error');
        if (errorElement) {
            errorElement.remove();
        }
    }

    isValidEmail(email) {
        return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email);
    }

    /**
     * Accessible Tooltips
     */
    setupTooltips() {
        document.querySelectorAll('[data-tooltip]').forEach(element => {
            element.setAttribute('aria-label', element.getAttribute('data-tooltip'));
        });
    }

    /**
     * Respect Reduced Motion Preference
     */
    setupReducedMotion() {
        const prefersReducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)');
        
        if (prefersReducedMotion.matches) {
            document.body.classList.add('reduced-motion');
        }

        prefersReducedMotion.addEventListener('change', (e) => {
            if (e.matches) {
                document.body.classList.add('reduced-motion');
            } else {
                document.body.classList.remove('reduced-motion');
            }
        });
    }

    /**
     * Close All Overlays (Modals, Dropdowns, etc.)
     */
    closeAllOverlays() {
        // Close modals
        document.querySelectorAll('.modal-overlay.active').forEach(modal => {
            modal.classList.remove('active');
            this.announce('Modal closed');
        });

        // Close dropdowns
        document.querySelectorAll('.dropdown.active').forEach(dropdown => {
            dropdown.classList.remove('active');
        });

        // Close mobile drawer
        const drawer = document.querySelector('.mobile-drawer.active');
        if (drawer) {
            drawer.classList.remove('active');
            document.querySelector('.mobile-drawer-overlay')?.classList.remove('active');
        }
    }
}

/**
 * Toast Notification System with Accessibility
 */
class ToastManager {
    constructor() {
        this.container = this.createContainer();
    }

    createContainer() {
        let container = document.querySelector('.toast-container');
        if (!container) {
            container = document.createElement('div');
            container.className = 'toast-container';
            container.setAttribute('aria-live', 'polite');
            container.setAttribute('aria-atomic', 'false');
            document.body.appendChild(container);
        }
        return container;
    }

    show(message, type = 'info', duration = 5000) {
        const toast = document.createElement('div');
        toast.className = `toast ${type}`;
        toast.setAttribute('role', 'alert');
        
        const icons = {
            success: 'check_circle',
            error: 'error',
            warning: 'warning',
            info: 'info'
        };

        toast.innerHTML = `
            <div class="toast-icon">
                <span class="material-symbols-outlined">${icons[type]}</span>
            </div>
            <div class="toast-content">
                <div class="toast-title">${this.getTitle(type)}</div>
                <div class="toast-message">${message}</div>
            </div>
            <button class="toast-close" aria-label="Close notification">
                <span class="material-symbols-outlined">close</span>
            </button>
        `;

        this.container.appendChild(toast);

        // Close button
        toast.querySelector('.toast-close').addEventListener('click', () => {
            this.remove(toast);
        });

        // Auto remove
        if (duration > 0) {
            setTimeout(() => this.remove(toast), duration);
        }

        return toast;
    }

    remove(toast) {
        toast.classList.add('exiting');
        setTimeout(() => {
            toast.remove();
        }, 300);
    }

    getTitle(type) {
        const titles = {
            success: 'Success',
            error: 'Error',
            warning: 'Warning',
            info: 'Information'
        };
        return titles[type] || 'Notification';
    }
}

/**
 * Modal Manager with Accessibility
 */
class ModalManager {
    constructor() {
        this.activeModal = null;
        this.previousFocus = null;
    }

    open(modalId) {
        const modal = document.getElementById(modalId);
        if (!modal) return;

        this.previousFocus = document.activeElement;
        this.activeModal = modal;

        modal.classList.add('active');
        modal.setAttribute('aria-hidden', 'false');

        // Focus first focusable element
        const firstFocusable = modal.querySelector('button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])');
        if (firstFocusable) {
            setTimeout(() => firstFocusable.focus(), 100);
        }

        // Prevent body scroll
        document.body.style.overflow = 'hidden';

        window.accessibilityManager?.announce('Modal opened');
    }

    close(modalId) {
        const modal = document.getElementById(modalId);
        if (!modal) return;

        modal.classList.remove('active');
        modal.setAttribute('aria-hidden', 'true');

        // Restore focus
        if (this.previousFocus) {
            this.previousFocus.focus();
        }

        // Restore body scroll
        document.body.style.overflow = '';

        this.activeModal = null;

        window.accessibilityManager?.announce('Modal closed');
    }
}

// Initialize on DOM ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => {
        window.accessibilityManager = new AccessibilityManager();
        window.toastManager = new ToastManager();
        window.modalManager = new ModalManager();
    });
} else {
    window.accessibilityManager = new AccessibilityManager();
    window.toastManager = new ToastManager();
    window.modalManager = new ModalManager();
}

// Export for module usage
if (typeof module !== 'undefined' && module.exports) {
    module.exports = { AccessibilityManager, ToastManager, ModalManager };
}
