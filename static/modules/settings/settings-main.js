// Settings Main Controller
class SettingsMainController {
    constructor() {
        this.dataService = new SettingsDataService();
        this.uiController = new SettingsUIController();
    }

    async initSettingsDashboard() {
        const token = localStorage.getItem('authToken');
        if (!token) {
            window.location.href = '/login';
            return;
        }

        UIUtils.showLoading(true);
        
        try {
            await Promise.all([
                this.loadGeneralSettings(),
                this.loadSecuritySettings()
            ]);
            
            this.initEventListeners();
            UIUtils.showToast('Dashboard settings berhasil dimuat', 'success', 3000);
        } catch (error) {
            console.error('Error loading settings dashboard:', error);
            UIUtils.showToast('Gagal memuat data settings', 'error');
        } finally {
            UIUtils.showLoading(false);
        }
    }

    async loadGeneralSettings() {
        const settings = await this.dataService.loadGeneralSettings();
        this.uiController.populateGeneralSettings(settings);
    }

    async loadSecuritySettings() {
        const settings = await this.dataService.loadSecuritySettings();
        this.uiController.populateSecuritySettings(settings);
    }

    async saveGeneralSettings() {
        UIUtils.showLoading(true);
        
        try {
            const settingsData = this.uiController.getGeneralSettingsData();
            const result = await this.dataService.saveSettings('general', settingsData);
            
            if (result.success) {
                UIUtils.showToast(result.message, 'success');
            } else {
                UIUtils.showToast(result.message, 'error');
            }
        } catch (error) {
            console.error('Error saving general settings:', error);
            UIUtils.showToast('Terjadi kesalahan saat menyimpan pengaturan', 'error');
        } finally {
            UIUtils.showLoading(false);
        }
    }

    async saveSecuritySettings() {
        UIUtils.showLoading(true);
        
        try {
            const settingsData = this.uiController.getSecuritySettingsData();
            const result = await this.dataService.saveSettings('security', settingsData);
            
            if (result.success) {
                UIUtils.showToast(result.message, 'success');
            } else {
                UIUtils.showToast(result.message, 'error');
            }
        } catch (error) {
            console.error('Error saving security settings:', error);
            UIUtils.showToast('Terjadi kesalahan saat menyimpan pengaturan keamanan', 'error');
        } finally {
            UIUtils.showLoading(false);
        }
    }

    initEventListeners() {
        // General settings save button
        if (this.uiController.elements.saveGeneralBtn) {
            this.uiController.elements.saveGeneralBtn.addEventListener('click', () => {
                this.saveGeneralSettings();
            });
        }

        // Security settings save button
        if (this.uiController.elements.saveSecurityBtn) {
            this.uiController.elements.saveSecurityBtn.addEventListener('click', () => {
                this.saveSecuritySettings();
            });
        }
    }
}

// Global instance
const settingsMainController = new SettingsMainController();
