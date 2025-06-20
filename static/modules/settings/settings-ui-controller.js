// Settings UI Controller
class SettingsUIController {
    constructor() {
        this.elements = {};
        this.initElements();
    }

    initElements() {
        this.elements = {
            // General Settings
            siteName: document.getElementById('siteName'),
            siteDescription: document.getElementById('siteDescription'),
            maintenanceMode: document.getElementById('maintenanceMode'),
            debugMode: document.getElementById('debugMode'),
            
            // Security Settings
            twoFactorAuth: document.getElementById('twoFactorAuth'),
            passwordExpiry: document.getElementById('passwordExpiry'),
            maxLoginAttempts: document.getElementById('maxLoginAttempts'),
            sessionTimeout: document.getElementById('sessionTimeout'),
            
            // Buttons
            saveGeneralBtn: document.getElementById('saveGeneralSettings'),
            saveSecurityBtn: document.getElementById('saveSecuritySettings')
        };
    }

    populateGeneralSettings(settings) {
        if (this.elements.siteName) {
            this.elements.siteName.value = settings.site_name || '';
        }
        
        if (this.elements.siteDescription) {
            this.elements.siteDescription.value = settings.site_description || '';
        }
        
        if (this.elements.maintenanceMode) {
            this.elements.maintenanceMode.checked = settings.maintenance_mode || false;
        }
        
        if (this.elements.debugMode) {
            this.elements.debugMode.checked = settings.debug_mode || false;
        }
    }

    populateSecuritySettings(settings) {
        if (this.elements.twoFactorAuth) {
            this.elements.twoFactorAuth.checked = settings.two_factor_auth || false;
        }
        
        if (this.elements.passwordExpiry) {
            this.elements.passwordExpiry.value = settings.password_expiry || 90;
        }
        
        if (this.elements.maxLoginAttempts) {
            this.elements.maxLoginAttempts.value = settings.max_login_attempts || 5;
        }
        
        if (this.elements.sessionTimeout) {
            this.elements.sessionTimeout.value = settings.session_timeout || 30;
        }
    }

    getGeneralSettingsData() {
        return {
            site_name: this.elements.siteName?.value || '',
            site_description: this.elements.siteDescription?.value || '',
            maintenance_mode: this.elements.maintenanceMode?.checked || false,
            debug_mode: this.elements.debugMode?.checked || false
        };
    }

    getSecuritySettingsData() {
        return {
            two_factor_auth: this.elements.twoFactorAuth?.checked || false,
            password_expiry: parseInt(this.elements.passwordExpiry?.value) || 90,
            max_login_attempts: parseInt(this.elements.maxLoginAttempts?.value) || 5,
            session_timeout: parseInt(this.elements.sessionTimeout?.value) || 30
        };
    }
}

const settingsUIController = new SettingsUIController();
