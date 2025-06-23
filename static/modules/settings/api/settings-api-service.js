// Settings API Service
// Maksimal 50 baris per file

class SettingsApiService {
    constructor() {
        this.baseUrl = '/api/v1';
    }

    // Load all settings
    async loadAllSettings() {
        try {
            const response = await apiRequest('/api/v1/admin/settings');
            
            if (response && response.ok) {
                const data = await response.json();
                return data.data || {};
            } else {
                throw new Error(`API Error: ${response.status}`);
            }
        } catch (error) {
            console.error('Error loading settings:', error);
            throw error;
        }
    }

    // Save settings by category
    async saveSettings(category, data) {
        let endpoint = '/settings/general';
        
        switch (category) {
            case 'general':
                endpoint = '/settings/general';
                break;
            case 'payment':
                endpoint = '/settings/payment';
                break;
            case 'notification':
                endpoint = '/settings/notification';
                break;
            case 'security':
                endpoint = '/settings/security';
                break;
            case 'change-password':
                endpoint = '/settings/change-password';
                break;
        }
        
        const response = await apiRequest(endpoint, {
            method: 'PUT',
            body: JSON.stringify(data)
        });
        
        return response;
    }

    // Save all settings at once
    async saveAllSettings(allData) {
        const response = await apiRequest('/settings/bulk', {
            method: 'PUT',
            body: JSON.stringify(allData)
        });
        return response;
    }
}

// Export instance
window.settingsApiService = new SettingsApiService();
