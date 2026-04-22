/**
 * Error Handler with Toast Notifications
 * Provides user-friendly error messages and notifications
 */

class ErrorHandler {
  constructor() {
    this.toastContainer = null;
    this.init();
  }

  /**
   * Initialize toast container
   */
  init() {
    // Create toast container if it doesn't exist
    if (!document.getElementById('toast-container')) {
      this.toastContainer = document.createElement('div');
      this.toastContainer.id = 'toast-container';
      this.toastContainer.className = 'fixed top-4 right-4 z-[9999] space-y-2 max-w-md';
      document.body.appendChild(this.toastContainer);
    } else {
      this.toastContainer = document.getElementById('toast-container');
    }
  }

  /**
   * Show toast notification
   */
  showToast(message, type = 'info', duration = 5000) {
    const toast = document.createElement('div');
    toast.className = this.getToastClasses(type);
    
    const icon = this.getIcon(type);
    
    toast.innerHTML = `
      <div class="flex items-start gap-3">
        <span class="material-symbols-outlined text-xl flex-shrink-0">${icon}</span>
        <div class="flex-1">
          <p class="font-body text-sm">${message}</p>
        </div>
        <button class="toast-close flex-shrink-0 hover:opacity-70 transition-opacity">
          <span class="material-symbols-outlined text-sm">close</span>
        </button>
      </div>
    `;

    // Add to container
    this.toastContainer.appendChild(toast);

    // Animate in
    setTimeout(() => {
      toast.classList.add('toast-show');
    }, 10);

    // Close button
    const closeBtn = toast.querySelector('.toast-close');
    closeBtn.addEventListener('click', () => this.removeToast(toast));

    // Auto remove
    if (duration > 0) {
      setTimeout(() => this.removeToast(toast), duration);
    }

    return toast;
  }

  /**
   * Remove toast
   */
  removeToast(toast) {
    toast.classList.remove('toast-show');
    toast.classList.add('toast-hide');
    
    setTimeout(() => {
      if (toast.parentNode) {
        toast.parentNode.removeChild(toast);
      }
    }, 300);
  }

  /**
   * Get toast classes based on type
   */
  getToastClasses(type) {
    const baseClasses = 'toast-notification backdrop-blur-xl rounded-lg p-4 shadow-2xl border transform transition-all duration-300 opacity-0 translate-x-full';
    
    const typeClasses = {
      success: 'bg-green-500/10 border-green-500/30 text-green-400',
      error: 'bg-red-500/10 border-red-500/30 text-red-400',
      warning: 'bg-yellow-500/10 border-yellow-500/30 text-yellow-400',
      info: 'bg-blue-500/10 border-blue-500/30 text-blue-400',
    };

    return `${baseClasses} ${typeClasses[type] || typeClasses.info}`;
  }

  /**
   * Get icon for toast type
   */
  getIcon(type) {
    const icons = {
      success: 'check_circle',
      error: 'error',
      warning: 'warning',
      info: 'info',
    };

    return icons[type] || icons.info;
  }

  /**
   * Show success message
   */
  success(message, duration) {
    return this.showToast(message, 'success', duration);
  }

  /**
   * Show error message
   */
  error(message, duration) {
    return this.showToast(message, 'error', duration);
  }

  /**
   * Show warning message
   */
  warning(message, duration) {
    return this.showToast(message, 'warning', duration);
  }

  /**
   * Show info message
   */
  info(message, duration) {
    return this.showToast(message, 'info', duration);
  }

  /**
   * Handle API error
   */
  handleAPIError(error) {
    console.error('API Error:', error);
    
    if (error instanceof window.APIError) {
      // Handle authentication errors
      if (error.isAuthError()) {
        this.error('Session expired. Please log in again.');
        setTimeout(() => {
          window.location.href = '/pages/login.html';
        }, 2000);
        return;
      }

      // Handle network errors
      if (error.isNetworkError()) {
        this.error('Unable to connect to server. Please check your connection.');
        return;
      }

      // Show user-friendly message
      this.error(error.getUserMessage());
    } else {
      // Generic error
      this.error('An unexpected error occurred. Please try again.');
    }
  }

  /**
   * Show loading indicator
   */
  showLoading(message = 'Loading...') {
    const loading = document.createElement('div');
    loading.id = 'global-loading';
    loading.className = 'fixed inset-0 z-[9998] bg-black/50 backdrop-blur-sm flex items-center justify-center';
    
    loading.innerHTML = `
      <div class="bg-surface-container rounded-lg p-8 shadow-2xl border border-white/10 flex flex-col items-center gap-4">
        <div class="animate-spin rounded-full h-12 w-12 border-4 border-primary border-t-transparent"></div>
        <p class="font-body text-on-surface">${message}</p>
      </div>
    `;

    document.body.appendChild(loading);
    return loading;
  }

  /**
   * Hide loading indicator
   */
  hideLoading() {
    const loading = document.getElementById('global-loading');
    if (loading) {
      loading.remove();
    }
  }

  /**
   * Show confirmation dialog
   */
  async confirm(message, title = 'Confirm') {
    return new Promise((resolve) => {
      const dialog = document.createElement('div');
      dialog.className = 'fixed inset-0 z-[9999] bg-black/50 backdrop-blur-sm flex items-center justify-center';
      
      dialog.innerHTML = `
        <div class="bg-surface-container rounded-lg p-8 shadow-2xl border border-white/10 max-w-md w-full mx-4">
          <h3 class="font-headline font-bold text-xl text-on-surface mb-4">${title}</h3>
          <p class="font-body text-on-surface-variant mb-6">${message}</p>
          <div class="flex gap-3 justify-end">
            <button class="cancel-btn px-6 py-2 rounded-full bg-surface-container-highest border border-outline-variant/20 hover:bg-surface-bright transition-all font-label text-sm uppercase tracking-widest">
              Cancel
            </button>
            <button class="confirm-btn px-6 py-2 rounded-full bg-gradient-to-r from-primary to-primary-dim text-on-primary font-headline font-bold hover:shadow-lg transition-all">
              Confirm
            </button>
          </div>
        </div>
      `;

      document.body.appendChild(dialog);

      const confirmBtn = dialog.querySelector('.confirm-btn');
      const cancelBtn = dialog.querySelector('.cancel-btn');

      confirmBtn.addEventListener('click', () => {
        dialog.remove();
        resolve(true);
      });

      cancelBtn.addEventListener('click', () => {
        dialog.remove();
        resolve(false);
      });

      // Close on backdrop click
      dialog.addEventListener('click', (e) => {
        if (e.target === dialog) {
          dialog.remove();
          resolve(false);
        }
      });
    });
  }
}

// Add CSS for toast animations
const style = document.createElement('style');
style.textContent = `
  .toast-show {
    opacity: 1 !important;
    transform: translateX(0) !important;
  }
  
  .toast-hide {
    opacity: 0 !important;
    transform: translateX(100%) !important;
  }
`;
document.head.appendChild(style);

// Create singleton instance
const errorHandler = new ErrorHandler();

// Export for use in other modules
window.errorHandler = errorHandler;
