// Settings Data Handler
// Maksimal 50 baris per file

class SettingsDataHandler {
    constructor() {
        this.currentSettings = {};
        this.hasUnsavedChanges = false;
    }

    // Set current settings
    setCurrentSettings(settings) {
        this.currentSettings = settings;
    }

    // Get current settings
    getCurrentSettings() {
        return this.currentSettings;
    }

    // Update current settings by category
    updateCurrentSettings(category, data) {
        switch (category) {
            case 'siteInfoForm':
            case 'businessForm':
                this.currentSettings.general = { ...this.currentSettings.general, ...data };
                break;
            case 'paymentConfigForm':
                this.currentSettings.payment = { ...this.currentSettings.payment, ...data };
                break;
            case 'emailNotificationForm':
            case 'discordNotificationForm':
                this.currentSettings.notification = { ...this.currentSettings.notification, ...data };
                break;
            case 'securityConfigForm':
                this.currentSettings.security = { ...this.currentSettings.security, ...data };
                break;
        }
    }

    // Set unsaved changes flag
    setUnsavedChanges(hasChanges) {
        this.hasUnsavedChanges = hasChanges;
    }

    // Check if has unsaved changes
    getUnsavedChanges() {
        return this.hasUnsavedChanges;
    }

    // Get settings by category
    getSettingsByCategory(category) {
        return this.currentSettings[category] || {};
    }

    // Reset to original settings
    resetSettings() {
        this.hasUnsavedChanges = false;
    }
}

// Export instance
window.settingsDataHandler = new SettingsDataHandler();
