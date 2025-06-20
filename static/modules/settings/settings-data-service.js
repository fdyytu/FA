// Settings Data Service
class SettingsDataService {
    constructor() {
        this.data = {
            generalSettings: {},
            securitySettings: {},
            notificationSettings: {},
            apiSettings: {}
        };
    }

    async loadGeneralSettings() {
        try {
            const response = await apiClient.get('/settings/general');
            
            if (response && response.ok) {
                const data = await response.json();
                this.data.generalSettings = data.data || data;
            } else {
                this.data.generalSettings = this.generateMockGeneralSettings();
            }
            return this.data.generalSettings;
        } catch (error) {
            console.error('Error loading general settings:', error);
            this.data.generalSettings = this.generateMockGeneralSettings();
            return this.data.generalSettings;
        }
    }

    generateMockGeneralSettings() {
        return {
            site_name: 'My Application',
            site_description: 'A modern web application',
            maintenance_mode: false,
            debug_mode: false
        };
    }

    async loadSecuritySettings() {
        try {
            const response = await apiClient.get('/settings/security');
            
            if (response && response.ok) {
                const data = await response.json();
                this.data.securitySettings = data.data || data;
            } else {
                this.data.securitySettings = this.generateMockSecuritySettings();
            }
            return this.data.securitySettings;
        } catch (error) {
            console.error('Error loading security settings:', error);
            this.data.securitySettings = this.generateMockSecuritySettings();
            return this.data.securitySettings;
        }
    }

    generateMockSecuritySettings() {
        return {
            two_factor_auth: true,
            password_expiry: 90,
            max_login_attempts: 5,
            session_timeout: 30
        };
    }

    async saveSettings(category, settings) {
        try {
            const response = await apiClient.put(`/settings/${category}`, settings);
            
            if (response && response.ok) {
                return { success: true, message: 'Settings saved successfully' };
            } else {
                const errorData = await response.json();
                return { success: false, message: errorData.message || 'Failed to save settings' };
            }
        } catch (error) {
            console.error('Error saving settings:', error);
            return { success: false, message: 'Error occurred while saving settings' };
        }
    }
}

const settingsDataService = new SettingsDataService();
