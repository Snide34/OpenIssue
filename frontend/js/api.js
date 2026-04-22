/**
 * API Client for OpenIssue Backend
 * Handles all HTTP requests to the FastAPI backend
 */

class APIClient {
  constructor() {
    // Get API URL from environment or use default
    this.baseURL = this.getAPIBaseURL();
    this.token = null;
    this.sessionId = null;
    
    // Load session from localStorage
    this.loadSession();
  }

  /**
   * Get API base URL from environment
   */
  getAPIBaseURL() {
    // Check if running in development
    const isDev = window.location.hostname === 'localhost' || 
                  window.location.hostname === '127.0.0.1';
    
    // Use environment variable or default
    return isDev 
      ? 'http://localhost:8001'
      : (window.ENV?.API_URL || 'http://localhost:8001');
  }

  /**
   * Load session from localStorage
   */
  loadSession() {
    this.sessionId = localStorage.getItem('session_id');
    this.token = localStorage.getItem('auth_token');
  }

  /**
   * Save session to localStorage
   */
  saveSession(sessionId, token) {
    this.sessionId = sessionId;
    this.token = token;
    
    if (sessionId) localStorage.setItem('session_id', sessionId);
    if (token) localStorage.setItem('auth_token', token);
  }

  /**
   * Clear session
   */
  clearSession() {
    this.sessionId = null;
    this.token = null;
    localStorage.removeItem('session_id');
    localStorage.removeItem('auth_token');
  }

  /**
   * Get authentication headers
   */
  getHeaders() {
    const headers = {
      'Content-Type': 'application/json',
    };

    if (this.token) {
      headers['Authorization'] = `Bearer ${this.token}`;
    }

    return headers;
  }

  /**
   * Make HTTP request
   */
  async request(endpoint, options = {}) {
    const url = `${this.baseURL}${endpoint}`;
    
    const config = {
      ...options,
      headers: {
        ...this.getHeaders(),
        ...options.headers,
      },
    };

    try {
      const response = await fetch(url, config);
      
      // Handle non-OK responses
      if (!response.ok) {
        const error = await response.json().catch(() => ({
          detail: `HTTP ${response.status}: ${response.statusText}`
        }));
        throw new APIError(error.detail || 'Request failed', response.status, error);
      }

      // Parse JSON response
      const data = await response.json();
      return data;
      
    } catch (error) {
      if (error instanceof APIError) {
        throw error;
      }
      
      // Network or other errors
      throw new APIError(
        error.message || 'Network error occurred',
        0,
        { originalError: error }
      );
    }
  }

  /**
   * GET request
   */
  async get(endpoint, params = {}) {
    const queryString = new URLSearchParams(params).toString();
    const url = queryString ? `${endpoint}?${queryString}` : endpoint;
    
    return this.request(url, {
      method: 'GET',
    });
  }

  /**
   * POST request
   */
  async post(endpoint, data = {}) {
    return this.request(endpoint, {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }

  /**
   * PUT request
   */
  async put(endpoint, data = {}) {
    return this.request(endpoint, {
      method: 'PUT',
      body: JSON.stringify(data),
    });
  }

  /**
   * DELETE request
   */
  async delete(endpoint) {
    return this.request(endpoint, {
      method: 'DELETE',
    });
  }

  // ==================== AUTH ENDPOINTS ====================

  /**
   * Get GitHub OAuth login URL
   */
  getGitHubLoginURL() {
    return `${this.baseURL}/auth/login`;
  }

  /**
   * Handle OAuth callback
   */
  async handleOAuthCallback(code, state) {
    const data = await this.get('/auth/callback', { code, state });
    
    if (data.session_id) {
      this.saveSession(data.session_id, data.access_token);
    }
    
    return data;
  }

  /**
   * Get current user info
   */
  async getCurrentUser() {
    return this.get('/auth/user');
  }

  /**
   * Logout
   */
  async logout() {
    try {
      await this.post('/auth/logout');
    } finally {
      this.clearSession();
    }
  }

  // ==================== GITHUB ENDPOINTS ====================

  /**
   * Get user's GitHub repositories
   */
  async getRepositories() {
    return this.get('/github/repos');
  }

  /**
   * Get repository details
   */
  async getRepository(owner, repo) {
    return this.get(`/github/repos/${owner}/${repo}`);
  }

  /**
   * Get repository issues
   */
  async getRepositoryIssues(owner, repo, params = {}) {
    return this.get(`/github/repos/${owner}/${repo}/issues`, params);
  }

  // ==================== ISSUE ANALYSIS ENDPOINTS ====================

  /**
   * Analyze an issue
   */
  async analyzeIssue(issueData) {
    return this.post('/issues/analyze', issueData);
  }

  /**
   * Get issue analysis results
   */
  async getIssueAnalysis(issueId) {
    return this.get(`/issues/${issueId}`);
  }

  /**
   * Find duplicate issues
   */
  async findDuplicates(issueId) {
    return this.get(`/issues/${issueId}/duplicates`);
  }

  /**
   * Get suggested labels
   */
  async getSuggestedLabels(issueId) {
    return this.get(`/issues/${issueId}/labels`);
  }

  /**
   * Apply labels to issue
   */
  async applyLabels(issueId, labels) {
    return this.post(`/issues/${issueId}/labels`, { labels });
  }

  /**
   * Get priority classification
   */
  async getPriority(issueId) {
    return this.get(`/issues/${issueId}/priority`);
  }

  // ==================== WEBHOOK ENDPOINTS ====================

  /**
   * Get webhook settings
   */
  async getWebhookSettings(owner, repo) {
    return this.get(`/webhooks/${owner}/${repo}`);
  }

  /**
   * Update webhook settings
   */
  async updateWebhookSettings(owner, repo, settings) {
    return this.put(`/webhooks/${owner}/${repo}`, settings);
  }

  /**
   * Test webhook
   */
  async testWebhook(owner, repo) {
    return this.post(`/webhooks/${owner}/${repo}/test`);
  }

  // ==================== UTILITY METHODS ====================

  /**
   * Check if user is authenticated
   */
  isAuthenticated() {
    return !!this.sessionId || !!this.token;
  }

  /**
   * Health check
   */
  async healthCheck() {
    try {
      const response = await fetch(`${this.baseURL}/health`);
      return response.ok;
    } catch {
      return false;
    }
  }
}

/**
 * Custom API Error class
 */
class APIError extends Error {
  constructor(message, status, data = {}) {
    super(message);
    this.name = 'APIError';
    this.status = status;
    this.data = data;
  }

  /**
   * Check if error is authentication related
   */
  isAuthError() {
    return this.status === 401 || this.status === 403;
  }

  /**
   * Check if error is network related
   */
  isNetworkError() {
    return this.status === 0;
  }

  /**
   * Get user-friendly error message
   */
  getUserMessage() {
    if (this.isNetworkError()) {
      return 'Unable to connect to server. Please check your internet connection.';
    }
    
    if (this.isAuthError()) {
      return 'Authentication failed. Please log in again.';
    }
    
    if (this.status >= 500) {
      return 'Server error occurred. Please try again later.';
    }
    
    return this.message || 'An error occurred. Please try again.';
  }
}

// Create singleton instance
const api = new APIClient();

// Export for use in other modules
window.api = api;
window.APIError = APIError;
