// API Client utilities
class ApiClient {
    constructor(baseUrl = 'api/v1/') {
        this.baseUrl = baseUrl;
    }

    async request(endpoint, options = {}) {
        const token = localStorage.getItem('adminToken');
        const defaultHeaders = {
            'Content-Type': 'application/json',
            ...(token && { 'Authorization': `Bearer ${token}` })
        };

        const config = {
            headers: { ...defaultHeaders, ...options.headers },
            ...options
        };

        try {
            const response = await fetch(`${this.baseUrl}${endpoint}`, config);
            return response;
        } catch (error) {
            console.error('API request failed:', error);
            throw error;
        }
    }

    async get(endpoint) {
        return this.request(endpoint, { method: 'GET' });
    }

    async post(endpoint, data) {
        return this.request(endpoint, {
            method: 'POST',
            body: JSON.stringify(data)
        });
    }

    async put(endpoint, data) {
        return this.request(endpoint, {
            method: 'PUT',
            body: JSON.stringify(data)
        });
    }

    async delete(endpoint) {
        return this.request(endpoint, { method: 'DELETE' });
    }
}

// Global API client instance
const apiClient = new ApiClient('/api/v1');

// Legacy compatibility function with response format handling
async function apiRequest(endpoint, options = {}) {
    try {
        const response = await apiClient.request(endpoint, options);
        
        if (!response.ok) {
            if (response.status === 401) {
                localStorage.removeItem('adminToken');
                window.location.href = 'login_android.html';
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
        throw error;
    }
}
