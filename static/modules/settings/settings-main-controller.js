// Settings Main Controller
// Maksimal 50 baris per file

class SettingsMainController {
    constructor() {
        this.initialized = false;
    }

    // Initialize settings dashboard
    async initSettingsDashboard() {
        const token = checkAuth();
        if (!token) return;

        showLoading(true);
        
        try {
            await this.loadAllSettings();
            this.initEventListeners();
            settingsTabs.initTabNavigation();
            showToast('Dashboard settings berhasil dimuat', 'success', 3000);
            this.initialized = true;
        } catch (error) {
            console.error('Error loading settings dashboard:', error);
            showToast('Gagal memuat data settings', 'error');
        } finally {
            showLoading(false);
        }
    }

    // Load all settings
    async loadAllSettings() {
        try {
            const settings = await settingsApiService.loadAllSettings();
            settingsDataHandler.setCurrentSettings(settings);
            this.populateAllForms();
        } catch (error) {
            console.error('Error loading settings:', error);
            settingsDataHandler.setCurrentSettings({});
            this.populateAllForms();
        }
    }

    // Populate all settings forms
    populateAllForms() {
        const currentSettings = settingsDataHandler.getCurrentSettings();
        
        // General settings
        settingsFormUI.populateForm('siteInfoForm', currentSettings.general || {});
        settingsFormUI.populateForm('businessForm', currentSettings.general || {});
        
        // Payment settings
        settingsFormUI.populatePaymentSettings(currentSettings.payment || {});
        
        // Notification settings
        settingsFormUI.populateForm('emailNotificationForm', currentSettings.notification || {});
        settingsFormUI.populateForm('discordNotificationForm', currentSettings.notification || {});
        
        // Security and API settings
        settingsFormUI.populateForm('securityConfigForm', currentSettings.security || {});
        settingsFormUI.populateApiSettings(currentSettings.api || {});
    }
}

// Export instance
window.settingsMainController = new SettingsMainController();
