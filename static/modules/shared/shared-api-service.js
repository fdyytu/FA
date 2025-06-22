// Shared API Service
class SharedAPIService {
    constructor() {
        this.API_BASE_URL = '/api/v1';
    }

    // API helper function
    async apiRequest(endpoint, options = {}) {
        const token = localStorage.getItem('adminToken');
        
        const defaultOptions = {
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${token}`
            }
        };
        
        const mergedOptions = {
            ...defaultOptions,
            ...options,
            headers: {
                ...defaultOptions.headers,
                ...options.headers
            }
        };
        
        try {
            const response = await fetch(`${this.API_BASE_URL}${endpoint}`, mergedOptions);
            
            if (!response.ok) {
                if (response.status === 401) {
                    this.logout();
                    throw new Error('Unauthorized access');
                }
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            
            const data = await response.json();
            
            // Handle API response format consistency
            // If response has success and data properties, return the data
            if (data && typeof data === 'object' && data.hasOwnProperty('success') && data.hasOwnProperty('data')) {
                return data;
            }
            
            return data;
            
        } catch (error) {
            console.error('API request error:', error);
            if (window.SharedUIService) {
                const uiService = new SharedUIService();
                uiService.showToast(`Error: ${error.message}`, 'error');
            }
            throw error;
        }
    }

    // Logout helper
    logout() {
        localStorage.removeItem('adminToken');
        window.location.href = 'login_android.html';
    }
}

// Export for use in other modules
window.SharedAPIService = SharedAPIService;
